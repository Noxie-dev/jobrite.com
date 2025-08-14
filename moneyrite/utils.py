"""
MoneyRite Financial Calculation Utilities
South African tax calculations with versioned rate engine
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Import observability with fallback
try:
    from .observability import observability
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False
    observability = None


class SARSTaxCalculator:
    """
    South African Revenue Service tax calculator with versioned rate engine

    This calculator uses a versioned rate engine to ensure calculations are always
    based on the most current and accurate SARS tax tables. Falls back to hardcoded
    2025 rates if the rate engine is unavailable.
    """

    # Fallback 2025 SARS Tax Brackets (annual amounts in ZAR)
    FALLBACK_TAX_BRACKETS = [
        (237100, Decimal('0.18')),    # 18% up to R237,100
        (370500, Decimal('0.26')),    # 26% up to R370,500
        (512800, Decimal('0.31')),    # 31% up to R512,800
        (673000, Decimal('0.36')),    # 36% up to R673,000
        (857900, Decimal('0.39')),    # 39% up to R857,900
        (1817000, Decimal('0.41')),   # 41% up to R1,817,000
        (float('inf'), Decimal('0.45'))  # 45% above R1,817,000
    ]

    # Fallback tax rebates (annual amounts in ZAR) - Corrected 2025 values
    FALLBACK_PRIMARY_REBATE = Decimal('17235')      # Under 65
    FALLBACK_SECONDARY_REBATE = Decimal('3300')     # 65-74 years (additional)
    FALLBACK_TERTIARY_REBATE = Decimal('1470')      # 75+ years (additional)

    # Fallback UIF (Unemployment Insurance Fund)
    FALLBACK_UIF_RATE = Decimal('0.01')             # 1% of salary
    FALLBACK_UIF_MONTHLY_CAP = Decimal('177.12')    # Maximum monthly UIF contribution

    # Fallback medical tax credits (monthly amounts in ZAR)
    FALLBACK_MEDICAL_CREDIT_MAIN = Decimal('364')   # Main member
    FALLBACK_MEDICAL_CREDIT_DEPENDENT = Decimal('364')  # First dependent
    FALLBACK_MEDICAL_CREDIT_ADDITIONAL = Decimal('246')  # Each additional dependent

    @classmethod
    def _get_rate_engine(cls):
        """Get rate engine instance, with error handling"""
        try:
            from .rate_engine import rate_engine
            return rate_engine
        except ImportError as e:
            logger.warning(f"Rate engine not available, using fallback rates: {e}")
            return None

    @classmethod
    def _get_current_config(cls):
        """Get current rate configuration, with fallback"""
        rate_eng = cls._get_rate_engine()
        if rate_eng:
            try:
                return rate_eng.get_current_rates()
            except Exception as e:
                logger.warning(f"Failed to get current rates from engine: {e}")
        return None

    @classmethod
    @property
    def TAX_BRACKETS(cls):
        """Get current tax brackets"""
        config = cls._get_current_config()
        if config:
            brackets = []
            for bracket in config.tax_brackets:
                limit = float(bracket.max_income) if bracket.max_income else float('inf')
                rate = bracket.rate
                brackets.append((limit, rate))
            return brackets
        return cls.FALLBACK_TAX_BRACKETS

    @classmethod
    @property
    def PRIMARY_REBATE(cls):
        """Get primary tax rebate"""
        config = cls._get_current_config()
        if config:
            for rebate in config.tax_rebates:
                if rebate.age_category == 'under_65':
                    return rebate.amount
        return cls.FALLBACK_PRIMARY_REBATE

    @classmethod
    @property
    def SECONDARY_REBATE(cls):
        """Get secondary tax rebate (additional for 65-74)"""
        config = cls._get_current_config()
        if config:
            for rebate in config.tax_rebates:
                if rebate.age_category == '65_to_74':
                    return rebate.amount
        return cls.FALLBACK_SECONDARY_REBATE

    @classmethod
    @property
    def TERTIARY_REBATE(cls):
        """Get tertiary tax rebate (additional for 75+)"""
        config = cls._get_current_config()
        if config:
            for rebate in config.tax_rebates:
                if rebate.age_category == '75_plus':
                    return rebate.amount
        return cls.FALLBACK_TERTIARY_REBATE

    @classmethod
    @property
    def UIF_RATE(cls):
        """Get UIF rate"""
        config = cls._get_current_config()
        if config:
            return config.uif_rate
        return cls.FALLBACK_UIF_RATE

    @classmethod
    @property
    def UIF_MONTHLY_CAP(cls):
        """Get UIF monthly cap"""
        config = cls._get_current_config()
        if config:
            return config.uif_monthly_cap
        return cls.FALLBACK_UIF_MONTHLY_CAP
    
    @classmethod
    def calculate_annual_tax(cls, annual_income: Decimal, age_category: str = 'under_65') -> Dict:
        """
        Calculate annual income tax based on SARS brackets

        Args:
            annual_income: Annual gross income in ZAR
            age_category: 'under_65', '65_to_74', or '75_plus'

        Returns:
            Dict with tax calculation breakdown
        """
        # Add observability tracing
        if OBSERVABILITY_AVAILABLE and observability:
            with observability.trace_span("calculate_annual_tax", {
                "annual_income": str(annual_income),
                "age_category": age_category
            }):
                return cls._calculate_annual_tax_impl(annual_income, age_category)
        else:
            return cls._calculate_annual_tax_impl(annual_income, age_category)

    @classmethod
    def _calculate_annual_tax_impl(cls, annual_income: Decimal, age_category: str = 'under_65') -> Dict:
        """Implementation of annual tax calculation"""
        annual_income = Decimal(str(annual_income))

        # Calculate tax before rebates using cumulative brackets
        tax_before_rebates = Decimal('0')
        previous_limit = Decimal('0')

        for bracket_limit, rate in cls.TAX_BRACKETS:
            current_limit = Decimal(str(bracket_limit)) if bracket_limit != float('inf') else annual_income

            if annual_income <= previous_limit:
                break

            # Calculate taxable amount in this bracket
            taxable_in_bracket = min(annual_income, current_limit) - previous_limit

            if taxable_in_bracket > 0:
                bracket_tax = taxable_in_bracket * rate
                tax_before_rebates += bracket_tax

            # Move to next bracket
            previous_limit = current_limit

            if bracket_limit == float('inf') or annual_income <= current_limit:
                break

        # Apply age-based rebates
        total_rebate = cls.PRIMARY_REBATE
        if age_category == '65_to_74':
            total_rebate += cls.SECONDARY_REBATE
        elif age_category == '75_plus':
            total_rebate += cls.SECONDARY_REBATE + cls.TERTIARY_REBATE

        # Final tax calculation
        annual_tax = max(Decimal('0'), tax_before_rebates - total_rebate)

        return {
            'annual_income': annual_income,
            'tax_before_rebates': tax_before_rebates,
            'total_rebate': total_rebate,
            'annual_tax': annual_tax,
            'effective_rate': (annual_tax / annual_income * 100) if annual_income > 0 else Decimal('0'),
            'marginal_rate': cls._get_marginal_rate(annual_income)
        }
    
    @classmethod
    def _get_marginal_rate(cls, annual_income: Decimal) -> Decimal:
        """Get the marginal tax rate for given income"""
        for bracket_limit, rate in cls.TAX_BRACKETS:
            if annual_income <= bracket_limit:
                return rate * 100  # Return as percentage
        return cls.TAX_BRACKETS[-1][1] * 100  # Highest bracket

    @classmethod
    def get_tax_breakdown(cls, annual_income: Decimal, age_category: str = 'under_65') -> dict:
        """
        Get detailed tax breakdown by bracket for transparency

        Args:
            annual_income: Annual income amount
            age_category: Age category for rebate calculation

        Returns:
            Dict with detailed bracket-by-bracket breakdown
        """
        annual_income = Decimal(str(annual_income))

        brackets = []
        total_tax = Decimal('0')
        previous_limit = Decimal('0')

        for bracket_limit, rate in cls.TAX_BRACKETS:
            current_limit = Decimal(str(bracket_limit)) if bracket_limit != float('inf') else annual_income

            if annual_income <= previous_limit:
                break

            # Calculate taxable amount in this bracket
            taxable_in_bracket = min(annual_income, current_limit) - previous_limit

            if taxable_in_bracket > 0:
                bracket_tax = taxable_in_bracket * rate
                total_tax += bracket_tax

                # Format bracket info
                if bracket_limit == float('inf'):
                    range_str = f"R{previous_limit:,.0f}+"
                else:
                    range_str = f"R{previous_limit:,.0f} - R{current_limit:,.0f}"

                brackets.append({
                    'range': range_str,
                    'rate': f"{rate * 100:.0f}%",
                    'taxable_amount': f"R{taxable_in_bracket:,.2f}",
                    'tax': f"R{bracket_tax:,.2f}"
                })

            previous_limit = current_limit
            if bracket_limit == float('inf') or annual_income <= current_limit:
                break

        # Calculate rebates
        total_rebate = cls.PRIMARY_REBATE
        if age_category == '65_to_74':
            total_rebate += cls.SECONDARY_REBATE
        elif age_category == '75_plus':
            total_rebate += cls.SECONDARY_REBATE + cls.TERTIARY_REBATE

        final_tax = max(Decimal('0'), total_tax - total_rebate)

        return {
            'brackets': brackets,
            'total_before_rebates': f"R{total_tax:,.2f}",
            'primary_rebate': f"R{cls.PRIMARY_REBATE:,.2f}",
            'secondary_rebate': f"R{cls.SECONDARY_REBATE:,.2f}" if age_category != 'under_65' else None,
            'tertiary_rebate': f"R{cls.TERTIARY_REBATE:,.2f}" if age_category == '75_plus' else None,
            'total_rebate': f"R{total_rebate:,.2f}",
            'final_tax': f"R{final_tax:,.2f}",
            'effective_rate': f"{(final_tax / annual_income * 100) if annual_income > 0 else 0:.2f}%"
        }
    
    @classmethod
    def calculate_uif(cls, monthly_gross: Decimal) -> Decimal:
        """Calculate monthly UIF contribution"""
        monthly_gross = Decimal(str(monthly_gross))
        uif_amount = monthly_gross * cls.UIF_RATE
        return min(uif_amount, cls.UIF_MONTHLY_CAP)
    
    @classmethod
    def calculate_medical_tax_credit(cls, members: int) -> Decimal:
        """
        Calculate monthly medical tax credit
        
        Args:
            members: Number of medical scheme members
        
        Returns:
            Monthly medical tax credit amount
        """
        if members <= 0:
            return Decimal('0')
        
        credit = cls.MEDICAL_CREDIT_MAIN  # Main member
        
        if members > 1:
            credit += cls.MEDICAL_CREDIT_DEPENDENT  # First dependent
        
        if members > 2:
            additional_dependents = members - 2
            credit += additional_dependents * cls.MEDICAL_CREDIT_ADDITIONAL
        
        return credit


class PayRateConverter:
    """Convert between different pay rate periods"""
    
    # Standard conversion factors
    WEEKS_PER_MONTH = Decimal('4.33')  # 52 weeks / 12 months
    MONTHS_PER_YEAR = Decimal('12')
    WEEKS_PER_YEAR = Decimal('52')
    DAYS_PER_WEEK = Decimal('5')  # Standard work week
    
    @classmethod
    def to_monthly(cls, amount: Decimal, period: str, hours_per_week: Decimal = Decimal('40')) -> Decimal:
        """Convert any pay period to monthly amount"""
        amount = Decimal(str(amount))
        hours_per_week = Decimal(str(hours_per_week))
        
        if period == 'monthly':
            return amount
        elif period == 'annually':
            return amount / cls.MONTHS_PER_YEAR
        elif period == 'weekly':
            return amount * cls.WEEKS_PER_MONTH
        elif period == 'daily':
            return amount * cls.DAYS_PER_WEEK * cls.WEEKS_PER_MONTH
        elif period == 'hourly':
            hours_per_month = hours_per_week * cls.WEEKS_PER_MONTH
            return amount * hours_per_month
        else:
            raise ValueError(f"Unknown pay period: {period}")
    
    @classmethod
    def from_monthly(cls, monthly_amount: Decimal, target_period: str, hours_per_week: Decimal = Decimal('40')) -> Decimal:
        """Convert monthly amount to target period"""
        monthly_amount = Decimal(str(monthly_amount))
        hours_per_week = Decimal(str(hours_per_week))
        
        if target_period == 'monthly':
            return monthly_amount
        elif target_period == 'annually':
            return monthly_amount * cls.MONTHS_PER_YEAR
        elif target_period == 'weekly':
            return monthly_amount / cls.WEEKS_PER_MONTH
        elif target_period == 'daily':
            return monthly_amount / (cls.DAYS_PER_WEEK * cls.WEEKS_PER_MONTH)
        elif target_period == 'hourly':
            hours_per_month = hours_per_week * cls.WEEKS_PER_MONTH
            return monthly_amount / hours_per_month
        else:
            raise ValueError(f"Unknown target period: {target_period}")


def calculate_net_salary(gross_monthly: Decimal, include_medical: bool = False,
                        medical_members: int = 1, pension_percentage: Decimal = Decimal('0'),
                        age_category: str = 'under_65') -> Dict:
    """
    Calculate net monthly salary after all deductions

    Args:
        gross_monthly: Monthly gross salary
        include_medical: Whether to include medical tax credit
        medical_members: Number of medical scheme members
        pension_percentage: Pension contribution as percentage of gross
        age_category: Age category for tax rebates

    Returns:
        Dict with complete salary breakdown including pay rate conversions
    """
    gross_monthly = Decimal(str(gross_monthly))
    pension_percentage = Decimal(str(pension_percentage))

    # Calculate annual figures for tax calculation
    gross_annual = gross_monthly * Decimal('12')

    # Calculate pension contribution (pre-tax)
    pension_monthly = gross_monthly * (pension_percentage / Decimal('100'))
    taxable_annual = gross_annual - (pension_monthly * Decimal('12'))

    # Calculate income tax
    tax_calc = SARSTaxCalculator.calculate_annual_tax(taxable_annual, age_category)
    income_tax_monthly = tax_calc['annual_tax'] / Decimal('12')

    # Calculate UIF
    uif_monthly = SARSTaxCalculator.calculate_uif(gross_monthly)

    # Calculate medical tax credit (reduces tax, not salary)
    medical_credit_monthly = Decimal('0')
    if include_medical:
        medical_credit_monthly = SARSTaxCalculator.calculate_medical_tax_credit(medical_members)
        income_tax_monthly = max(Decimal('0'), income_tax_monthly - medical_credit_monthly)

    # Calculate net salary
    total_deductions = income_tax_monthly + uif_monthly + pension_monthly
    net_monthly = gross_monthly - total_deductions

    # Calculate pay rate conversions
    conversions = {
        'hourly': PayRateConverter.from_monthly(gross_monthly, 'hourly').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'daily': PayRateConverter.from_monthly(gross_monthly, 'daily').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'weekly': PayRateConverter.from_monthly(gross_monthly, 'weekly').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'monthly': gross_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'annually': PayRateConverter.from_monthly(gross_monthly, 'annually').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    }

    return {
        'gross_monthly': gross_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'gross_annual': gross_annual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'pension_monthly': pension_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'taxable_annual': taxable_annual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'income_tax_monthly': income_tax_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'uif_monthly': uif_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'medical_credit_monthly': medical_credit_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'total_deductions': total_deductions.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'net_monthly': net_monthly.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'effective_tax_rate': tax_calc['effective_rate'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'marginal_tax_rate': tax_calc['marginal_rate'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'conversions': conversions
    }
