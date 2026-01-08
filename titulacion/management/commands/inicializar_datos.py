from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User, Permission
from titulacion.models import Documento, Etapa
from titulacion.models import Egresado
from django.db import transaction

class Command(BaseCommand):
    help = 'Crea datos, grupos y usuarios iniciales para titulacion'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos iniciales...')

        with transaction.atomic():
            self.crear_grupos()

            self.crear_usuarios()

            self.crear_egresados()
            
            self.crear_documentos()

            self.crear_etapas()

        
        self.stdout.write(
            self.style.SUCCESS('Los datos se crearon correctamente!')
        )
        
    def crear_grupos(self):
        grupos = [
            {
                'name': 'servicios_escolares',
                'permisions': [
                    'view_etapa', 'view_egresadodocumento', 
                    'view_egresado', 'change_egresado', 'view_documento'
                ]
            },
            {
                'name': 'egresados',
                'permisions': []
            }
        ]

        for datos in grupos:
            grupo, created = Group.objects.get_or_create(name=datos['name'])

            if created:
                self.stdout.write(f'Grupo creado: {datos["name"]}')
            else:
                self.stdout.write(f'Grupo ya existente: {datos["name"]}')

            for codename in datos['permisions']:
                try:
                    permision = Permission.objects.get(codename=codename)
                    grupo.permissions.add(permision)

                    self.stdout.write(f'Permiso {codename} añadido a {datos["name"]}')
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Permiso {datos["name"]} no existe')
                    )


    def crear_usuarios(self):
        usuarios = [
            {
                'username': 'se1',
                'email': 'se1@gmail.com',
                'first_name': 'Servicios',
                'last_name': 'Escolares',
                'groups': ['servicios_escolares'],
                'is_staff': True,
                'is_superuser': False,
            },
        ]

        for datos in usuarios:
            user, created = User.objects.get_or_create(
                username=datos['username'],
                defaults={
                    'email': datos['email'],
                    'first_name': datos['first_name'],
                    'last_name': datos['last_name'],
                    'is_staff': datos.get('is_staff', False),
                    'is_superuser': datos.get('is_superuser', False),
                }
            )

            if created:
                user.set_password('user4life') # Default Password
                user.save()
                self.stdout.write(f'Usuario creado: {user.username}')

                for nombre_grupo in datos['groups']:
                    grupo = Group.objects.get(name=nombre_grupo)
                    user.groups.add(grupo)
                    self.stdout.write(f'Se añadio {user.username} a {nombre_grupo}')

    def crear_egresados(self):
        egresados = [
            {
                'numero_control': '22490001',
                'curp': '1',
                'nombre': 'Juan',
                'primer_apellido': 'Pérez',
                'segundo_apellido': 'García',
                'genero': 'M',
            },
            {
                'numero_control': '22490002',
                'curp': '2',
                'nombre': 'María',
                'primer_apellido': 'López',
                'segundo_apellido': 'Martínez',
                'genero': 'F',
            },
            {
                'numero_control': '22490003',
                'curp': '3',
                'nombre': 'Carlos',
                'primer_apellido': 'Ramírez',
                'segundo_apellido': 'Sánchez',
                'genero': 'M',
            },
            {
                'numero_control': '22490004',
                'curp': '4',
                'nombre': 'Ana',
                'primer_apellido': 'Hernández',
                'segundo_apellido': 'Díaz',
                'genero': 'F',
            },
            {
                'numero_control': '22490005',
                'curp': '5',
                'nombre': 'Luis',
                'primer_apellido': 'Torres',
                'segundo_apellido': 'Vargas',
                'genero': 'M',
            },
            {
                'numero_control': '22490006',
                'curp': '6',
                'nombre': 'Sofía',
                'primer_apellido': 'Mendoza',
                'segundo_apellido': 'Reyes',
                'genero': 'F',
            },
            {
                'numero_control': '22490007',
                'curp': '7',
                'nombre': 'Miguel',
                'primer_apellido': 'Castro',
                'segundo_apellido': 'Ortega',
                'genero': 'M',
            },
            {
                'numero_control': '22490008',
                'curp': '8',
                'nombre': 'Valeria',
                'primer_apellido': 'Jiménez',
                'segundo_apellido': 'Flores',
                'genero': 'F',
            },
            {
                'numero_control': '22490009',
                'curp': '9',
                'nombre': 'Diego',
                'primer_apellido': 'Ríos',
                'segundo_apellido': 'Morales',
                'genero': 'M',
            },
            {
                'numero_control': '22490010',
                'curp': '10',
                'nombre': 'Paula',
                'primer_apellido': 'Navarro',
                'segundo_apellido': 'Silva',
                'genero': 'F',
            },
        ]

        for datos in egresados:
            egresado, created = Egresado.objects.get_or_create(
                numero_control=datos['numero_control'],
                defaults={
                    'curp': datos['curp'],
                    'nombre': datos['nombre'],
                    'primer_apellido': datos['primer_apellido'],
                    'segundo_apellido': datos['segundo_apellido'],
                    'genero': datos['genero'],
                }
            )
            if created:
                self.stdout.write(f'Egresado creado: {egresado.numero_control} - {egresado.nombre}')
            else:
                self.stdout.write(f'Egresado ya existente: {egresado.numero_control} - {egresado.nombre}')

    def crear_documentos(self):
        documentos = documentos = [
        {
            'clave': 'id',
            'titulo': 'Identificación',
            'descripcion': 'Puede ser una INE, pasaporte y otros?', 
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'e_firma',
            'titulo': 'Firma Electronica',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'beca',
            'titulo': 'Beca',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'impresion',
            'titulo': 'Autorizacion de Impresion',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'practicas',
            'titulo': 'Liberación de Practicas Profesionales',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'ingles',
            'titulo': 'Liberación de Inglés',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'p_titulacion',
            'titulo': 'Liberacion de Proyecto de Titulación',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 's_social',
            'titulo': 'Liberacion de Servicio Social',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'licenciatura',
            'titulo': 'Certificado de Licenciatura',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'bachillerato',
            'titulo': 'Certificado de Bachillerato',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'curp',
            'titulo': 'CURP',
            'descripcion': 'Clave Única de Registro de Población',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'acta',
            'titulo': 'Acta de Nacimiento',
            'descripcion': 'Acta de nacimiento digital o escaneada',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'linea_1',
            'titulo': 'Recibo de Linea de Pago 2',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'linea_2',
            'titulo': 'Recibo de Linea de Pago 1',
            'descripcion': '',
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
        {
            'clave': 'cni',
            'titulo': 'Carta de No Inconveniencia',
            'descripcion': '',      
            'extensiones_aceptados': 'pdf, png, jpg, jpeg',
        },
    ]

        for datos in documentos:
            documento, created = Documento.objects.get_or_create(
                clave = datos['clave'],
                defaults={
                    'titulo': datos['titulo'],
                    'descripcion': datos['descripcion'],
                    'extensiones_aceptados': datos['extensiones_aceptados'],
                }
            )

            if created:
                self.stdout.write(f'Documento creado: {datos["clave"]}')

    def crear_etapas(self):
        etapas = [
            {
                'nombre': 'identificacion_se',
                'titulo': 'Identificacion',
                'descripcion': 'Recepción y validación de identificación oficial del egresado.',
                'orden': 1
            },
            {
                'nombre': 'revision_egresados',
                'titulo': 'Revicion de Documentos',
                'descripcion': 'Revisión de documentos entregados por el egresado.',
                'orden': 2
            },
            {
                'nombre': 'revision_se',
                'titulo': 'Revicion de Documentos',
                'descripcion': 'Revisión final por Servicios Escolares.',
                'orden': 3
            },
            {
                'nombre': 'segunda_revision_se',
                'titulo': 'Segunda Revicion de Documentos',
                'descripcion': 'Segunda revision.',
                'orden': 4
            },
            {
                'nombre': 'activar_linea_pago_se',
                'titulo': 'Activar linea de pago ',
                'descripcion': 'Activar linea de pago',
                'orden': 5
            },
            {
                'nombre': 'lineas_pago_egresados',
                'titulo': 'Pago',
                'descripcion': 'Generación de documentos finales para el egresado.',
                'orden': 6
            },
            {
                'nombre': 'lineas_pago_se',
                'titulo': 'Pago',
                'descripcion': 'Generación de documentos finales para el egresado.',
                'orden': 7
            },
            {
                'nombre': 'cni_egresado',
                'descripcion': 'Generación de documentos finales para el egresado.',
                'orden': 8
            },
        ]

        for datos in etapas:
            etapa, created = Etapa.objects.get_or_create(
                nombre=datos['nombre'],
                defaults={
                    'descripcion': datos['descripcion'],
                    'orden': datos['orden'],
                }
            )

            if created:
                self.stdout.write(f'Etapa creada: {datos["nombre"]}')