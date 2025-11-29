import logging
from datetime import datetime
from typing import Dict, Any, Optional
from ..config.settings import settings

logger = logging.getLogger(__name__)

class TelemetryService:
    """
    Service for logging telemetry, audit events, and responsible AI metrics 
    to Azure Application Insights.
    """
    
    def __init__(self):
        self.connection_string = settings.APPLICATIONINSIGHTS_CONNECTION_STRING
        self.enabled = settings.ENABLE_AUDIT_LOGGING
        
        if self.connection_string:
            # In a real implementation, we would initialize the Azure Monitor exporter here
            # from azure.monitor.opentelemetry import configure_azure_monitor
            # configure_azure_monitor(connection_string=self.connection_string)
            logger.info("TelemetryService initialized with connection string")
        else:
            logger.warning("TelemetryService initialized in local mode (no connection string)")

    async def log_event(self, event_name: str, properties: Dict[str, Any] = None):
        """Log a custom event"""
        if not self.enabled:
            return
            
        properties = properties or {}
        properties["timestamp"] = datetime.utcnow().isoformat()
        properties["app_name"] = settings.APP_NAME
        
        # In production:
        # logger.info(event_name, extra={"custom_dimensions": properties})
        
        logger.info(f"[TELEMETRY] Event: {event_name} | Properties: {properties}")

    async def log_audit(self, action: str, user_id: str, details: str, status: str):
        """Log an audit trail event for compliance"""
        await self.log_event("AuditLog", {
            "action": action,
            "user_id": user_id,
            "details": details,
            "status": status,
            "category": "Compliance"
        })

    async def log_responsible_ai(self, check_type: str, passed: bool, score: float, details: str):
        """Log Responsible AI metrics (content safety, bias, etc.)"""
        await self.log_event("ResponsibleAI", {
            "check_type": check_type,
            "passed": passed,
            "score": score,
            "details": details
        })

_telemetry_service = None

def get_telemetry_service() -> TelemetryService:
    global _telemetry_service
    if _telemetry_service is None:
        _telemetry_service = TelemetryService()
    return _telemetry_service
