import pandas as pd
import logging
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Documento, Egresado, EgresadoDocumento, Etapa
from .auth import is_egresado, is_servicions_escolares
from django.db import IntegrityError, transaction

# -------------------------------------------------------------------------
# FUNCIONES DE LOGIN Y AUTENTICACIÓN
# -------------------------------------------------------------------------

# Maneja el login para servicios escolares
def handle_servicios_escolares_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.groups.filter(name='servicios_escolares').exists():
            auth_login(request, user)
            messages.success(request, 'Bienvenido al sistema de Servicios Escolares.')
            return redirect('servicios_escolares')
        else:
            messages.error(request, 'Acceso no permitido.')
    else:
        messages.error(request, 'Usuario no válido.')
    return None

# Maneja el login para egresados
def handle_egresados_login(request):
    correo = request.POST.get('correo')
    curp = request.POST.get('curp')
    user = authenticate(request, email=correo, curp=curp)
    if user is not None:
        if user.groups.filter(name='egresados').exists():
            auth_login(request, user)
            return redirect('egresado')
        else:
            messages.error(request, 'Acceso no permitido.')
    else:
        messages.error(request, 'Usuario no válido.')
    return None

def handle_crear_egresado(request):
    """
    Maneja la creación de cuenta para egresados, asegurando que todas las operaciones 
    de base de datos se ejecuten de forma atómica (Todo o Nada).
    """
    if request.method != 'POST':
        return redirect('login')

    correo = request.POST.get('correo')
    curp = request.POST.get('curp')
    archivo = request.FILES.get('id')
    
    # --- 1. Validaciones Preliminares (Fuera de la transacción) ---
    
    # Verifica si el CURP no existe en la tabla de Egresados (Fuente de verdad inicial)
    if not Egresado.objects.filter(curp=curp).exists():
        messages.error(request, 'Error: No se encontró un egresado con el CURP proporcionado.')
        return redirect('login')
    
    # Verifica que el CURP y correo no estén ya registrados como Usuarios
    if User.objects.filter(username=curp).exists():
        messages.error(request, 'Error: El CURP ya está registrado en el sistema.')
        return redirect('login')
    if User.objects.filter(email=correo).exists():
        messages.error(request, 'Error: El correo electrónico ya está registrado en el sistema.')
        return redirect('login')

    # --- 2. Bloque Atómico de Operaciones de Base de Datos ---
    try:
        with transaction.atomic():
            # Obtiene las instancias de modelos necesarias (pueden fallar con DoesNotExist)
            egresado = Egresado.objects.get(curp=curp)
            group = Group.objects.get(name='egresados')
            etapa = Etapa.objects.get(nombre='identificacion_se')
            documento = Documento.objects.get(clave='id')

            # a) Crea el Usuario
            user = User.objects.create_user(username=curp, email=correo)
            user.set_unusable_password()
            user.groups.add(group)
            # Nota: user.save() y user.groups.add(group) son parte del atomic()

            # b) Guarda el documento de identificación
            EgresadoDocumento.objects.create(
                egresado=egresado,
                documento=documento,
                archivo=archivo
            )
            
            # c) Actualiza y guarda la instancia de Egresado
            egresado.usuario = user
            egresado.etapa = etapa
            egresado.save()
            
            # d) Autentica y loguea al usuario (Operación no-DB, pero crítica)
            user_auth = authenticate(request, username=curp) # Usamos CURP/username para autenticar
            
            if user_auth is None:
                 # Forzar ROLLBACK si la autenticación falla por algún error inesperado.
                raise Exception("Fallo la autenticación del nuevo usuario.")

            auth_login(request, user_auth)
            
            # COMMIT implícito si el bloque 'with' termina sin errores
            messages.success(request, 'Usuario y cuenta creados correctamente.')
            return redirect('egresado')
    
    # --- 3. Manejo de Excepciones ---
    except (Group.DoesNotExist, Etapa.DoesNotExist, Documento.DoesNotExist) as e:
        # Captura errores de objetos que faltan en la DB (ej. si el grupo 'egresados' no existe)
        error_msg = f"Error de configuración del sistema: No se encontró un objeto necesario. Detalles: {e}"
        messages.error(request, error_msg)
        return redirect('login')
        
    except Exception as e:
        # Captura cualquier otro error, incluyendo fallos en la DB o el 'raise Exception'
        # ¡El ROLLBACK ya ha sido ejecutado por transaction.atomic()!
        print(f"Error fatal durante la transacción: {e}")
        messages.error(request, 'Error inesperado al crear la cuenta. Se han revertido todos los cambios.')
        return redirect('login')


