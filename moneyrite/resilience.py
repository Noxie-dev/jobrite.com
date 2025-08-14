"""
Resilience Patterns for MoneyRite

Implements circuit breakers, rate limiting, graceful degradation,
and error handling patterns for reliable operation.
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5      # Failures before opening
    recovery_timeout: int = 60      # Seconds before trying half-open
    success_threshold: int = 3      # Successes to close from half-open
    timeout: float = 30.0           # Request timeout in seconds


class CircuitBreaker:
    """Circuit breaker implementation for external dependencies"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.cache_prefix = f"circuit_breaker:{name}"
        
    def _get_state(self) -> CircuitState:
        """Get current circuit state"""
        state_data = cache.get(f"{self.cache_prefix}:state")
        if not state_data:
            return CircuitState.CLOSED
        return CircuitState(state_data.get('state', 'closed'))
    
    def _set_state(self, state: CircuitState, **kwargs):
        """Set circuit state with metadata"""
        state_data = {
            'state': state.value,
            'timestamp': time.time(),
            **kwargs
        }
        cache.set(f"{self.cache_prefix}:state", state_data, 3600)  # 1 hour TTL
    
    def _get_failure_count(self) -> int:
        """Get current failure count"""
        return cache.get(f"{self.cache_prefix}:failures", 0)
    
    def _increment_failures(self):
        """Increment failure count"""
        current = self._get_failure_count()
        cache.set(f"{self.cache_prefix}:failures", current + 1, 3600)
    
    def _reset_failures(self):
        """Reset failure count"""
        cache.delete(f"{self.cache_prefix}:failures")
    
    def _get_success_count(self) -> int:
        """Get success count in half-open state"""
        return cache.get(f"{self.cache_prefix}:successes", 0)
    
    def _increment_successes(self):
        """Increment success count"""
        current = self._get_success_count()
        cache.set(f"{self.cache_prefix}:successes", current + 1, 300)  # 5 min TTL
    
    def _reset_successes(self):
        """Reset success count"""
        cache.delete(f"{self.cache_prefix}:successes")
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        state = self._get_state()
        
        # Check if circuit is open
        if state == CircuitState.OPEN:
            state_data = cache.get(f"{self.cache_prefix}:state", {})
            last_failure = state_data.get('timestamp', 0)
            
            # Check if recovery timeout has passed
            if time.time() - last_failure > self.config.recovery_timeout:
                self._set_state(CircuitState.HALF_OPEN)
                self._reset_successes()
                logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        # Execute the function
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Handle success
            self._handle_success(duration)
            return result
            
        except Exception as e:
            # Handle failure
            self._handle_failure(e)
            raise
    
    def _handle_success(self, duration: float):
        """Handle successful execution"""
        state = self._get_state()
        
        if state == CircuitState.HALF_OPEN:
            # Increment success count
            self._increment_successes()
            success_count = self._get_success_count()
            
            if success_count >= self.config.success_threshold:
                # Close the circuit
                self._set_state(CircuitState.CLOSED)
                self._reset_failures()
                self._reset_successes()
                logger.info(f"Circuit breaker {self.name} CLOSED after {success_count} successes")
        
        elif state == CircuitState.CLOSED:
            # Reset failure count on success
            self._reset_failures()
    
    def _handle_failure(self, exception: Exception):
        """Handle failed execution"""
        state = self._get_state()
        
        if state == CircuitState.HALF_OPEN:
            # Failure in half-open state - go back to open
            self._set_state(CircuitState.OPEN, last_error=str(exception))
            self._reset_successes()
            logger.warning(f"Circuit breaker {self.name} back to OPEN due to failure: {exception}")
        
        elif state == CircuitState.CLOSED:
            # Increment failure count
            self._increment_failures()
            failure_count = self._get_failure_count()
            
            if failure_count >= self.config.failure_threshold:
                # Open the circuit
                self._set_state(CircuitState.OPEN, last_error=str(exception))
                logger.error(f"Circuit breaker {self.name} OPENED after {failure_count} failures")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        state = self._get_state()
        state_data = cache.get(f"{self.cache_prefix}:state", {})
        
        return {
            'name': self.name,
            'state': state.value,
            'failure_count': self._get_failure_count(),
            'success_count': self._get_success_count() if state == CircuitState.HALF_OPEN else 0,
            'last_state_change': state_data.get('timestamp'),
            'last_error': state_data.get('last_error'),
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold
            }
        }


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass


