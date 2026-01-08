#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py inicializar_datos
export DJANGO_SUPERUSER_PASSWORD=admin4life
python manage.py createsuperuser --noinput --username=admin --email=rivas.raulh@gmail.com
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 titulacion_itm.wsgi:application