# Vista para iniciar sesión y manejar los diferentes tipos de login
@csrf_protect
def login(request):
    """
    Vista para autenticar usuarios de Servicios Escolares, Egresados y crear una cuenta de egresado.
    Permite el acceso según el tipo de usuario y sus credenciales.
    """
    if request.method == 'GET':
        return render(request, 'titulacion/login.html')
    
    # Determina qué formulario fue enviado
    form_type = request.POST.get('form_type')

    # Login como servicios_escolares
    if form_type == 'servicios_escolares':
        result = handle_servicios_escolares_login(request)
        if result: return result
    # Login como egresados
    elif form_type == 'egresados':
        result = handle_egresados_login(request)
        if result: return result
    # Crear cuenta de egresado
    elif form_type == 'crear_egresado':
        result = handle_crear_egresado(request)     
        if result: return result
    else:
        messages.error(request, 'Usuario o contraseña incorrectos.')

    return

# -------------------------------------------------------------------------
# VISTAS DE EGRESADO
# -------------------------------------------------------------------------

# Dashboard para egresados, permite ver y subir documentos
@user_passes_test(is_egresado)
def egresado(request):
    egresado = Egresado.objects.get(usuario=request.user)
    
    if request.method == 'GET':
        etapa = egresado.etapa.nombre

        # Obtiene todos los documentos requeridos y los documentos ya subidos por el egresado
        documentos_requeridos = Documento.objects.all()
        documentos = EgresadoDocumento.objects.filter(egresado=egresado)

        documentos_dict = {}

        # Para cada documento requerido, busca el documento más reciente subido por el egresado
        for documento_requerido in documentos_requeridos:
            documento = documentos.filter(
                documento=documento_requerido
                ).order_by('-fecha_asignacion').first()
            
            documentos_dict[documento_requerido] = documento

        context = {
            'egresado':egresado,
            'etapa': etapa,
            'docs': documentos_dict
        }

        return render(request, 'titulacion/egresado/egresado.html', context=context)
    
    # Guardar archivos enviados en el formulario
    s= ''
    for clave, archivo in request.FILES.items():
        s+= f'{clave}: {archivo.name}\n'
        # Busca el Documento correspondiente por clave
        documento = Documento.objects.get(clave=clave)
        # Crea el registro del documento subido
        EgresadoDocumento.objects.create(
            egresado=egresado,
            documento=documento,
            archivo=archivo
        )

    egresado.avanzar_etapa()

    messages.success(request, 'Documentos enviados excitosamente + ' + s)
    return redirect('egresado')

@user_passes_test(is_egresado)
def perfil(request):
    egresado = Egresado.objects.get(usuario=request.user)
    return render(request, 'titulacion/egresado/perfil.html', {'egresado': egresado})


# -------------------------------------------------------------------------
# VISTAS DE SERVICIOS ESCOLARES
# -------------------------------------------------------------------------