class RateLimiter:
    """Rate limiter implementation"""
    
    def __init__(self, name: str, max_requests: int, window_seconds: int = 60):
        self.name = name
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cache_key = f"rate_limit:{name}"
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed"""
        key = f"{self.cache_key}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Get current request count
        request_data = cache.get(key, {})
        
        # Clean old requests
        cleaned_requests = {
            timestamp: count for timestamp, count in request_data.items()
            if int(timestamp) > window_start
        }
        
        # Count total requests in window
        total_requests = sum(cleaned_requests.values())
        
        if total_requests >= self.max_requests:
            return False
        
        # Add current request
        current_second = str(current_time)
        cleaned_requests[current_second] = cleaned_requests.get(current_second, 0) + 1
        
        # Save updated data
        cache.set(key, cleaned_requests, self.window_seconds + 60)
        
        return True
    
    def get_status(self, identifier: str) -> Dict[str, Any]:
        """Get rate limit status for identifier"""
        key = f"{self.cache_key}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        request_data = cache.get(key, {})
        
        # Count requests in current window
        current_requests = sum(
            count for timestamp, count in request_data.items()
            if int(timestamp) > window_start
        )
        
        return {
            'identifier': identifier,
            'current_requests': current_requests,
            'max_requests': self.max_requests,
            'window_seconds': self.window_seconds,
            'remaining_requests': max(0, self.max_requests - current_requests),
            'reset_time': current_time + self.window_seconds
        }


def circuit_breaker(name: str, config: CircuitBreakerConfig = None):
    """Decorator for circuit breaker protection"""
    breaker = CircuitBreaker(name, config)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        # Attach breaker to function for status checking
        wrapper._circuit_breaker = breaker
        return wrapper
    
    return decorator


def rate_limit(name: str, max_requests: int, window_seconds: int = 60, 
               key_func: Callable = None):
    """Decorator for rate limiting"""
    limiter = RateLimiter(name, max_requests, window_seconds)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine rate limit key
            if key_func:
                identifier = key_func(*args, **kwargs)
            else:
                # Default to user ID if available
                request = args[0] if args and hasattr(args[0], 'user') else None
                if request and hasattr(request.user, 'id'):
                    identifier = str(request.user.id)
                else:
                    identifier = 'anonymous'
            
            if not limiter.is_allowed(identifier):
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': window_seconds
                }, status=429)
            
            return func(*args, **kwargs)
        
        # Attach limiter to function for status checking
        wrapper._rate_limiter = limiter
        return wrapper
    
    return decorator


class GracefulDegradation:
    """Graceful degradation patterns"""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable, 
                     fallback_exceptions: tuple = (Exception,)):
        """Execute primary function with fallback on failure"""
        def wrapper(*args, **kwargs):
            try:
                return primary_func(*args, **kwargs)
            except fallback_exceptions as e:
                logger.warning(f"Primary function failed, using fallback: {e}")
                return fallback_func(*args, **kwargs)
        
        return wrapper
    
    @staticmethod
    def with_timeout(timeout_seconds: float):
        """Add timeout to function execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds}s")
                
                # Set timeout
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout_seconds))
                
                try:
                    result = func(*args, **kwargs)
                    signal.alarm(0)  # Cancel timeout
                    return result
                finally:
                    signal.signal(signal.SIGALRM, old_handler)
            
            return wrapper
        return decorator


# Global circuit breakers for common external dependencies
external_api_breaker = CircuitBreaker("external_api", CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30,
    success_threshold=2
))

database_breaker = CircuitBreaker("database", CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60,
    success_threshold=3
))

# Global rate limiters
calculation_rate_limiter = RateLimiter("calculations", max_requests=100, window_seconds=60)
api_rate_limiter = RateLimiter("api", max_requests=1000, window_seconds=60)
