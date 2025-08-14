"""
Feature Flags and Release Safety for MoneyRite

Implements feature flags, canary deployments, shadow mode testing,
and instant rollback capabilities for safe releases.
"""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class RolloutStrategy(Enum):
    """Feature rollout strategies"""
    OFF = "off"                    # Feature disabled for all users
    ON = "on"                      # Feature enabled for all users
    PERCENTAGE = "percentage"      # Percentage-based rollout
    USER_LIST = "user_list"        # Specific user list
    CANARY = "canary"             # Canary deployment
    SHADOW = "shadow"             # Shadow mode (run but don't use results)


@dataclass
class FeatureFlag:
    """Feature flag configuration"""
    name: str
    description: str
    strategy: RolloutStrategy
    enabled: bool = False
    
    # Rollout configuration
    percentage: float = 0.0        # For percentage rollout (0-100)
    user_ids: List[int] = None     # For user list rollout
    user_groups: List[str] = None  # For group-based rollout
    
    # Canary configuration
    canary_percentage: float = 5.0  # Canary user percentage
    canary_success_threshold: float = 99.0  # Success rate to proceed
    
    # Shadow mode configuration
    shadow_percentage: float = 10.0  # Shadow mode user percentage
    
    # Metadata
    created_by: str = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.user_ids is None:
            self.user_ids = []
        if self.user_groups is None:
            self.user_groups = []