@user_passes_test(is_servicions_escolares)
def servicios_escolares(request):
    if request.method == 'GET':
        # Configuration
        # IMPORTANTE: Estos nombres (keys) deben coincidir EXACTAMENTE con los nombres de Etapa en el Admin
        etapa_docs = {
            'identificacion_se': ['id'],
            'revision_se': [
                'e_firma',
                'beca',
                'impresion',
                'practicas',
                'ingles',
                'p_titulacion',
                's_social',
                'licenciatura',
                'bachillerato',
                'curp',
                'acta'
            ],
            'segunda_revision_se': [
                'e_firma',
                'beca',
                'impresion',
                'practicas',
                'ingles',
                'p_titulacion',
                's_social',
                'licenciatura',
                'bachillerato',
                'curp',
                'acta'
            ],
            'activar_linea_pago_se': [

            ],
            'lineas_pago_se': [
                'linea_1',
                'linea_2',
            ],
        }
        
        # Get documents
        all_doc_claves = sum(etapa_docs.values(), [])  # Flatten list
        documentos = {doc.clave: doc for doc in Documento.objects.filter(clave__in=all_doc_claves)}
        
        # Get egresados
        # Traemos todos los que tienen etapa asignada
        egresados = Egresado.objects.select_related('etapa').filter(etapa__isnull=False)
        
        # Build results
        results = {
            etapa: {
                egresado: {
                    clave: EgresadoDocumento.objects.filter(
                        egresado=egresado, documento=documentos[clave]
                    ).order_by('-fecha_asignacion').first()
                    for clave in doc_claves
                }
                for egresado in egresados 
                # AQUÍ es donde compara el nombre de la etapa de la BD con el nombre del diccionario
                if egresado.etapa and egresado.etapa.nombre == etapa
            }
            for etapa, doc_claves in etapa_docs.items()
        }
        
        context = {
            'egresados': egresados,
            'etapa_id': results.get('identificacion_se', {}),
            'etapa_revision': results.get('revision_se', {}),
            'etapa_segunda_revision': results.get('segunda_revision_se', {}),
            'etapa_activar_linea_pago': results.get('activar_linea_pago_se', {}),
            'etapa_lineas_pago': results.get('lineas_pago_se', {})
        }

        return render(request, 'titulacion/servicios_escolares/servicios_escolares.html', context)
    
    if request.POST.get('accion') == 'activar_pago_masivo':
        # Recibimos la lista de matrículas seleccionadas en los checkboxes
        lista_matriculas = request.POST.getlist('egresados_seleccionados')
        count = 0
        
        for matricula in lista_matriculas:
            try:
                egresado = Egresado.objects.get(numero_control=matricula)
                # Avanzamos al egresado a la siguiente etapa
                egresado.avanzar_etapa()
                count += 1
            except Egresado.DoesNotExist:
                continue
        
        if count > 0:
            messages.success(request, f'Se activó la línea de pago para {count} egresados exitosamente.')
        else:
            messages.warning(request, 'No seleccionaste ningún egresado.')
            
        return redirect('servicios_escolares')
    
    # ---------------- Lógica POST (Procesar documentos) ----------------
    egresado_numero_control = request.POST.get('numero_control')
    egresado = Egresado.objects.get(numero_control=egresado_numero_control)

    avanzar_etapa = True


    # Manejar inputs de estado (aceptar/rechazar)
    for key, value in request.POST.items():
            if key.startswith('estado_'):
                documento_id = key.split('_')[1]  # Extract documento ID
                estado = value

                if estado == 'rechazado':
                    avanzar_etapa = False
                
                try:
                    documento = EgresadoDocumento.objects.get(pk=documento_id)
                    documento.estado = estado
                    
                    # Get corresponding notas
                    notas_key = f'notas_{documento_id}'
                    notas_seleccionadas = request.POST.getlist(notas_key)
                    documento.notas = ', '.join(notas_seleccionadas) if notas_seleccionadas else ''
                    
                    documento.save()

                except Documento.DoesNotExist:
                    continue

    # Manejar subida de archivos por parte de servicios escolares (si aplica)
    for key, archivo in request.FILES.items():
        if key.startswith('subir_'):
            clave = key[len('subir_'):]
            try:
                documento = Documento.objects.get(clave=clave)
                doc = EgresadoDocumento.objects.create(
                    egresado=egresado,
                    documento=documento,
                    archivo=archivo
                )
                doc.estado = 'aceptado'
                doc.save()
            except Documento.DoesNotExist:
                pass

    if avanzar_etapa:
        egresado.avanzar_etapa()
    else:
        # Lógica de retroceso
        egresado.retroceder_etapa()
        if egresado.etapa and egresado.etapa.nombre == 'revision_se':
            egresado.retroceder_etapa()
            
    messages.success(request, f'documentos de {egresado.nombre} actualizados.')
    return redirect('servicios_escolares')

# -------------------------------------------------------------------------
# IMPORTAR EXCEL (CORREGIDO)
# -------------------------------------------------------------------------
@user_passes_test(is_servicions_escolares)
def importar_egresados(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        excel_file = request.FILES['archivo_excel']
        
        try:
            # 1. Leer el archivo con Pandas
            df = pd.read_excel(excel_file)
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip().str.lower()
            
            cont_creados = 0
            cont_actualizados = 0
            
            # Buscar la etapa con orden 1
            # primera_etapa = Etapa.objects.filter(orden=1).first()

            # 2. Iterar sobre el Excel
            for index, row in df.iterrows():
                num_control = str(row.get('numero_control', '')).strip()
                curp = str(row.get('curp', '')).strip()
                
                if not num_control or not curp or num_control == 'nan':
                    continue 
                
                nombre = str(row.get('nombre', '')).strip()
                p_apellido = str(row.get('primer_apellido', '')).strip()
                s_apellido = str(row.get('segundo_apellido', '')).strip()
                if s_apellido == 'nan': s_apellido = ''
                
                genero = str(row.get('genero', 'M')).strip().upper()

                # 3. Usuario
                user, created_user = User.objects.get_or_create(username=num_control)
                if created_user:
                    user.set_password(num_control)
                    user.first_name = nombre
                    user.last_name = f"{p_apellido} {s_apellido}"
                    user.save()

                # 4. Egresado
                egresado, created_egresado = Egresado.objects.update_or_create(
                    numero_control=num_control,
                    defaults={
                        'curp': curp,
                        'nombre': nombre,
                        'primer_apellido': p_apellido,
                        'segundo_apellido': s_apellido,
                        'genero': genero,
                        'usuario': user,
                    }
                )
                
                # --- CORRECCIÓN: Asigna etapa si es nuevo O si no tiene etapa ---
                if primera_etapa and (created_egresado or egresado.etapa is None):
                    egresado.etapa = primera_etapa
                    egresado.save()

                if created_egresado:
                    cont_creados += 1
                else:
                    cont_actualizados += 1

            messages.success(request, f'Carga exitosa: {cont_creados} nuevos, {cont_actualizados} actualizados.')

        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {e}')
            print(f"Error detallado: {e}")
            
    return redirect('servicios_escolares')