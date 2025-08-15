"""
WSGI config for jobrite_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobrite_project.settings")

# Initialize Django
application = get_wsgi_application()

# Vercel serverless function handler
def handler(request, context):
    return application(request, context)
