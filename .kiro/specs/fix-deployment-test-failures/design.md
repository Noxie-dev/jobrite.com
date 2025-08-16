# Design Document

## Overview

This design addresses the critical test failures preventing successful deployment of the JobRite application. The failures are concentrated in the MoneyRite tax calculation system and involve calculation accuracy, input validation, and data structure consistency issues.

## Architecture

The fix involves four main components:
1. **Calculation Engine Fixes** - Correct mathematical inconsistencies in tax and salary calculations
2. **Input Validation Layer** - Add proper error handling for invalid inputs
3. **Data Structure Consistency** - Ensure all expected fields are present in calculation results
4. **Dependency Management** - Ensure all required packages are properly declared in requirements.txt

## Components and Interfaces

### 1. Tax Calculation Engine (`moneyrite/utils.py`)

**Issues to Fix:**
- Medical credit calculation returning annual amount instead of monthly
- Missing 'taxable_monthly' field in salary calculation results
- Insufficient input validation for edge cases

**Design Changes:**
- Fix medical credit calculation to return monthly amount (annual/12)
- Add 'taxable_monthly' field to salary calculation results
- Add comprehensive input validation with proper exception handling

### 2. Pay Rate Converter (`moneyrite/utils.py`)

**Issues to Fix:**
- Mathematical inconsistency in hourly-to-annual conversions via monthly
- Rounding precision issues causing test failures

**Design Changes:**
- Improve precision in conversion calculations
- Ensure consistent rounding across all conversion paths
- Use higher precision intermediate calculations

### 3. Input Validation System

**Issues to Fix:**
- Negative values not raising appropriate exceptions
- Invalid string inputs not handled properly
- Missing type checking for None values

**Design Changes:**
- Add explicit validation for negative values
- Implement proper string-to-decimal conversion with error handling
- Add type checking for None and invalid types

### 4. Dependency Management System

**Issues to Fix:**
- social_django is imported in Django settings but not declared in requirements.txt
- ModuleNotFoundError during deployment build process
- Missing dependency causing deployment failures

**Design Changes:**
- Add social-auth-app-django to requirements.txt
- Audit all INSTALLED_APPS for missing dependencies
- Ensure consistent dependency versions across environments

## Data Models

### Salary Calculation Result Structure
```python
{
    'gross_monthly': Decimal,
    'pension_monthly': Decimal,
    'taxable_monthly': Decimal,  # NEW: Required field
    'income_tax_monthly': Decimal,
    'uif_monthly': Decimal,
    'medical_credit_monthly': Decimal,  # FIX: Monthly amount, not annual
    'net_monthly': Decimal,
    'effective_tax_rate': Decimal,
    'marginal_tax_rate': Decimal
}
```

### Input Validation Rules
```python
def validate_financial_input(value):
    """Validate financial input with proper error handling"""
    if value is None:
        raise TypeError("Input cannot be None")
    
    if isinstance(value, str):
        try:
            decimal_value = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError(f"Invalid numeric input: {value}")
    else:
        decimal_value = Decimal(str(value))
    
    if decimal_value < 0:
        raise ValueError("Financial values cannot be negative")
    
    return decimal_value
```

## Error Handling

### Exception Hierarchy
1. **ValueError** - For negative values and invalid numeric strings
2. **TypeError** - For None values and wrong types
3. **InvalidOperation** - For decimal conversion failures
4. **Custom ValidationError** - For business logic violations

### Error Response Format
```python
{
    'error': True,
    'error_type': 'validation_error',
    'message': 'Descriptive error message',
    'field': 'field_name' (if applicable)
}
```

## Testing Strategy

### 1. Fix Golden Vector Tests
- Correct medical credit calculation expectation
- Ensure all salary breakdown fields are present
- Validate calculation accuracy against SARS requirements

### 2. Fix Property-Based Tests
- Improve conversion precision to pass consistency checks
- Add proper input validation to handle edge cases
- Ensure mathematical properties hold across all inputs

### 3. Fix Snapshot Tests
- Update error handling to match expected behavior
- Ensure data structure consistency
- Validate UI component integration

### 4. Deployment Validation
- Run full test suite before deployment
- Verify static file collection
- Test production configuration

## Implementation Approach

### Phase 1: Critical Calculation Fixes
1. Fix medical credit monthly calculation
2. Add missing 'taxable_monthly' field
3. Improve pay rate conversion precision

### Phase 2: Input Validation
1. Add comprehensive input validation
2. Implement proper exception handling
3. Update error message formatting

### Phase 3: Test Updates
1. Update test expectations where needed
2. Verify all tests pass
3. Run deployment process

### Phase 4: Dependency Management
1. Add missing social_django dependency to requirements.txt
2. Verify all Django apps in INSTALLED_APPS have corresponding packages
3. Test dependency installation locally

### Phase 5: Deployment
1. Collect static files
2. Run production deployment
3. Verify live site functionality