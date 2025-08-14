"""
Comprehensive Error Handling for MoneyRite

Provides structured error handling, user-friendly error messages,
and error recovery patterns for financial calculations.
"""

import logging
from typing import Dict, Any, Optional, Union
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


class MoneyRiteError(Exception):
    """Base exception for MoneyRite errors"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(message)


class CalculationError(MoneyRiteError):
    """Error in financial calculations"""
    pass


class ValidationError(MoneyRiteError):
    """Input validation error"""
    pass


class RateEngineError(MoneyRiteError):
    """Rate engine related error"""
    pass


class ExternalServiceError(MoneyRiteError):
    """External service unavailable error"""
    pass


class ErrorHandler:
    """Central error handling and recovery"""
    
    ERROR_MESSAGES = {
        # Validation errors
        'invalid_amount': _('Please enter a valid amount. Amount must be a positive number.'),
        'amount_too_large': _('Amount is too large. Please enter a reasonable value.'),
        'amount_negative': _('Amount cannot be negative.'),
        'invalid_percentage': _('Please enter a valid percentage between 0 and 100.'),
        'invalid_age_category': _('Please select a valid age category.'),
        'missing_required_field': _('This field is required.'),
        
        # Calculation errors
        'calculation_failed': _('Calculation failed. Please check your inputs and try again.'),
        'tax_calculation_error': _('Unable to calculate tax. Please verify your income amount.'),
        'uif_calculation_error': _('Unable to calculate UIF contribution.'),
        'pension_calculation_error': _('Unable to calculate pension contribution.'),
        
        # Rate engine errors
        'rate_engine_unavailable': _('Tax rate information is temporarily unavailable. Using fallback rates.'),
        'rate_update_failed': _('Failed to update tax rates. Using current rates.'),
        'rate_integrity_error': _('Tax rate data integrity check failed.'),
        
        # System errors
        'system_error': _('A system error occurred. Please try again later.'),
        'service_unavailable': _('Service is temporarily unavailable. Please try again later.'),
        'rate_limit_exceeded': _('Too many requests. Please wait before trying again.'),
        'timeout_error': _('Request timed out. Please try again.'),
    }
    
    @classmethod
    def handle_validation_error(cls, field: str, value: Any, error_type: str = 'invalid') -> ValidationError:
        """Handle input validation errors"""
        error_key = f'{error_type}_{field}' if f'{error_type}_{field}' in cls.ERROR_MESSAGES else 'invalid_amount'
        message = cls.ERROR_MESSAGES.get(error_key, cls.ERROR_MESSAGES['invalid_amount'])
        
        return ValidationError(
            message=message,
            error_code=f'VALIDATION_{error_type.upper()}_{field.upper()}',
            details={'field': field, 'value': str(value)}
        )
    
    @classmethod
    def handle_calculation_error(cls, calculation_type: str, original_error: Exception) -> CalculationError:
        """Handle calculation errors with context"""
        error_key = f'{calculation_type}_calculation_error'
        message = cls.ERROR_MESSAGES.get(error_key, cls.ERROR_MESSAGES['calculation_failed'])
        
        logger.error(f"Calculation error in {calculation_type}: {original_error}")
        
        return CalculationError(
            message=message,
            error_code=f'CALC_{calculation_type.upper()}_ERROR',
            details={
                'calculation_type': calculation_type,
                'original_error': str(original_error),
                'error_type': type(original_error).__name__
            }
        )
    
    @classmethod
    def handle_rate_engine_error(cls, operation: str, original_error: Exception) -> RateEngineError:
        """Handle rate engine errors"""
        message = cls.ERROR_MESSAGES.get('rate_engine_unavailable')
        
        logger.warning(f"Rate engine error in {operation}: {original_error}")
        
        return RateEngineError(
            message=message,
            error_code=f'RATE_ENGINE_{operation.upper()}_ERROR',
            details={
                'operation': operation,
                'original_error': str(original_error),
                'fallback_available': True
            }
        )
    
    @classmethod
    def to_json_response(cls, error: MoneyRiteError, status_code: int = 400) -> JsonResponse:
        """Convert error to JSON response"""
        response_data = {
            'error': True,
            'message': error.message,
            'error_code': error.error_code,
            'details': error.details
        }
        
        # Add user-friendly suggestions
        suggestions = cls._get_error_suggestions(error.error_code)
        if suggestions:
            response_data['suggestions'] = suggestions
        
        return JsonResponse(response_data, status=status_code)
    
    @classmethod
    def _get_error_suggestions(cls, error_code: str) -> Optional[list]:
        """Get user-friendly suggestions for error recovery"""
        suggestions_map = {
            'VALIDATION_INVALID_AMOUNT': [
                'Enter a positive number without currency symbols',
                'Use decimal point (.) for cents, e.g., 25000.50',
                'Ensure the amount is reasonable for South African salaries'
            ],
            'VALIDATION_AMOUNT_TOO_LARGE': [
                'Check if you entered the amount correctly',
                'Annual salaries should typically be under R10 million',
                'Monthly salaries should typically be under R1 million'
            ],
            'CALC_TAX_ERROR': [
                'Verify your annual income is entered correctly',
                'Check that your age category is selected',
                'Try refreshing the page and entering the information again'
            ],
            'RATE_ENGINE_GET_RATES_ERROR': [
                'The system is using backup tax rates',
                'Your calculations are still accurate',
                'Try again in a few minutes for updated rates'
            ]
        }
        
        return suggestions_map.get(error_code)


class InputValidator:
    """Input validation with detailed error reporting"""
    
    @staticmethod
    def validate_amount(value: Any, field_name: str = 'amount', 
                       min_value: Decimal = Decimal('0'), 
                       max_value: Decimal = Decimal('100000000')) -> Decimal:
        """Validate monetary amount"""
        try:
            if value is None or value == '':
                raise ErrorHandler.handle_validation_error(field_name, value, 'missing_required')
            
            # Convert to Decimal
            if isinstance(value, str):
                # Clean common formatting
                cleaned_value = value.replace(',', '').replace(' ', '').replace('R', '')
                decimal_value = Decimal(cleaned_value)
            else:
                decimal_value = Decimal(str(value))
            
            # Check bounds
            if decimal_value < min_value:
                raise ErrorHandler.handle_validation_error(field_name, value, 'negative')
            
            if decimal_value > max_value:
                raise ErrorHandler.handle_validation_error(field_name, value, 'too_large')
            
            return decimal_value
            
        except (InvalidOperation, ValueError) as e:
            raise ErrorHandler.handle_validation_error(field_name, value, 'invalid')
    
    @staticmethod
    def validate_percentage(value: Any, field_name: str = 'percentage',
                          min_value: Decimal = Decimal('0'),
                          max_value: Decimal = Decimal('100')) -> Decimal:
        """Validate percentage value"""
        try:
            if value is None or value == '':
                return Decimal('0')  # Default to 0 for optional percentages
            
            decimal_value = Decimal(str(value))
            
            if decimal_value < min_value or decimal_value > max_value:
                raise ErrorHandler.handle_validation_error(field_name, value, 'invalid_percentage')
            
            return decimal_value
            
        except (InvalidOperation, ValueError):
            raise ErrorHandler.handle_validation_error(field_name, value, 'invalid_percentage')
    
    @staticmethod
    def validate_age_category(value: str) -> str:
        """Validate age category"""
        valid_categories = ['under_65', '65_to_74', '75_plus']
        
        if value not in valid_categories:
            raise ErrorHandler.handle_validation_error('age_category', value, 'invalid')
        
        return value
    
    @staticmethod
    def validate_pay_period(value: str) -> str:
        """Validate pay period"""
        valid_periods = ['hourly', 'daily', 'weekly', 'monthly', 'annually']
        
        if value not in valid_periods:
            raise ErrorHandler.handle_validation_error('pay_period', value, 'invalid')
        
        return value


def safe_calculation(calculation_name: str):
    """Decorator for safe calculation execution with error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MoneyRiteError:
                # Re-raise our custom errors
                raise
            except Exception as e:
                # Convert unexpected errors to calculation errors
                raise ErrorHandler.handle_calculation_error(calculation_name, e)
        
        return wrapper
    return decorator


def graceful_fallback(fallback_value: Any = None, log_error: bool = True):
    """Decorator for graceful fallback on errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.warning(f"Function {func.__name__} failed, using fallback: {e}")
                return fallback_value
        
        return wrapper
    return decorator


# Utility functions for common error scenarios
def handle_api_error(error: Exception, operation: str) -> JsonResponse:
    """Handle API errors and return appropriate JSON response"""
    if isinstance(error, MoneyRiteError):
        return ErrorHandler.to_json_response(error)
    elif isinstance(error, (ValueError, InvalidOperation)):
        validation_error = ErrorHandler.handle_validation_error('input', str(error), 'invalid')
        return ErrorHandler.to_json_response(validation_error)
    else:
        system_error = MoneyRiteError(
            message=ErrorHandler.ERROR_MESSAGES['system_error'],
            error_code='SYSTEM_ERROR',
            details={'operation': operation, 'error_type': type(error).__name__}
        )
        logger.error(f"Unexpected error in {operation}: {error}")
        return ErrorHandler.to_json_response(system_error, status_code=500)
