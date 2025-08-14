"""
Observability Infrastructure for MoneyRite

Implements OpenTelemetry instrumentation for traces, metrics, and logs
with SLO monitoring and alerting capabilities.
"""

import time
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager
from django.conf import settings

# OpenTelemetry imports with fallback
try:
    from opentelemetry import trace, metrics
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.metrics import Counter, Histogram, Gauge
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

logger = logging.getLogger(__name__)


class MoneyRiteObservability:
    """Central observability manager for MoneyRite"""
    
    def __init__(self):
        self.initialized = False
        self.tracer = None
        self.meter = None
        self.metrics = {}
        
        if OTEL_AVAILABLE:
            self._initialize_otel()
        else:
            logger.warning("OpenTelemetry not available, using fallback observability")
    
    def _initialize_otel(self):
        """Initialize OpenTelemetry instrumentation"""
        try:
            # Create resource
            resource = Resource.create({
                "service.name": "moneyrite",
                "service.version": "1.0.0",
                "service.namespace": "jobrite"
            })
            
            # Initialize tracing
            trace.set_tracer_provider(TracerProvider(resource=resource))
            self.tracer = trace.get_tracer(__name__)
            
            # Initialize metrics
            metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(),
                export_interval_millis=30000  # 30 seconds
            )
            metrics.set_meter_provider(MeterProvider(
                resource=resource,
                metric_readers=[metric_reader]
            ))
            self.meter = metrics.get_meter(__name__)
            
            # Create metrics
            self._create_metrics()
            
            # Add span processor for traces
            span_processor = BatchSpanProcessor(OTLPSpanExporter())
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            self.initialized = True
            logger.info("OpenTelemetry initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
            self.initialized = False
    
    def _create_metrics(self):
        """Create application-specific metrics"""
        if not self.meter:
            return
        
        # Calculation metrics
        self.metrics['calculation_requests'] = self.meter.create_counter(
            name="moneyrite_calculation_requests_total",
            description="Total number of calculation requests",
            unit="1"
        )
        
        self.metrics['calculation_duration'] = self.meter.create_histogram(
            name="moneyrite_calculation_duration_seconds",
            description="Duration of calculation requests",
            unit="s"
        )
        
        self.metrics['calculation_errors'] = self.meter.create_counter(
            name="moneyrite_calculation_errors_total",
            description="Total number of calculation errors",
            unit="1"
        )
        
        # Accuracy metrics
        self.metrics['accuracy_checks'] = self.meter.create_counter(
            name="moneyrite_accuracy_checks_total",
            description="Total number of accuracy checks performed",
            unit="1"
        )
        
        self.metrics['accuracy_failures'] = self.meter.create_counter(
            name="moneyrite_accuracy_failures_total",
            description="Total number of accuracy check failures",
            unit="1"
        )
        
        # Rate engine metrics
        self.metrics['rate_engine_requests'] = self.meter.create_counter(
            name="moneyrite_rate_engine_requests_total",
            description="Total number of rate engine requests",
            unit="1"
        )
        
        self.metrics['rate_updates'] = self.meter.create_counter(
            name="moneyrite_rate_updates_total",
            description="Total number of rate updates",
            unit="1"
        )
        
        # SLO metrics
        self.metrics['slo_availability'] = self.meter.create_gauge(
            name="moneyrite_slo_availability_ratio",
            description="Current availability SLO ratio",
            unit="1"
        )
        
        self.metrics['slo_latency'] = self.meter.create_gauge(
            name="moneyrite_slo_latency_p95_seconds",
            description="Current p95 latency SLO",
            unit="s"
        )
    
    def trace_calculation(self, calculation_type: str):
        """Decorator for tracing calculations"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._trace_function(func, calculation_type, *args, **kwargs)
            return wrapper
        return decorator
    
    def _trace_function(self, func, operation_name: str, *args, **kwargs):
        """Trace a function execution"""
        start_time = time.time()
        
        # Increment request counter
        if 'calculation_requests' in self.metrics:
            self.metrics['calculation_requests'].add(1, {"operation": operation_name})
        
        if self.tracer:
            with self.tracer.start_as_current_span(f"moneyrite.{operation_name}") as span:
                try:
                    # Add span attributes
                    span.set_attribute("operation.name", operation_name)
                    span.set_attribute("operation.type", "calculation")
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Mark as successful
                    span.set_status(Status(StatusCode.OK))
                    
                    # Record duration
                    duration = time.time() - start_time
                    if 'calculation_duration' in self.metrics:
                        self.metrics['calculation_duration'].record(duration, {"operation": operation_name})
                    
                    return result
                    
                except Exception as e:
                    # Record error
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    
                    if 'calculation_errors' in self.metrics:
                        self.metrics['calculation_errors'].add(1, {
                            "operation": operation_name,
                            "error_type": type(e).__name__
                        })
                    
                    raise
        else:
            # Fallback without tracing
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Calculation {operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                logger.error(f"Calculation {operation_name} failed: {e}")
                raise
    
    @contextmanager
    def trace_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Context manager for creating custom spans"""
        if self.tracer:
            with self.tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                yield span
        else:
            # Fallback - just yield None
            yield None
    
    def record_accuracy_check(self, test_name: str, passed: bool, expected: Decimal, actual: Decimal):
        """Record accuracy check results"""
        if 'accuracy_checks' in self.metrics:
            self.metrics['accuracy_checks'].add(1, {"test": test_name})
        
        if not passed and 'accuracy_failures' in self.metrics:
            self.metrics['accuracy_failures'].add(1, {"test": test_name})
            
            # Log accuracy failure
            difference = abs(actual - expected)
            logger.error(f"Accuracy check failed: {test_name}, expected {expected}, got {actual}, diff {difference}")
    
    def record_rate_engine_access(self, operation: str, success: bool = True):
        """Record rate engine access"""
        if 'rate_engine_requests' in self.metrics:
            self.metrics['rate_engine_requests'].add(1, {
                "operation": operation,
                "success": str(success)
            })
    
    def record_rate_update(self, version: str, success: bool = True):
        """Record rate update"""
        if 'rate_updates' in self.metrics:
            self.metrics['rate_updates'].add(1, {
                "version": version,
                "success": str(success)
            })
        
        logger.info(f"Rate update recorded: version={version}, success={success}")
    
    def update_slo_metrics(self, availability_ratio: float, latency_p95: float):
        """Update SLO metrics"""
        if 'slo_availability' in self.metrics:
            self.metrics['slo_availability'].set(availability_ratio)
        
        if 'slo_latency' in self.metrics:
            self.metrics['slo_latency'].set(latency_p95)


class SLOMonitor:
    """Service Level Objective monitoring"""
    
    def __init__(self, observability: MoneyRiteObservability):
        self.observability = observability
        self.slos = {
            'availability': {
                'target': 0.999,  # 99.9%
                'current': 1.0,
                'error_budget': 0.001
            },
            'latency_p95': {
                'target': 0.3,  # 300ms
                'current': 0.0,
                'error_budget': 0.1  # 100ms buffer
            },
            'accuracy': {
                'target': 0.9999,  # 99.99%
                'current': 1.0,
                'error_budget': 0.0001
            }
        }
    
    def check_slos(self) -> Dict[str, Any]:
        """Check current SLO status"""
        status = {}
        
        for slo_name, slo_config in self.slos.items():
            current = slo_config['current']
            target = slo_config['target']
            error_budget = slo_config['error_budget']
            
            # Calculate error budget burn rate
            if slo_name == 'latency_p95':
                # For latency, lower is better
                burn_rate = max(0, (current - target) / error_budget) if error_budget > 0 else 0
            else:
                # For availability and accuracy, higher is better
                burn_rate = max(0, (target - current) / error_budget) if error_budget > 0 else 0
            
            status[slo_name] = {
                'current': current,
                'target': target,
                'error_budget_remaining': max(0, 1 - burn_rate),
                'status': 'OK' if burn_rate < 0.5 else 'WARNING' if burn_rate < 1.0 else 'CRITICAL'
            }
        
        return status
    
    def should_alert(self, slo_name: str) -> bool:
        """Check if SLO breach should trigger alert"""
        if slo_name not in self.slos:
            return False
        
        status = self.check_slos()
        return status[slo_name]['status'] in ['WARNING', 'CRITICAL']


# Global observability instance
observability = MoneyRiteObservability()
slo_monitor = SLOMonitor(observability)
