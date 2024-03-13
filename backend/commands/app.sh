#!/bin/bash

python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic

cp -r /app/collected_static/. /app/static/

gunicorn --bind 0.0.0.0:9000 backend.wsgi
