import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RunbookService:
    """
    Simulates secure automation runbooks for the Service Desk.
    Triggers Azure Logic Apps via HTTP triggers.
    """
    
    def __init__(self):
        # In production, these would be real Logic App URLs from settings
        self.logic_app_urls = {
            "reset_password": "https://prod-00.westus.logic.azure.com:443/workflows/...",
            "book_room": "https://prod-01.westus.logic.azure.com:443/workflows/...",
            "check_license": "https://prod-02.westus.logic.azure.com:443/workflows/...",
            "update_payroll": "https://prod-03.westus.logic.azure.com:443/workflows/..."
        }
    
    async def execute_runbook(self, runbook_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific runbook via Logic App Trigger"""
        logger.info(f"Triggering Logic App runbook: {runbook_name} with params: {parameters}")
        
        if runbook_name in self.logic_app_urls:
            try:
                # Simulate HTTP call to Logic App
                # async with aiohttp.ClientSession() as session:
                #     async with session.post(self.logic_app_urls[runbook_name], json=parameters) as resp:
                #         result = await resp.json()
                
                # Mock simulation of Logic App execution
                await asyncio.sleep(1.5)  # Network latency simulation
                
                result = await self._mock_logic_app_response(runbook_name, parameters)
                
                logger.info(f"Logic App {runbook_name} triggered successfully")
                return {
                    "success": True,
                    "runbook": runbook_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result
                }
            except Exception as e:
                logger.error(f"Failed to trigger Logic App {runbook_name}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        else:
            logger.warning(f"Runbook {runbook_name} not found")
            return {
                "success": False,
                "error": "Runbook not found"
            }

    async def _mock_logic_app_response(self, runbook_name: str, params: Dict[str, Any]) -> str:
        """Mock responses that would come back from the Logic App"""
        if runbook_name == "reset_password":
            user_id = params.get("user_id")
            return f"Logic App 'ResetPassword' executed. Temporary password sent to {user_id}@company.com via SMS."
        elif runbook_name == "book_room":
            room = params.get("room", "Conference Room A")
            time = params.get("time", "2:00 PM")
            return f"Logic App 'BookRoom' executed. Room {room} booked for {time}. Calendar invite sent."
        elif runbook_name == "check_license":
            software = params.get("software", "Unknown")
            return f"Logic App 'CheckLicense' executed. License for {software} is valid until 2025-12-31."
        elif runbook_name == "update_payroll":
            return "Logic App 'UpdatePayroll' executed. Payroll information updated."
        return "Logic App executed successfully."

_runbook_service = None

def get_runbook_service() -> RunbookService:
    global _runbook_service
    if _runbook_service is None:
        _runbook_service = RunbookService()
    return _runbook_service
