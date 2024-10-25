#!/bin/bash
set -e 

# run migrations
python manage.py makemigrations
python manage.py migrate
python service_registration/grpc_registration.py

# run the app
# exec gunicorn --bind 0.0.0.0:8000 user_service.wsgi:application
exec gunicorn --bind 0.0.0.0:8000 user_service.wsgi:application --reload --access-logfile '-' --error-logfile '-'
