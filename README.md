# Sistema de Gestión de Titulación ITM

Sistema web desarrollado en Django para la gestión de documentos y procesos de titulación de egresados del Instituto Tecnológico de Mexicali. Facilita el seguimiento del estado de titulación, carga de documentos, generación de reportes y coordinación entre estudiantes, docentes y servicios escolares.

##  Requisitos Previos

- **Python 3.13+** (para ejecución local)
- **Docker y Docker Compose** (para ejecución con contenedores)
- **Git** (para clonar el repositorio)
- **pip** (gestor de paquetes de Python)

##  Instalación y Ejecución Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Rivas-R/titulacion_itm.git
cd titulacion_itm
```

### 2. Crear un entorno virtual

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DEBUG=1
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Inicializar datos (opcional)

```bash
python manage.py inicializar_datos
```

### 7. Crear un superusuario

```bash
python manage.py createsuperuser
```

Ingresa los datos solicitados (nombre de usuario, email y contraseña).

### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000`

Panel de administración: `http://127.0.0.1:8000/admin`

---

##  Ejecución con Docker Compose

### 1. Clonar el repositorio

```bash
git clone https://github.com/Rivas-R/titulacion_itm.git
cd titulacion_itm
```

### 2. Configurar variables de entorno (opcional)

Puedes crear un archivo `.env` para personalizar la configuración, o usar los valores por defecto en el `docker-compose.yml`.

### 3. Construir e iniciar los contenedores

```bash
docker-compose up --build
```

El flag `--build` construye la imagen si no existe o si hay cambios en el `Dockerfile`.

Para ejecutar en segundo plano:

```bash
docker-compose up -d --build
```

### 4. Verificar que los servicios están corriendo

```bash
docker-compose ps
```

### 5. Acceder a la aplicación

- Aplicación web: `http://localhost`
- Panel de administración: `http://localhost/admin`
- API: `http://localhost/api` (si está configurada)

### 6. Comandos útiles

```bash
# Ver los logs de los contenedores
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f django-web

# Ejecutar un comando dentro del contenedor
docker-compose exec django-web python manage.py shell

# Detener los contenedores
docker-compose down

# Detener y eliminar volúmenes (cuidado: elimina datos)
docker-compose down -v
```

---

##  Construir una Imagen Docker

### 1. Construir la imagen manualmente

Para construir la imagen sin usar Docker Compose:

```bash
docker build -t titulacion-itm:latest .
```

Donde `titulacion-itm` es el nombre de la imagen y `latest` es la etiqueta. Puedes cambiarlos según tus necesidades.

### 2. Verificar que la imagen se construyó correctamente

```bash
docker images | findstr titulacion-itm
```

### 3. Ejecutar un contenedor desde la imagen

```bash
docker run -d \
  --name titulacion-container \
  -p 8000:8000 \
  -e DEBUG=0 \
  -e DJANGO_SECRET_KEY=tu-clave-secreta \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 \
  titulacion-itm:latest
```

### 4. Acceder a los logs del contenedor

```bash
docker logs -f titulacion-container
```

### 5. Ejecutar comandos dentro del contenedor

```bash
docker exec -it titulacion-container python manage.py shell
```

---

##  Estructura del Proyecto

```
titulacion_itm/
├── titulacion/                    # Aplicación principal de Django
│   ├── migrations/                # Migraciones de la base de datos
│   ├── management/
│   │   └── commands/
│   │       └── inicializar_datos.py   # Comando para inicializar datos
│   ├── static/                    # Archivos estáticos (CSS, JS, imágenes)
│   ├── templates/                 # Plantillas HTML
│   ├── models.py                  # Modelos de datos
│   ├── views.py                   # Vistas principales
│   ├── views_generador_documentos.py  # Vistas para generación de documentos
│   ├── urls.py                    # URLs de la aplicación
│   ├── admin.py                   # Configuración del panel admin
│   └── auth.py                    # Lógica de autenticación
├── titulacion_itm/                # Configuración del proyecto Django
│   ├── settings.py                # Configuración de Django
│   ├── urls.py                    # URLs principales
│   ├── wsgi.py                    # Configuración WSGI
│   └── asgi.py                    # Configuración ASGI
├── Dockerfile                     # Definición del contenedor Docker
├── docker-compose.yml             # Orquestación de servicios
├── nginx.conf                     # Configuración de Nginx
├── entrypoint.sh                  # Script de inicialización del contenedor
├── manage.py                      # Herramienta de gestión de Django
├── requirements.txt               # Dependencias de Python
└── README.md                      # Este archivo
```

---

##  Base de Datos

El proyecto utiliza las siguientes variables de entorno para la configuración de la base de datos (en contenedor):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=titulacion_db
DB_USER=titulacion_user
DB_PASSWORD=secure_password
DB_HOST=db
DB_PORT=5432
```

Para desarrollo local, Django usa SQLite por defecto (archivo `db.sqlite3`).

---

##  Dependencias Principales

- **Django 5.2.1** - Framework web
- **Gunicorn 23.0.0** - Servidor WSGI para producción
- **PostgreSQL (psycopg2)** - Base de datos en producción
- **Pillow 11.2.1** - Procesamiento de imágenes
- **ReportLab 4.4.1** - Generación de PDFs
- **Pandas & OpenPyXL** - Procesamiento de Excel

Ver `requirements.txt` para la lista completa.

---

##  Variables de Entorno Importantes

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `DEBUG` | `1` | Modo debug de Django |
| `DJANGO_SECRET_KEY` | `asdfasdfsad3234` | Clave secreta para producción |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1` | Hosts permitidos |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://127.0.0.1` | Orígenes CSRF confiables |
| `DB_ENGINE` | `sqlite3` (local) | Motor de base de datos |

---

##  Comandos Útiles de Django

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Inicializar datos
python manage.py inicializar_datos

# Recolectar archivos estáticos
python manage.py collectstatic

# Shell interactivo de Django
python manage.py shell

# Ejecutar servidor de desarrollo
python manage.py runserver [puerto]
```

---

##  Solución de Problemas

### El servidor no inicia en local

- Asegúrate de estar en el entorno virtual correcto
- Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
- Intenta eliminar y recrear la base de datos: `rm db.sqlite3` y ejecuta `python manage.py migrate`

### Error de conexión con Docker

- Verifica que Docker y Docker Compose estén instalados: `docker --version` y `docker-compose --version`
- Asegúrate de que el puerto 80 (Nginx) no esté en uso
- Revisa los logs: `docker-compose logs`

### Permisos en Linux/macOS

Si encuentras problemas de permisos, ejecuta:

```bash
chmod +x entrypoint.sh
sudo chown -R $USER:$USER .
```

---

##  Roles y Funcionalidades

- **Egresados**: Carga de documentos, seguimiento de progreso de titulación
- **Servicios Escolares**: Gestión general de procesos y etapas
- **Administrador**: Control total del sistema

---
