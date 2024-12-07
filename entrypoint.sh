#!/bin/sh

DJ_PORT=${PORT:-8000}

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn -b "0.0.0.0:${DJ_PORT}" web.wsgi:application