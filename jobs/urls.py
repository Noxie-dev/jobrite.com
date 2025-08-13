from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_jobs, name='search'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),
    path('job/<int:job_id>/quick-apply/', views.quick_apply, name='quick_apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Saved searches
    path('save-search/', views.save_search, name='save_search'),
    path('saved-searches/', views.saved_searches, name='saved_searches'),
    path('saved-search/<int:search_id>/delete/', views.delete_saved_search, name='delete_saved_search'),
    
    # Employer URLs
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('employer/profile/', views.employer_profile, name='employer_profile'),
    path('employer/post-job/', views.post_job, name='post_job'),
    path('employer/job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('employer/job/<int:job_id>/applications/', views.job_applications_view, name='job_applications'),
    
    # Other pages
    path('faq/', views.faq, name='faq'),
    path('salary-calculator/', views.salary_calculator, name='salary_calculator'),
    path('cv-creator/', views.cv_creator, name='cv_creator'),
    path('contact/', views.contact, name='contact'),
]
