from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Onboarding
    path('onboarding/', views.onboarding, name='onboarding'),
    path('skip-onboarding/', views.skip_onboarding, name='skip_onboarding'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile_detail'),
]