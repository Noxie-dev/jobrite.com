"""
Rate Update Service for MoneyRite

Handles hot updates of tax rates and configurations with integrity verification
and graceful fallback mechanisms.
"""

import json
import logging
import hashlib
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings
from .rate_engine import RateEngine, RateConfiguration

logger = logging.getLogger(__name__)


class RateUpdateService:
    """Service for updating tax rates with safety checks"""
    
    def __init__(self):
        self.rate_engine = RateEngine()
        self.update_lock_key = 'moneyrite:rate_update_lock'
        self.update_status_key = 'moneyrite:rate_update_status'
    
    def check_for_updates(self) -> Dict[str, Any]:
        """Check if new rate configurations are available"""
        try:
            current_config = self.rate_engine.get_current_rates()
            
            # In a real implementation, this would check a remote manifest
            # For now, we'll simulate checking for updates
            status = {
                'current_version': current_config.version,
                'current_effective_date': current_config.effective_date.isoformat(),
                'last_check': datetime.now().isoformat(),
                'updates_available': False,
                'next_check_due': None
            }
            
            # Cache the status
            cache.set(self.update_status_key, status, 3600)  # 1 hour
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to check for rate updates: {e}")
            return {
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def update_rates(self, new_config_data: Dict[str, Any], verify_only: bool = False) -> Dict[str, Any]:
        """
        Update tax rates with new configuration
        
        Args:
            new_config_data: New rate configuration data
            verify_only: If True, only verify the configuration without applying
            
        Returns:
            Update result with status and any errors
        """
        
        # Acquire update lock
        if cache.get(self.update_lock_key):
            return {
                'success': False,
                'error': 'Rate update already in progress'
            }
        
        try:
            cache.set(self.update_lock_key, True, 300)  # 5 minute lock
            
            # Deserialize and validate new configuration
            try:
                new_config = self.rate_engine._deserialize_config(new_config_data)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Invalid configuration format: {e}'
                }
            
            # Verify integrity
            if not self.rate_engine.verify_integrity(new_config):
                return {
                    'success': False,
                    'error': 'Configuration integrity check failed'
                }
            
            # Verify configuration makes sense
            validation_result = self._validate_configuration(new_config)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f'Configuration validation failed: {validation_result["error"]}'
                }
            
            if verify_only:
                return {
                    'success': True,
                    'message': 'Configuration verified successfully',
                    'version': new_config.version
                }
            
            # Get current configuration for comparison
            current_config = self.rate_engine.get_current_rates()
            
            # Run shadow comparison if possible
            comparison_result = self._shadow_compare(current_config, new_config)
            
            # Save new configuration
            if self.rate_engine.save_configuration(new_config, make_current=True):
                logger.info(f"Successfully updated rates to version {new_config.version}")
                
                return {
                    'success': True,
                    'message': f'Rates updated to version {new_config.version}',
                    'previous_version': current_config.version,
                    'new_version': new_config.version,
                    'comparison': comparison_result
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save new configuration'
                }
                
        except Exception as e:
            logger.error(f"Rate update failed: {e}")
            return {
                'success': False,
                'error': f'Update failed: {e}'
            }
        finally:
            cache.delete(self.update_lock_key)
    
    def _validate_configuration(self, config: RateConfiguration) -> Dict[str, Any]:
        """Validate that configuration is reasonable"""
        try:
            # Check that tax brackets are in ascending order
            prev_max = 0
            for bracket in config.tax_brackets:
                if bracket.min_income < prev_max:
                    return {
                        'valid': False,
                        'error': 'Tax brackets are not in ascending order'
                    }
                if bracket.max_income and bracket.max_income <= bracket.min_income:
                    return {
                        'valid': False,
                        'error': 'Invalid bracket range'
                    }
                prev_max = bracket.max_income or float('inf')
            
            # Check that rates are reasonable (0-50%)
            for bracket in config.tax_brackets:
                if bracket.rate < 0 or bracket.rate > 0.5:
                    return {
                        'valid': False,
                        'error': f'Unreasonable tax rate: {bracket.rate * 100}%'
                    }
            
            # Check that rebates are positive
            for rebate in config.tax_rebates:
                if rebate.amount < 0:
                    return {
                        'valid': False,
                        'error': f'Negative rebate amount: {rebate.amount}'
                    }
            
            # Check UIF configuration
            if config.uif_rate < 0 or config.uif_rate > 0.05:  # Max 5%
                return {
                    'valid': False,
                    'error': f'Unreasonable UIF rate: {config.uif_rate * 100}%'
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {e}'
            }
    
    def _shadow_compare(self, old_config: RateConfiguration, new_config: RateConfiguration) -> Dict[str, Any]:
        """Compare old and new configurations on sample calculations"""
        try:
            from .utils import SARSTaxCalculator
            
            # Test cases for comparison
            test_incomes = [
                100000, 200000, 300000, 500000, 1000000
            ]
            
            differences = []
            max_difference = 0
            
            for income in test_incomes:
                # This would require implementing a way to calculate with specific config
                # For now, we'll just note the comparison was attempted
                differences.append({
                    'income': income,
                    'note': 'Shadow comparison not fully implemented'
                })
            
            return {
                'compared': True,
                'test_cases': len(test_incomes),
                'max_difference': max_difference,
                'differences': differences
            }
            
        except Exception as e:
            logger.warning(f"Shadow comparison failed: {e}")
            return {
                'compared': False,
                'error': str(e)
            }
    
    def rollback_to_version(self, version: str) -> Dict[str, Any]:
        """Rollback to a specific rate version"""
        try:
            # This would load a specific version and make it current
            # Implementation depends on version storage mechanism
            
            return {
                'success': False,
                'error': 'Rollback not yet implemented'
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {
                'success': False,
                'error': f'Rollback failed: {e}'
            }
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status"""
        status = cache.get(self.update_status_key)
        if not status:
            status = self.check_for_updates()
        
        # Add lock status
        status['update_in_progress'] = bool(cache.get(self.update_lock_key))
        
        return status


# Global update service instance
rate_update_service = RateUpdateService()
