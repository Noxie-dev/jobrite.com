"""
MoneyRite Observability Middleware

Automatic request tracing and metrics collection for Django views.
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .observability import observability, slo_monitor

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(MiddlewareMixin):
    """Middleware for automatic request tracing and metrics"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Start request tracing"""
        request._start_time = time.time()
        request._span = None
        
        if observability and observability.tracer:
            # Create span for the request
            span_name = f"{request.method} {request.path}"
            request._span = observability.tracer.start_span(span_name)
            
            # Add request attributes
            request._span.set_attribute("http.method", request.method)
            request._span.set_attribute("http.url", request.build_absolute_uri())
            request._span.set_attribute("http.scheme", request.scheme)
            request._span.set_attribute("http.host", request.get_host())
            request._span.set_attribute("http.target", request.get_full_path())
            
            if request.user and hasattr(request.user, 'id'):
                request._span.set_attribute("user.id", str(request.user.id))
    
    def process_response(self, request, response):
        """Complete request tracing and record metrics"""
        duration = time.time() - getattr(request, '_start_time', time.time())
        
        # Complete span if it exists
        if hasattr(request, '_span') and request._span:
            request._span.set_attribute("http.status_code", response.status_code)
            request._span.set_attribute("http.response_size", len(response.content))
            
            if response.status_code >= 400:
                request._span.set_status(
                    observability.trace.Status(
                        observability.trace.StatusCode.ERROR,
                        f"HTTP {response.status_code}"
                    )
                )
            
            request._span.end()
        
        # Record metrics
        if observability and 'calculation_duration' in observability.metrics:
            # Identify MoneyRite calculation endpoints
            if '/moneyrite/' in request.path:
                operation = self._get_operation_name(request.path)
                observability.metrics['calculation_duration'].record(
                    duration, 
                    {"operation": operation, "status_code": str(response.status_code)}
                )
        
        # Update SLO metrics
        self._update_slo_metrics(request, response, duration)
        
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions in request processing"""
        if hasattr(request, '_span') and request._span:
            request._span.record_exception(exception)
            request._span.set_status(
                observability.trace.Status(
                    observability.trace.StatusCode.ERROR,
                    str(exception)
                )
            )
            request._span.end()
        
        # Record error metrics
        if observability and 'calculation_errors' in observability.metrics:
            if '/moneyrite/' in request.path:
                operation = self._get_operation_name(request.path)
                observability.metrics['calculation_errors'].add(1, {
                    "operation": operation,
                    "error_type": type(exception).__name__
                })
        
        logger.error(f"Request exception: {request.path} - {exception}")
    
    def _get_operation_name(self, path: str) -> str:
        """Extract operation name from request path"""
        if 'calculate_salary_api' in path:
            return 'salary_calculation'
        elif 'calculate_budget_api' in path:
            return 'budget_calculation'
        elif 'calculate_debt_api' in path:
            return 'debt_calculation'
        elif 'salary_calculator' in path:
            return 'salary_calculator_page'
        elif 'dashboard' in path:
            return 'dashboard'
        else:
            return 'unknown'
    
    def _update_slo_metrics(self, request, response, duration):
        """Update SLO metrics based on request"""
        if not observability:
            return
        
        # Update availability SLO
        if response.status_code < 500:
            # Request was successful from availability perspective
            pass  # Would update running average here
        
        # Update latency SLO
        if '/moneyrite/' in request.path and 'api' in request.path:
            # This is a calculation API request
            if duration > 0.3:  # 300ms threshold
                logger.warning(f"Slow calculation request: {request.path} took {duration:.3f}s")


class HealthCheckMiddleware(MiddlewareMixin):
    """Middleware for health checks and SLO monitoring"""
    
    def process_request(self, request):
        """Handle health check requests"""
        if request.path == '/health':
            return self._health_check_response()
        elif request.path == '/health/slo':
            return self._slo_status_response()
        elif request.path == '/health/ready':
            return self._readiness_check_response()
    
    def _health_check_response(self):
        """Basic health check"""
        try:
            # Basic health checks
            health_status = {
                'status': 'healthy',
                'timestamp': time.time(),
                'version': '1.0.0',
                'checks': {
                    'database': self._check_database(),
                    'cache': self._check_cache(),
                    'rate_engine': self._check_rate_engine()
                }
            }
            
            # Overall status
            if all(check['status'] == 'ok' for check in health_status['checks'].values()):
                status_code = 200
            else:
                status_code = 503
                health_status['status'] = 'unhealthy'
            
            return JsonResponse(health_status, status=status_code)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    def _slo_status_response(self):
        """SLO status check"""
        try:
            slo_status = slo_monitor.check_slos()
            
            # Determine overall status
            critical_slos = [slo for slo, status in slo_status.items() 
                           if status['status'] == 'CRITICAL']
            
            if critical_slos:
                overall_status = 'CRITICAL'
                status_code = 503
            elif any(status['status'] == 'WARNING' for status in slo_status.values()):
                overall_status = 'WARNING'
                status_code = 200
            else:
                overall_status = 'OK'
                status_code = 200
            
            return JsonResponse({
                'overall_status': overall_status,
                'slos': slo_status,
                'timestamp': time.time()
            }, status=status_code)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    def _readiness_check_response(self):
        """Readiness check for deployment"""
        try:
            ready_checks = {
                'rate_engine_initialized': self._check_rate_engine()['status'] == 'ok',
                'observability_initialized': observability.initialized if observability else False,
                'database_ready': self._check_database()['status'] == 'ok'
            }
            
            if all(ready_checks.values()):
                return JsonResponse({
                    'status': 'ready',
                    'checks': ready_checks
                }, status=200)
            else:
                return JsonResponse({
                    'status': 'not_ready',
                    'checks': ready_checks
                }, status=503)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    
    def _check_database(self):
        """Check database connectivity"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {'status': 'ok', 'message': 'Database connection successful'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _check_cache(self):
        """Check cache connectivity"""
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 30)
            result = cache.get('health_check')
            if result == 'ok':
                return {'status': 'ok', 'message': 'Cache working'}
            else:
                return {'status': 'error', 'message': 'Cache not working'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _check_rate_engine(self):
        """Check rate engine status"""
        try:
            from .rate_engine import rate_engine
            config = rate_engine.get_current_rates()
            return {
                'status': 'ok', 
                'message': f'Rate engine working, version {config.version}'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
