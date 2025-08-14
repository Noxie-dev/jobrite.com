from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .models import UserFinancialProfile, SalaryCalculation, BudgetPlan, DebtAccount, DebtPayment


class FinancialProfileForm(forms.ModelForm):
    """Form for user financial profile settings"""
    
    class Meta:
        model = UserFinancialProfile
        fields = [
            'default_hours_per_week', 'include_medical_aid', 'medical_aid_members',
            'include_pension', 'pension_percentage'
        ]
        widgets = {
            'default_hours_per_week': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '40.00',
                'step': '0.01',
                'min': '0.01',
                'max': '168.00'
            }),
            'medical_aid_members': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '1',
                'min': '1'
            }),
            'pension_percentage': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00',
                'max': '27.50'
            }),
            'include_medical_aid': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'include_pension': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'default_hours_per_week': 'Default Hours Per Week',
            'include_medical_aid': 'Include Medical Aid Tax Credit',
            'medical_aid_members': 'Number of Medical Aid Members',
            'include_pension': 'Include Pension Contributions',
            'pension_percentage': 'Pension Contribution (%)',
        }


class SalaryCalculatorForm(forms.Form):
    """Form for salary and tax calculations"""
    
    PAY_PERIOD_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annually', 'Annually'),
    ]
    
    pay_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter amount',
            'step': '0.01',
            'min': '0.01'
        }),
        label='Pay Amount (ZAR)'
    )
    
    pay_period = forms.ChoiceField(
        choices=PAY_PERIOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Pay Period'
    )
    
    hours_per_week = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('168.00'))],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '40.00',
            'step': '0.01',
            'min': '0.01',
            'max': '168.00'
        }),
        label='Hours Per Week',
        required=False,
        help_text='Required for hourly calculations'
    )
    
    include_medical_aid = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label='Include Medical Aid Tax Credit'
    )
    
    medical_aid_members = forms.IntegerField(
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '1',
            'min': '1'
        }),
        label='Number of Medical Aid Members',
        required=False
    )
    
    pension_percentage = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('27.50'))],
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.00',
            'max': '27.50'
        }),
        label='Pension Contribution (%)',
        required=False,
        help_text='Maximum 27.5% allowed by SARS'
    )


class BudgetPlanForm(forms.ModelForm):
    """Form for creating and editing budget plans"""
    
    class Meta:
        model = BudgetPlan
        fields = [
            'name', 'monthly_income', 'housing_rent_bond', 'groceries_household',
            'utilities_water_electricity', 'transport_fuel_taxi', 'education_school_fees',
            'healthcare_medical', 'insurance', 'loan_repayments', 'family_black_tax',
            'entertainment_lifestyle', 'savings_investments', 'other_expenses'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'My Budget Plan'
            }),
            'monthly_income': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'housing_rent_bond': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'groceries_household': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'utilities_water_electricity': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'transport_fuel_taxi': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'education_school_fees': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'healthcare_medical': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'insurance': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'loan_repayments': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'family_black_tax': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'entertainment_lifestyle': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'savings_investments': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'other_expenses': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
        }
        
        labels = {
            'name': 'Budget Name',
            'monthly_income': 'Monthly Income (ZAR)',
            'housing_rent_bond': 'Housing (Rent/Bond)',
            'groceries_household': 'Groceries & Household',
            'utilities_water_electricity': 'Utilities (Water/Electricity)',
            'transport_fuel_taxi': 'Transport (Fuel/Taxi)',
            'education_school_fees': 'Education (School Fees)',
            'healthcare_medical': 'Healthcare/Medical',
            'insurance': 'Insurance',
            'loan_repayments': 'Loan Repayments',
            'family_black_tax': 'Family Support (Black Tax)',
            'entertainment_lifestyle': 'Entertainment & Lifestyle',
            'savings_investments': 'Savings & Investments',
            'other_expenses': 'Other Expenses',
        }


class DebtAccountForm(forms.ModelForm):
    """Form for adding and editing debt accounts"""
    
    class Meta:
        model = DebtAccount
        fields = [
            'account_name', 'debt_type', 'creditor_name', 'original_amount',
            'current_balance', 'annual_interest_rate', 'monthly_payment',
            'original_term_months', 'next_payment_date'
        ]
        
        widgets = {
            'account_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Car Loan - Toyota'
            }),
            'debt_type': forms.Select(attrs={'class': 'form-input'}),
            'creditor_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Standard Bank'
            }),
            'original_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'current_balance': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.00'
            }),
            'annual_interest_rate': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '12.50',
                'step': '0.01',
                'min': '0.00',
                'max': '50.00'
            }),
            'monthly_payment': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'original_term_months': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '60',
                'min': '1'
            }),
            'next_payment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
        }
        
        labels = {
            'account_name': 'Account Name',
            'debt_type': 'Debt Type',
            'creditor_name': 'Creditor/Bank Name',
            'original_amount': 'Original Amount (ZAR)',
            'current_balance': 'Current Balance (ZAR)',
            'annual_interest_rate': 'Annual Interest Rate (%)',
            'monthly_payment': 'Monthly Payment (ZAR)',
            'original_term_months': 'Original Term (Months)',
            'next_payment_date': 'Next Payment Date',
        }


class DebtPaymentForm(forms.ModelForm):
    """Form for recording debt payments"""
    
    class Meta:
        model = DebtPayment
        fields = ['payment_date', 'payment_amount']
        
        widgets = {
            'payment_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'payment_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
        }
        
        labels = {
            'payment_date': 'Payment Date',
            'payment_amount': 'Payment Amount (ZAR)',
        }
