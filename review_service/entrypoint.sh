#!/bin/bash
set -e 

# run migrations
python manage.py makemigrations
python manage.py migrate
python service_registration/grpc_registration.py

# run the app
# exec uvicorn review_service.asgi:application --host 0.0.0.0 --port 8000 --reload
exec uvicorn review_service.asgi:application --host 0.0.0.0 --port 8000 --reload --no-access-log