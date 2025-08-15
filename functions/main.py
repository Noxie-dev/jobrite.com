import os
import django
from django.core.wsgi import get_wsgi_application
from firebase_functions import https_fn

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.settings')
django.setup()

# Get Django WSGI application
application = get_wsgi_application()

@https_fn.on_request()
def djangoApp(req):
    """Firebase Function to serve Django application"""
    return application(req.environ, req.start_response)