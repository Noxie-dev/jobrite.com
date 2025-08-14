from django.contrib import admin
from .models import UserFinancialProfile, SalaryCalculation, BudgetPlan, DebtAccount, DebtPayment


@admin.register(UserFinancialProfile)
class UserFinancialProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_hours_per_week', 'include_medical_aid', 'include_pension', 'created_at']
    list_filter = ['include_medical_aid', 'include_pension', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SalaryCalculation)
class SalaryCalculationAdmin(admin.ModelAdmin):
    list_display = ['user', 'pay_amount', 'pay_period', 'gross_monthly', 'net_monthly', 'created_at']
    list_filter = ['pay_period', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'monthly_income', 'total_expenses', 'remaining_balance', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    def total_expenses(self, obj):
        return obj.total_expenses()
    total_expenses.short_description = 'Total Expenses'

    def remaining_balance(self, obj):
        return obj.remaining_balance()
    remaining_balance.short_description = 'Remaining Balance'


@admin.register(DebtAccount)
class DebtAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_name', 'debt_type', 'current_balance', 'monthly_payment', 'is_active', 'created_at']
    list_filter = ['debt_type', 'is_active', 'is_paid_off', 'created_at']
    search_fields = ['user__username', 'user__email', 'account_name', 'creditor_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-current_balance']


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ['debt_account', 'payment_date', 'payment_amount', 'principal_portion', 'balance_after_payment', 'created_at']
    list_filter = ['payment_date', 'created_at']
    search_fields = ['debt_account__account_name', 'debt_account__user__username']
    readonly_fields = ['id', 'created_at']
    ordering = ['-payment_date']
