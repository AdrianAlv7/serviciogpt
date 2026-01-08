import os
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Modelo para etapas del proceso de titulación
class Etapa(models.Model):
    orden = models.IntegerField()
    nombre = models.CharField(max_length=100)
    titulo = models.CharField(max_length=200, null=True, blank=True)
    descripcion = models.CharField(max_length=500)

    def __str__(self):
        return f'{self.nombre}'
    
# Modelo principal de egresados
class Egresado(models.Model):   
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)  # Relación con usuario
    etapa = models.ForeignKey(Etapa, null=True, blank=True, on_delete=models.SET_NULL)  # Etapa actual del egresado
    curp = models.CharField('CURP', max_length=18, unique=True, primary_key=True)  # CURP como identificador único
    numero_control = models.CharField('Número de control', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=100)
    primer_apellido = models.CharField('Primer apellido', max_length=100)
    segundo_apellido = models.CharField('Segundo apellido', max_length=100, blank=True, null=True)
    
    genero = models.CharField(
        'Género',
        max_length=1,
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ]
    )

    ano_de_egreso = models.IntegerField(
        verbose_name='Año de Egreso',
        help_text='Año en que finalizó los estudios (ej: 2024)',
        blank=True, null=True
    )

    periodo_escolar_de_egreso = models.CharField(
        'Período de Egreso',
        max_length=1,
        choices=[
            ('1', 'Enero - Junio'),
            ('2', 'Agosto - Diciembre'),
        ],
        blank=True, null=True
    )

    grupo_plan = models.ForeignKey('GrupoPlan', on_delete=models.SET_NULL, null=True, blank=True)
    opcion_titulacion = models.ForeignKey('OpcionTitulacion', on_delete=models.SET_NULL, null=True, blank=True)

    

    
    
    class Meta:
        verbose_name = 'Egresado'
        verbose_name_plural = 'Egresados'
        ordering = ['primer_apellido', 'segundo_apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido or ''}".strip()
    
    def nombre_completo(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido or ''}".strip()
    
    def save(self, *args, **kwargs):
        """Crea la carpeta del egresado automáticamente al guardar"""
        super().save(*args, **kwargs)
        self.crear_carpeta_documentos()
    
    def crear_carpeta_documentos(self):
        """Crea la carpeta para documentos del egresado si no existe"""
        carpeta_path = os.path.join(settings.MEDIA_ROOT, 'documentos', self.numero_control)
        
        if not os.path.exists(carpeta_path):
            try:
                os.makedirs(carpeta_path, exist_ok=True)
                print(f"Carpeta creada para egresado {self.numero_control}: {carpeta_path}")
            except OSError as e:
                print(f"Error al crear carpeta para {self.numero_control}: {e}")

    def avanzar_etapa(self):
        if self.etapa:
            siguiente_etapa_orden = self.etapa.orden + 1
        else:
            siguiente_etapa_orden = 1
        
        try:
            siguiente_etapa = Etapa.objects.get(orden=siguiente_etapa_orden)
            self.etapa = siguiente_etapa

            self.save()

        except Etapa.DoesNotExist:
            pass

    def retroceder_etapa(self):
        if self.etapa:
            etapa_anterior_orden = self.etapa.orden - 1

            if etapa_anterior_orden >= 1:
                etapa_anterior = Etapa.objects.get(orden=etapa_anterior_orden)
                self.etapa = etapa_anterior
            else:
                # Elimina el usuario de la base de datos si existe
                if self.usuario:
                    self.usuario.delete()
                self.usuario = None
                self.etapa = None
            
            self.save()

# Modelo para tipos de documentos requeridos
class Documento(models.Model):
    clave = models.CharField(max_length=50)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    extensiones_aceptados = models.CharField(
        max_length=200,
        help_text="Extensiones permitidas separadas por comas (ej: pdf,doc,docx,jpg,png)",
        default="pdf"
    )

    def __str__(self):
        return self.titulo
    
    def get_lista_extensiones(self):
        """Devuelve una lista de extensiones aceptadas"""
        return [tipo.strip().lower() for tipo in self.extensiones_aceptados.split(',')]

# Función para definir la ruta de guardado de archivos de egresados
def upload_path_egresado_documento(instance, filename):
    """
    Ruta: documentos/{numero_control}/{numero_control}-{nombre_documento}-{fecha_hora}.{extension}
    """
    _, extension = os.path.splitext(filename)
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"{instance.egresado.numero_control}-{instance.documento.clave}-{timestamp}{extension}"
    return f"documentos/{instance.egresado.numero_control}/{nombre_archivo}"

# Modelo que relaciona egresados con documentos y almacena el archivo
class EgresadoDocumento(models.Model):
    egresado = models.ForeignKey(Egresado, on_delete=models.CASCADE)  # Relación con egresado
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)  # Tipo de documento
    archivo = models.FileField(
        upload_to=upload_path_egresado_documento,
        help_text="El archivo se guardará automáticamente en la carpeta del egresado",
        blank=False, null=False
    )

    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('revisado', 'Revisado'),
            ('aceptado', 'Aceptado'),
            ('rechazado', 'Rechazado'),
        ],
        default='pendiente'
    )
    notas = models.TextField(blank=True)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Documento de Egresado'
        verbose_name_plural = 'Documentos de Egresados'

    def __str__(self):
        return f"{self.egresado} - {self.documento}"
    
    def save(self, *args, **kwargs):
        """Asegura que la carpeta del egresado exista antes de guardar el archivo"""
        if self.egresado:
            self.egresado.crear_carpeta_documentos()
        super().save(*args, **kwargs)
    
    def get_nombre_archivo_completo(self):
        """Devuelve el nombre del archivo guardado"""
        if self.archivo:
            return os.path.basename(self.archivo.name)
        return None
    
    def get_ruta_carpeta(self):
        """Devuelve la ruta de la carpeta del egresado"""
        return f"documentos/{self.egresado.numero_control}/"


class GrupoPlan(models.Model):
    """
    Representa los grupos de planes.
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=500, null=True, blank=True) 

    class Meta:
        verbose_name_plural = "Grupo de Planes de Titulacion"

    def __str__(self):
        return self.nombre

class Plan(models.Model):
    """
    Representa los planes de estudio o carreras que ofrece la institución.
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    grupo = models.ForeignKey(GrupoPlan, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Planes de Titulacion"

    def __str__(self):
        return self.nombre
    

class OpcionTitulacion(models.Model):
    """
    Representa las diferentes formas en que un estudiante puede titularse
    (tesis, examen profesional, proyecto terminal, servicio social, etc.)
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Opciones de Titulacion"

    def __str__(self):
        return self.nombre