from azure.communication.email import EmailClient
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.connection_string = settings.AZURE_COMMUNICATION_CONNECTION_STRING
        self.sender_address = settings.EMAIL_SENDER_ADDRESS
        self.client = None
        
        if self.connection_string:
            try:
                self.client = EmailClient.from_connection_string(self.connection_string)
                logger.info("EmailClient initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EmailClient: {e}")
        else:
            logger.warning("AZURE_COMMUNICATION_CONNECTION_STRING not set. Email service disabled.")

    def send_email(self, recipient: str, subject: str, html_content: str) -> bool:
        if not self.client or not self.sender_address:
            logger.warning("Email client not initialized or sender address missing.")
            return False

        try:
            message = {
                "senderAddress": self.sender_address,
                "recipients":  {
                    "to": [{"address": recipient}]
                },

def get_email_service():
    global _email_service
    if not _email_service:
        _email_service = EmailService()
    return _email_service