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