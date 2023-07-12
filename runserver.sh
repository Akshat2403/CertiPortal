#!/bin/sh
python manage.py collectstatic --no-input --clear
python manage.py createsuperuser --noinput
python manage.py migrate
gunicorn certiportal.wsgi:application --bind 0.0.0.0:80 --log-level=debug --timeout 180  --workers 4