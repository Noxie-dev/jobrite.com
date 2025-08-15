from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

def health_check(request):
    """Simple health check endpoint for Vercel"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'JobRite Django app is running on Vercel!'
    })

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)