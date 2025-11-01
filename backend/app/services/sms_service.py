"""
SMS service for sending alerts via Africa's Talking or Twilio
"""
import logging
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service wrapper"""
    
    def __init__(self):
        self.provider = settings.SMS_PROVIDER
        
        if self.provider == "africastalking":
            self._init_africastalking()
        elif self.provider == "twilio":
            self._init_twilio()
    
    def _init_africastalking(self):
        """Initialize Africa's Talking client"""
        try:
            import africastalking
            africastalking.initialize(
                username=settings.AFRICASTALKING_USERNAME,
                api_key=settings.AFRICASTALKING_API_KEY
            )
            self.sms_client = africastalking.SMS
            logger.info("Africa's Talking SMS initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking: {e}")
            self.sms_client = None
    
    def _init_twilio(self):
        """Initialize Twilio client"""
        try:
            from twilio.rest import Client
            self.sms_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            logger.info("Twilio SMS initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio: {e}")
            self.sms_client = None
    
    def send_sms(self, to: str, message: str) -> bool:
        """
        Send SMS to a phone number
        
        Args:
            to: Recipient phone number
            message: SMS message
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if self.provider == "africastalking":
                return self._send_africastalking(to, message)
            elif self.provider == "twilio":
                return self._send_twilio(to, message)
            else:
                logger.error(f"Unknown SMS provider: {self.provider}")
                return False
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False
    
    def _send_africastalking(self, to: str, message: str) -> bool:
        """Send SMS via Africa's Talking"""
        if not self.sms_client:
            logger.error("Africa's Talking client not initialized")
            return False
        
        try:
            response = self.sms_client.send(
                message,
                [to],
                sender_id=settings.AFRICASTALKING_SENDER_ID
            )
            logger.info(f"SMS sent to {to}: {response}")
            return True
        except Exception as e:
            logger.error(f"Africa's Talking SMS error: {e}")
            return False
    
    def _send_twilio(self, to: str, message: str) -> bool:
        """Send SMS via Twilio"""
        if not self.sms_client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            message = self.sms_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            logger.info(f"SMS sent to {to}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return False
    
    def send_bulk_sms(self, recipients: List[str], message: str) -> dict:
        """
        Send SMS to multiple recipients
        
        Args:
            recipients: List of phone numbers
            message: SMS message
        
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0}
        
        for recipient in recipients:
            if self.send_sms(recipient, message):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return results


# Global SMS service instance
sms_service = SMSService()