class FeatureFlagManager:
    """Manages feature flags and rollout strategies"""
    
    CACHE_PREFIX = "feature_flag"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self._load_flags()
    
    def _load_flags(self):
        """Load feature flags from cache/storage"""
        try:
            cached_flags = cache.get(f"{self.CACHE_PREFIX}:all")
            if cached_flags:
                for flag_data in cached_flags:
                    flag = FeatureFlag(**flag_data)
                    self.flags[flag.name] = flag
            else:
                # Initialize with default flags
                self._initialize_default_flags()
        except Exception as e:
            logger.error(f"Failed to load feature flags: {e}")
            self._initialize_default_flags()
    
    def _initialize_default_flags(self):
        """Initialize default feature flags for MoneyRite"""
        default_flags = [
            FeatureFlag(
                name="new_tax_engine",
                description="Use new versioned tax calculation engine",
                strategy=RolloutStrategy.CANARY,
                enabled=True,
                canary_percentage=5.0
            ),
            FeatureFlag(
                name="enhanced_error_handling",
                description="Enhanced error handling and user messages",
                strategy=RolloutStrategy.PERCENTAGE,
                enabled=True,
                percentage=50.0
            ),
            FeatureFlag(
                name="observability_tracing",
                description="OpenTelemetry tracing and metrics",
                strategy=RolloutStrategy.ON,
                enabled=True
            ),
            FeatureFlag(
                name="circuit_breakers",
                description="Circuit breaker protection for external services",
                strategy=RolloutStrategy.ON,
                enabled=True
            ),
            FeatureFlag(
                name="shadow_calculation_comparison",
                description="Shadow mode calculation comparison",
                strategy=RolloutStrategy.SHADOW,
                enabled=True,
                shadow_percentage=10.0
            )
        ]
        
        for flag in default_flags:
            self.flags[flag.name] = flag
        
        self._save_flags()
    
    def _save_flags(self):
        """Save feature flags to cache"""
        try:
            flag_data = [asdict(flag) for flag in self.flags.values()]
            cache.set(f"{self.CACHE_PREFIX}:all", flag_data, self.CACHE_TIMEOUT)
        except Exception as e:
            logger.error(f"Failed to save feature flags: {e}")
    
    def is_enabled(self, flag_name: str, user: User = None, context: Dict[str, Any] = None) -> bool:
        """Check if feature flag is enabled for user/context"""
        flag = self.flags.get(flag_name)
        if not flag or not flag.enabled:
            return False
        
        return self._evaluate_flag(flag, user, context)
    
    def _evaluate_flag(self, flag: FeatureFlag, user: User = None, context: Dict[str, Any] = None) -> bool:
        """Evaluate feature flag based on strategy"""
        context = context or {}
        
        if flag.strategy == RolloutStrategy.OFF:
            return False
        
        elif flag.strategy == RolloutStrategy.ON:
            return True
        
        elif flag.strategy == RolloutStrategy.PERCENTAGE:
            return self._percentage_rollout(flag, user)
        
        elif flag.strategy == RolloutStrategy.USER_LIST:
            return self._user_list_rollout(flag, user)
        
        elif flag.strategy == RolloutStrategy.CANARY:
            return self._canary_rollout(flag, user)
        
        elif flag.strategy == RolloutStrategy.SHADOW:
            # Shadow mode always returns False for actual usage
            # but tracks that it should run in shadow
            self._track_shadow_user(flag, user)
            return False
        
        return False
    
    def _percentage_rollout(self, flag: FeatureFlag, user: User = None) -> bool:
        """Percentage-based rollout"""
        if not user:
            return False
        
        # Use consistent hash of user ID and flag name
        hash_input = f"{user.id}:{flag.name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        user_percentage = (hash_value % 100) + 1
        
        return user_percentage <= flag.percentage
    
    def _user_list_rollout(self, flag: FeatureFlag, user: User = None) -> bool:
        """User list rollout"""
        if not user:
            return False
        
        return user.id in flag.user_ids
    
    def _canary_rollout(self, flag: FeatureFlag, user: User = None) -> bool:
        """Canary deployment rollout"""
        if not user:
            return False
        
        # Check if user is in canary group
        hash_input = f"{user.id}:canary:{flag.name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        user_percentage = (hash_value % 100) + 1
        
        is_canary_user = user_percentage <= flag.canary_percentage
        
        if is_canary_user:
            # Check canary success metrics
            success_rate = self._get_canary_success_rate(flag.name)
            if success_rate >= flag.canary_success_threshold:
                return True
            else:
                logger.warning(f"Canary {flag.name} success rate {success_rate}% below threshold {flag.canary_success_threshold}%")
                return False
        
        return False
    
    def _track_shadow_user(self, flag: FeatureFlag, user: User = None):
        """Track user for shadow mode testing"""
        if not user:
            return
        
        hash_input = f"{user.id}:shadow:{flag.name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        user_percentage = (hash_value % 100) + 1
        
        if user_percentage <= flag.shadow_percentage:
            # Mark user for shadow testing
            cache.set(f"shadow:{flag.name}:{user.id}", True, 3600)
    
    def should_run_shadow(self, flag_name: str, user: User = None) -> bool:
        """Check if should run shadow mode for user"""
        if not user:
            return False
        
        return bool(cache.get(f"shadow:{flag_name}:{user.id}"))
    
    def _get_canary_success_rate(self, flag_name: str) -> float:
        """Get canary success rate from metrics"""
        # This would integrate with observability metrics
        # For now, return a simulated success rate
        success_data = cache.get(f"canary_success:{flag_name}")
        if success_data:
            return success_data.get('success_rate', 100.0)
        return 100.0  # Default to 100% if no data
    
    def record_canary_result(self, flag_name: str, success: bool, user_id: int = None):
        """Record canary deployment result"""
        key = f"canary_success:{flag_name}"
        data = cache.get(key, {'total': 0, 'successes': 0})
        
        data['total'] += 1
        if success:
            data['successes'] += 1
        
        data['success_rate'] = (data['successes'] / data['total']) * 100
        
        cache.set(key, data, 3600)  # 1 hour
        
        logger.info(f"Canary result for {flag_name}: success={success}, rate={data['success_rate']:.1f}%")
    
    def update_flag(self, flag_name: str, **kwargs) -> bool:
        """Update feature flag configuration"""
        if flag_name not in self.flags:
            return False
        
        flag = self.flags[flag_name]
        
        # Update allowed fields
        allowed_fields = ['enabled', 'strategy', 'percentage', 'user_ids', 'canary_percentage']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(flag, field, value)
        
        self._save_flags()
        logger.info(f"Updated feature flag {flag_name}: {kwargs}")
        return True
    
    def get_flag_status(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """Get feature flag status and metrics"""
        flag = self.flags.get(flag_name)
        if not flag:
            return None
        
        status = asdict(flag)
        
        # Add runtime metrics
        if flag.strategy == RolloutStrategy.CANARY:
            status['canary_metrics'] = {
                'success_rate': self._get_canary_success_rate(flag_name)
            }
        
        return status
    
    def list_flags(self) -> Dict[str, Dict[str, Any]]:
        """List all feature flags with their status"""
        return {name: self.get_flag_status(name) for name in self.flags.keys()}
    
    def emergency_disable(self, flag_name: str, reason: str = "Emergency disable") -> bool:
        """Emergency disable feature flag"""
        if flag_name not in self.flags:
            return False
        
        self.flags[flag_name].enabled = False
        self.flags[flag_name].strategy = RolloutStrategy.OFF
        self._save_flags()
        
        logger.critical(f"Emergency disabled feature flag {flag_name}: {reason}")
        return True


# Global feature flag manager
feature_flags = FeatureFlagManager()


def feature_flag(flag_name: str, default: bool = False):
    """Decorator for feature flag protection"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Try to get user from request
            user = None
            if args and hasattr(args[0], 'user'):
                user = args[0].user
            
            if feature_flags.is_enabled(flag_name, user):
                return func(*args, **kwargs)
            elif default:
                return func(*args, **kwargs)
            else:
                # Feature disabled - return appropriate response
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'Feature not available',
                    'feature': flag_name
                }, status=404)
        
        return wrapper
    return decorator


def shadow_mode(flag_name: str, shadow_func: Callable):
    """Decorator for shadow mode testing"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Execute primary function
            result = func(*args, **kwargs)
            
            # Check if should run shadow
            user = None
            if args and hasattr(args[0], 'user'):
                user = args[0].user
            
            if feature_flags.should_run_shadow(flag_name, user):
                try:
                    # Run shadow function
                    shadow_result = shadow_func(*args, **kwargs)
                    
                    # Compare results (implement comparison logic)
                    comparison = _compare_results(result, shadow_result)
                    
                    # Log comparison
                    logger.info(f"Shadow mode comparison for {flag_name}: {comparison}")
                    
                except Exception as e:
                    logger.error(f"Shadow mode failed for {flag_name}: {e}")
            
            return result
        
        return wrapper
    return decorator


def _compare_results(primary: Any, shadow: Any) -> Dict[str, Any]:
    """Compare primary and shadow results"""
    try:
        if primary == shadow:
            return {'match': True, 'difference': None}
        else:
            return {
                'match': False,
                'primary': str(primary)[:100],  # Truncate for logging
                'shadow': str(shadow)[:100],
                'difference': 'Values differ'
            }
    except Exception as e:
        return {'match': False, 'error': str(e)}
