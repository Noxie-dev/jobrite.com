release: python manage.py collectstatic --noinput && python manage.py migrate
web: gunicorn jobrite_project.wsgi:application --bind 0.0.0.0:$PORT
