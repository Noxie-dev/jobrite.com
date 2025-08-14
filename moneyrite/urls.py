from django.urls import path
from . import views

app_name = 'moneyrite'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Salary & Tax Calculator
    path('salary-calculator/', views.salary_calculator, name='salary_calculator'),
    path('api/calculate-salary/', views.calculate_salary_api, name='calculate_salary_api'),
    
    # Budget Planner
    path('budget-planner/', views.budget_planner, name='budget_planner'),
    path('budget/create/', views.create_budget, name='create_budget'),
    path('budget/<uuid:budget_id>/', views.budget_detail, name='budget_detail'),
    path('budget/<uuid:budget_id>/edit/', views.edit_budget, name='edit_budget'),
    path('budget/<uuid:budget_id>/delete/', views.delete_budget, name='delete_budget'),
    path('api/calculate-budget/', views.calculate_budget_api, name='calculate_budget_api'),
    
    # Credit & Debt Tracker
    path('credit-tracker/', views.credit_tracker, name='credit_tracker'),
    path('debt/add/', views.add_debt, name='add_debt'),
    path('debt/<uuid:debt_id>/', views.debt_detail, name='debt_detail'),
    path('debt/<uuid:debt_id>/edit/', views.edit_debt, name='edit_debt'),
    path('debt/<uuid:debt_id>/delete/', views.delete_debt, name='delete_debt'),
    path('debt/<uuid:debt_id>/payment/', views.add_payment, name='add_payment'),
    path('api/debt-calculations/', views.debt_calculations_api, name='debt_calculations_api'),
    
    # Financial Profile
    path('profile/', views.financial_profile, name='financial_profile'),
    path('profile/update/', views.update_financial_profile, name='update_financial_profile'),
]
