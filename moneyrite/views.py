from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from decimal import Decimal, InvalidOperation
import json

from .models import UserFinancialProfile, SalaryCalculation, BudgetPlan, DebtAccount, DebtPayment
from .utils import SARSTaxCalculator, PayRateConverter, calculate_net_salary
from .forms import (
    FinancialProfileForm, SalaryCalculatorForm, BudgetPlanForm,
    DebtAccountForm, DebtPaymentForm
)
from .resilience import calculation_rate_limiter, GracefulDegradation


@login_required
def dashboard(request):
    """MoneyRite dashboard with financial overview"""
    # Get or create user's financial profile
    profile, created = UserFinancialProfile.objects.get_or_create(user=request.user)

    # Get latest salary calculation
    latest_salary = SalaryCalculation.objects.filter(user=request.user).first()

    # Get active budget
    active_budget = BudgetPlan.objects.filter(user=request.user).first()

    # Get debt summary
    active_debts = DebtAccount.objects.filter(user=request.user, is_active=True)
    total_debt = sum(debt.current_balance for debt in active_debts)
    total_monthly_payments = sum(debt.monthly_payment for debt in active_debts)

    context = {
        'profile': profile,
        'latest_salary': latest_salary,
        'active_budget': active_budget,
        'active_debts': active_debts,
        'total_debt': total_debt,
        'total_monthly_payments': total_monthly_payments,
        'debt_count': active_debts.count(),
    }

    return render(request, 'moneyrite/dashboard.html', context)


@login_required
def salary_calculator(request):
    """Salary and tax calculator"""
    profile, created = UserFinancialProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SalaryCalculatorForm(request.POST)
        if form.is_valid():
            # Create salary calculation record
            hours_per_week = form.cleaned_data.get('hours_per_week') or profile.default_hours_per_week or Decimal('40.00')
            # Ensure hours_per_week is a Decimal for database storage
            hours_per_week = Decimal(str(hours_per_week))

            calc = SalaryCalculation.objects.create(
                user=request.user,
                pay_amount=form.cleaned_data['pay_amount'],
                pay_period=form.cleaned_data['pay_period'],
                hours_per_week=hours_per_week
            )

            # Calculate all values
            gross_monthly = PayRateConverter.to_monthly(
                calc.pay_amount,
                calc.pay_period,
                calc.hours_per_week
            )

            # Get additional parameters from form or profile
            include_medical = form.cleaned_data.get('include_medical_aid', profile.include_medical_aid)
            medical_members = form.cleaned_data.get('medical_aid_members', profile.medical_aid_members)
            pension_percentage = form.cleaned_data.get('pension_percentage', profile.pension_percentage)

            # Calculate net salary
            salary_breakdown = calculate_net_salary(
                gross_monthly=gross_monthly,
                include_medical=include_medical,
                medical_members=medical_members,
                pension_percentage=pension_percentage
            )

            # Update calculation record
            calc.gross_monthly = salary_breakdown['gross_monthly']
            calc.gross_annual = salary_breakdown['gross_annual']
            calc.income_tax_monthly = salary_breakdown['income_tax_monthly']
            calc.uif_monthly = salary_breakdown['uif_monthly']
            calc.medical_tax_credit = salary_breakdown['medical_credit_monthly']
            calc.pension_contribution = salary_breakdown['pension_monthly']
            calc.net_monthly = salary_breakdown['net_monthly']
            calc.save()

            messages.success(request, 'Salary calculation completed successfully!')

            context = {
                'form': form,
                'calculation': calc,
                'salary_breakdown': salary_breakdown,
                'profile': profile,
            }
            return render(request, 'moneyrite/salary_calculator.html', context)
    else:
        form = SalaryCalculatorForm()

    # Get recent calculations
    recent_calculations = SalaryCalculation.objects.filter(user=request.user)[:5]

    context = {
        'form': form,
        'profile': profile,
        'recent_calculations': recent_calculations,
    }

    return render(request, 'moneyrite/salary_calculator.html', context)


