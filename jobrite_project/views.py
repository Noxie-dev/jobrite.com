from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

def health_check(request):
    """Health check endpoint for deployment platforms"""
    import sys
    from django.conf import settings
    
    try:
        # Basic database check
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return JsonResponse({
        'status': 'healthy',
        'message': 'JobRite Django app is running!',
        'platform': 'render' if 'render' in request.get_host() else 'unknown',
        'debug': settings.DEBUG,
        'python_version': sys.version,
        'database_status': db_status,
        'static_url': settings.STATIC_URL,
        'allowed_hosts': settings.ALLOWED_HOSTS[:5],  # First 5 only for security
        'environment_vars_set': {
            'SUPABASE_URL': bool(settings.SUPABASE_URL),
            'SUPABASE_KEY': bool(settings.SUPABASE_KEY),
            'SECRET_KEY': bool(settings.SECRET_KEY),
        }
    })

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)

def debug_view(request):
    """Simple debug view to test basic functionality"""
    import os
    from django.conf import settings
    
    debug_info = {
        'message': 'Django is working!',
        'environment': {
            'DEBUG': settings.DEBUG,
            'SECRET_KEY_SET': bool(settings.SECRET_KEY),
            'SUPABASE_URL_SET': bool(getattr(settings, 'SUPABASE_URL', None)),
            'SUPABASE_KEY_SET': bool(getattr(settings, 'SUPABASE_KEY', None)),
        },
        'database': 'testing_db_connection',
    }
    
    # Test database connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            debug_info['database'] = 'connected'
    except Exception as e:
        debug_info['database'] = f'error: {str(e)}'
    
    return JsonResponse(debug_info)
