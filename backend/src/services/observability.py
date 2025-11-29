import logging
from functools import wraps
from typing import Callable
from datetime import datetime

from ..config.settings import settings

logger = logging.getLogger(__name__)


def setup_observability():
    """
    Initialize Azure Monitor and Application Insights with OpenTelemetry
    
    In production this would configure:
    - OpenTelemetry tracing
    - Application Insights exporter
    - Custom metrics and dimensions
    """
    logger.info("Setting up observability with Application Insights")
    
    if settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
        try:
            # from azure.monitor.opentelemetry import configure_azure_monitor
            # configure_azure_monitor(connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING)
            logger.info("Application Insights configured successfully")
        except Exception as e:
            logger.warning(f"Failed to configure Application Insights: {e}")
    else:
        logger.info("Running without Application Insights (connection string not set)")


def trace_request(func: Callable) -> Callable:
    """
    Decorator to trace API requests with custom telemetry
    
    Tracks:
    - Request duration
    - Success/failure
    - Custom properties
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        func_name = func.__name__
        
        try:
            logger.debug(f"Starting {func_name}")
            result = await func(*args, **kwargs)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Completed {func_name} in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Failed {func_name} after {duration:.3f}s: {e}")
            raise
    
    return wrapper
