from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid


class UserFinancialProfile(models.Model):
    """User's financial profile and preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='financial_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Preferences
    default_hours_per_week = models.DecimalField(
        max_digits=5, decimal_places=2, default=40.00,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('168.00'))]
    )
    include_medical_aid = models.BooleanField(default=False)
    medical_aid_members = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    include_pension = models.BooleanField(default=False)
    pension_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('27.50'))]
    )

    def __str__(self):
        return f"Financial Profile - {self.user.username}"


class SalaryCalculation(models.Model):
    """Salary and tax calculation records"""
    PAY_PERIOD_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annually', 'Annually'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salary_calculations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Input data
    pay_amount = models.DecimalField(max_digits=12, decimal_places=2)
    pay_period = models.CharField(max_length=10, choices=PAY_PERIOD_CHOICES)
    hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=40.00)

    # Calculated values (stored for performance)
    gross_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gross_annual = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    income_tax_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    uif_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    medical_tax_credit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    pension_contribution = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    net_monthly = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Salary Calc - {self.user.username} - R{self.pay_amount}/{self.pay_period}"


class BudgetPlan(models.Model):
    """User's budget plan with South African expense categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=100, default="My Budget")
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2)

    # South African expense categories
    housing_rent_bond = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    groceries_household = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    utilities_water_electricity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transport_fuel_taxi = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    education_school_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    healthcare_medical = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    loan_repayments = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    family_black_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    entertainment_lifestyle = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    savings_investments = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-updated_at']

    def total_expenses(self):
        """Calculate total monthly expenses"""
        return (
            self.housing_rent_bond + self.groceries_household +
            self.utilities_water_electricity + self.transport_fuel_taxi +
            self.education_school_fees + self.healthcare_medical +
            self.insurance + self.loan_repayments + self.family_black_tax +
            self.entertainment_lifestyle + self.savings_investments + self.other_expenses
        )

    def remaining_balance(self):
        """Calculate remaining balance after expenses"""
        return self.monthly_income - self.total_expenses()

    def __str__(self):
        return f"Budget - {self.user.username} - {self.name}"


class DebtAccount(models.Model):
    """Individual debt/loan account tracking"""
    DEBT_TYPE_CHOICES = [
        ('home_loan', 'Home Loan'),
        ('car_loan', 'Car Loan'),
        ('personal_loan', 'Personal Loan'),
        ('credit_card', 'Credit Card'),
        ('store_account', 'Store Account'),
        ('student_loan', 'Student Loan'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debt_accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Account details
    account_name = models.CharField(max_length=100)
    debt_type = models.CharField(max_length=20, choices=DEBT_TYPE_CHOICES)
    creditor_name = models.CharField(max_length=100, blank=True)

    # Financial details
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    annual_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('50.00'))]
    )
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)

    # Term details
    original_term_months = models.IntegerField(null=True, blank=True)
    remaining_term_months = models.IntegerField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_paid_off = models.BooleanField(default=False)

    class Meta:
        ordering = ['-current_balance']

    def monthly_interest_rate(self):
        """Calculate monthly interest rate from annual rate"""
        return self.annual_interest_rate / Decimal('12') / Decimal('100')

    def monthly_interest_amount(self):
        """Calculate monthly interest on current balance"""
        return self.current_balance * self.monthly_interest_rate()

    def principal_payment(self):
        """Calculate principal portion of monthly payment"""
        return max(Decimal('0'), self.monthly_payment - self.monthly_interest_amount())

    def payoff_months_remaining(self):
        """Estimate months remaining to pay off debt"""
        if self.monthly_payment <= self.monthly_interest_amount():
            return None  # Payment doesn't cover interest

        balance = self.current_balance
        months = 0
        while balance > 0 and months < 600:  # Cap at 50 years
            interest = balance * self.monthly_interest_rate()
            principal = self.monthly_payment - interest
            if principal <= 0:
                return None
            balance -= principal
            months += 1
        return months if balance <= 0 else None

    def progress_percentage(self):
        """Calculate percentage of debt paid off"""
        if self.original_amount <= 0:
            return 0
        paid_amount = self.original_amount - self.current_balance
        return (paid_amount / self.original_amount) * 100

    def monthly_principal_amount(self):
        """Calculate principal portion of monthly payment"""
        return max(Decimal('0'), self.monthly_payment - self.monthly_interest_amount())

    def total_interest_remaining(self):
        """Calculate total interest remaining if paying minimum payments"""
        payoff_months = self.payoff_months_remaining()
        if not payoff_months:
            return Decimal('0')

        total_payments = self.monthly_payment * payoff_months
        return total_payments - self.current_balance

    def __str__(self):
        return f"{self.account_name} - R{self.current_balance}"


class DebtPayment(models.Model):
    """Record of debt payments made"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debt_account = models.ForeignKey(DebtAccount, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_portion = models.DecimalField(max_digits=10, decimal_places=2)
    principal_portion = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after_payment = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment - {self.debt_account.account_name} - R{self.payment_amount}"
