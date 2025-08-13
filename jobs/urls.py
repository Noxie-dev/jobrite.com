from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('faq/', views.faq, name='faq'),
    path('salary-calculator/', views.salary_calculator, name='salary_calculator'),
    path('cv-creator/', views.cv_creator, name='cv_creator'),
    path('contact/', views.contact, name='contact'),
]