@login_required
@require_http_methods(["POST"])
def calculate_salary_api(request):
    """API endpoint for real-time salary calculations with resilience patterns"""
    from .resilience import rate_limit, GracefulDegradation
    from .observability import observability

    # Apply rate limiting
    if not calculation_rate_limiter.is_allowed(str(request.user.id)):
        return JsonResponse({
            'error': 'Rate limit exceeded. Please try again later.',
            'retry_after': 60
        }, status=429)

    try:
        # Record API request
        if observability:
            observability.record_rate_engine_access('salary_calculation_api')

        data = json.loads(request.body)

        pay_amount = Decimal(str(data.get('pay_amount', 0)))
        pay_period = data.get('pay_period', 'monthly')
        hours_per_week = Decimal(str(data.get('hours_per_week', 40)))
        include_medical = data.get('include_medical', False)
        medical_members = int(data.get('medical_members', 1))
        pension_percentage = Decimal(str(data.get('pension_percentage', 0)))

        # Convert to monthly
        gross_monthly = PayRateConverter.to_monthly(pay_amount, pay_period, hours_per_week)

        # Calculate net salary
        salary_breakdown = calculate_net_salary(
            gross_monthly=gross_monthly,
            include_medical=include_medical,
            medical_members=medical_members,
            pension_percentage=pension_percentage
        )

        # Convert Decimal values to strings for JSON serialization
        response_data = {}
        for key, value in salary_breakdown.items():
            if isinstance(value, Decimal):
                response_data[key] = str(value)
            else:
                response_data[key] = value

        # Add conversions to other periods
        response_data['conversions'] = {
            'hourly': str(PayRateConverter.from_monthly(gross_monthly, 'hourly', hours_per_week)),
            'daily': str(PayRateConverter.from_monthly(gross_monthly, 'daily', hours_per_week)),
            'weekly': str(PayRateConverter.from_monthly(gross_monthly, 'weekly', hours_per_week)),
            'monthly': str(gross_monthly),
            'annually': str(PayRateConverter.from_monthly(gross_monthly, 'annually', hours_per_week)),
        }

        return JsonResponse(response_data)

    except (ValueError, InvalidOperation, KeyError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def budget_planner(request):
    """Budget planner main view"""
    budgets = BudgetPlan.objects.filter(user=request.user)

    context = {
        'budgets': budgets,
    }

    return render(request, 'moneyrite/budget_planner.html', context)


@login_required
def create_budget(request):
    """Create new budget plan"""
    if request.method == 'POST':
        form = BudgetPlanForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget plan created successfully!')
            return redirect('moneyrite:budget_detail', budget_id=budget.id)
    else:
        form = BudgetPlanForm()

    context = {
        'form': form,
        'page_title': 'Create Budget Plan',
    }

    return render(request, 'moneyrite/budget_form.html', context)


@login_required
def budget_detail(request, budget_id):
    """Budget plan detail view"""
    budget = get_object_or_404(BudgetPlan, id=budget_id, user=request.user)

    context = {
        'budget': budget,
    }

    return render(request, 'moneyrite/budget_detail.html', context)


@login_required
def edit_budget(request, budget_id):
    """Edit existing budget plan"""
    budget = get_object_or_404(BudgetPlan, id=budget_id, user=request.user)

    if request.method == 'POST':
        form = BudgetPlanForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget plan updated successfully!')
            return redirect('moneyrite:budget_detail', budget_id=budget.id)
    else:
        form = BudgetPlanForm(instance=budget)

    context = {
        'form': form,
        'budget': budget,
        'page_title': 'Edit Budget Plan',
    }

    return render(request, 'moneyrite/budget_form.html', context)


@login_required
def delete_budget(request, budget_id):
    """Delete budget plan"""
    budget = get_object_or_404(BudgetPlan, id=budget_id, user=request.user)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget plan deleted successfully!')
        return redirect('moneyrite:budget_planner')

    context = {
        'budget': budget,
    }

    return render(request, 'moneyrite/budget_confirm_delete.html', context)


@login_required
@require_http_methods(["POST"])
def calculate_budget_api(request):
    """API endpoint for real-time budget calculations"""
    try:
        data = json.loads(request.body)

        monthly_income = Decimal(str(data.get('monthly_income', 0)))
        expenses = {}
        total_expenses = Decimal('0')

        # Calculate total expenses
        expense_fields = [
            'housing_rent_bond', 'groceries_household', 'utilities_water_electricity',
            'transport_fuel_taxi', 'education_school_fees', 'healthcare_medical',
            'insurance', 'loan_repayments', 'family_black_tax',
            'entertainment_lifestyle', 'savings_investments', 'other_expenses'
        ]

        for field in expense_fields:
            amount = Decimal(str(data.get(field, 0)))
            expenses[field] = amount
            total_expenses += amount

        remaining_balance = monthly_income - total_expenses

        response_data = {
            'monthly_income': str(monthly_income),
            'total_expenses': str(total_expenses),
            'remaining_balance': str(remaining_balance),
            'is_overspending': remaining_balance < 0,
            'expenses': {k: str(v) for k, v in expenses.items()}
        }

        return JsonResponse(response_data)

    except (ValueError, InvalidOperation, KeyError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def credit_tracker(request):
    """Credit and debt tracker main view"""
    active_debts = DebtAccount.objects.filter(user=request.user, is_active=True)
    paid_off_debts = DebtAccount.objects.filter(user=request.user, is_paid_off=True)

    # Calculate summary statistics
    total_debt = sum(debt.current_balance for debt in active_debts)
    total_monthly_payments = sum(debt.monthly_payment for debt in active_debts)

    context = {
        'active_debts': active_debts,
        'paid_off_debts': paid_off_debts,
        'total_debt': total_debt,
        'total_monthly_payments': total_monthly_payments,
        'debt_count': active_debts.count(),
    }

    return render(request, 'moneyrite/credit_tracker.html', context)


@login_required
def add_debt(request):
    """Add new debt account"""
    if request.method == 'POST':
        form = DebtAccountForm(request.POST)
        if form.is_valid():
            debt = form.save(commit=False)
            debt.user = request.user
            debt.save()
            messages.success(request, 'Debt account added successfully!')
            return redirect('moneyrite:debt_detail', debt_id=debt.id)
    else:
        form = DebtAccountForm()

    context = {
        'form': form,
        'page_title': 'Add Debt Account',
    }

    return render(request, 'moneyrite/debt_form.html', context)


@login_required
def debt_detail(request, debt_id):
    """Debt account detail view"""
    debt = get_object_or_404(DebtAccount, id=debt_id, user=request.user)
    payments = DebtPayment.objects.filter(debt_account=debt)[:10]  # Last 10 payments

    context = {
        'debt': debt,
        'payments': payments,
        'payoff_months': debt.payoff_months_remaining(),
    }

    return render(request, 'moneyrite/debt_detail.html', context)


@login_required
def edit_debt(request, debt_id):
    """Edit existing debt account"""
    debt = get_object_or_404(DebtAccount, id=debt_id, user=request.user)

    if request.method == 'POST':
        form = DebtAccountForm(request.POST, instance=debt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Debt account updated successfully!')
            return redirect('moneyrite:debt_detail', debt_id=debt.id)
    else:
        form = DebtAccountForm(instance=debt)

    context = {
        'form': form,
        'debt': debt,
        'page_title': 'Edit Debt Account',
    }

    return render(request, 'moneyrite/debt_form.html', context)


@login_required
def delete_debt(request, debt_id):
    """Delete debt account"""
    debt = get_object_or_404(DebtAccount, id=debt_id, user=request.user)

    if request.method == 'POST':
        debt.delete()
        messages.success(request, 'Debt account deleted successfully!')
        return redirect('moneyrite:credit_tracker')

    context = {
        'debt': debt,
    }

    return render(request, 'moneyrite/debt_confirm_delete.html', context)


@login_required
def add_payment(request, debt_id):
    """Add payment to debt account"""
    debt = get_object_or_404(DebtAccount, id=debt_id, user=request.user)

    if request.method == 'POST':
        form = DebtPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.debt_account = debt

            # Calculate interest and principal portions
            interest_portion = debt.monthly_interest_amount()
            principal_portion = max(Decimal('0'), payment.payment_amount - interest_portion)

            payment.interest_portion = interest_portion
            payment.principal_portion = principal_portion
            payment.balance_after_payment = debt.current_balance - principal_portion
            payment.save()

            # Update debt balance
            debt.current_balance = payment.balance_after_payment
            if debt.current_balance <= 0:
                debt.is_paid_off = True
                debt.is_active = False
            debt.save()

            messages.success(request, 'Payment recorded successfully!')
            return redirect('moneyrite:debt_detail', debt_id=debt.id)
    else:
        form = DebtPaymentForm()

    context = {
        'form': form,
        'debt': debt,
        'page_title': 'Add Payment',
    }

    return render(request, 'moneyrite/payment_form.html', context)


@login_required
@require_http_methods(["POST"])
def debt_calculations_api(request):
    """API endpoint for debt calculations"""
    try:
        data = json.loads(request.body)

        current_balance = Decimal(str(data.get('current_balance', 0)))
        annual_interest_rate = Decimal(str(data.get('annual_interest_rate', 0)))
        monthly_payment = Decimal(str(data.get('monthly_payment', 0)))

        # Calculate monthly interest rate
        monthly_rate = annual_interest_rate / Decimal('12') / Decimal('100')

        # Calculate monthly interest amount
        monthly_interest = current_balance * monthly_rate

        # Calculate principal payment
        principal_payment = max(Decimal('0'), monthly_payment - monthly_interest)

        # Calculate payoff time
        payoff_months = None
        if monthly_payment > monthly_interest:
            balance = current_balance
            months = 0
            while balance > 0 and months < 600:  # Cap at 50 years
                interest = balance * monthly_rate
                principal = monthly_payment - interest
                if principal <= 0:
                    break
                balance -= principal
                months += 1
            if balance <= 0:
                payoff_months = months

        response_data = {
            'monthly_interest_rate': str(monthly_rate * 100),
            'monthly_interest_amount': str(monthly_interest),
            'principal_payment': str(principal_payment),
            'payoff_months': payoff_months,
            'payoff_years': round(payoff_months / 12, 1) if payoff_months else None,
        }

        return JsonResponse(response_data)

    except (ValueError, InvalidOperation, KeyError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def financial_profile(request):
    """User financial profile view"""
    profile, created = UserFinancialProfile.objects.get_or_create(user=request.user)

    context = {
        'profile': profile,
    }

    return render(request, 'moneyrite/financial_profile.html', context)


@login_required
def update_financial_profile(request):
    """Update user financial profile"""
    profile, created = UserFinancialProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = FinancialProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Financial profile updated successfully!')
            return redirect('moneyrite:financial_profile')
    else:
        form = FinancialProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'page_title': 'Update Financial Profile',
    }

    return render(request, 'moneyrite/profile_form.html', context)
