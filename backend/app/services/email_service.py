"""
Email service for sending notifications via SendGrid
"""
import logging
from typing import List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service wrapper"""
    
    def __init__(self):
        self.provider = settings.EMAIL_PROVIDER
        
        if self.provider == "sendgrid":
            self._init_sendgrid()
    
    def _init_sendgrid(self):
        """Initialize SendGrid client"""
        try:
            from sendgrid import SendGridAPIClient
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            logger.info("SendGrid email initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SendGrid: {e}")
            self.client = None
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email to recipient
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if self.provider == "sendgrid":
            return self._send_sendgrid(to_email, subject, html_content, text_content)
        else:
            logger.error(f"Unknown email provider: {self.provider}")
            return False
    
    def _send_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email via SendGrid"""
        if not self.client:
            logger.error("SendGrid client not initialized")
            return False
        
        try:
            from sendgrid.helpers.mail import Mail, Content
            
            message = Mail(
                from_email=(settings.FROM_EMAIL, settings.FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if text_content:
                message.content = [
                    Content("text/plain", text_content),
                    Content("text/html", html_content)
                ]
            
            response = self.client.send(message)
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"SendGrid email error: {e}")
            return False
    
    def send_anti_theft_alert(
        self,
        to_email: str,
        user_name: str,
        trigger_time: str,
        tracking_url: str
    ) -> bool:
        """
        Send anti-theft alert email
        
        Args:
            to_email: Recipient email
            user_name: Name of user whose device was stolen
            trigger_time: When the alert was triggered
            tracking_url: URL to track device location
        
        Returns:
            True if sent successfully
        """
        subject = f"🚨 URGENT: Anti-Theft Alert for {user_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #dc2626; color: white; padding: 20px; text-align: center;">
                <h1>🚨 ANTI-THEFT ALERT</h1>
            </div>
            <div style="padding: 20px; background-color: #f3f4f6;">
                <p style="font-size: 16px;">
                    <strong>{user_name}</strong> has triggered an anti-theft alert.
                </p>
                <p>
                    <strong>Time:</strong> {trigger_time}
                </p>
                <p>
                    This means their device may have been stolen. You are receiving this as an emergency contact.
                </p>
                <div style="margin: 30px 0; text-align: center;">
                    <a href="{tracking_url}" 
                       style="background-color: #dc2626; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Track Device Location
                    </a>
                </div>
                <p style="color: #6b7280; font-size: 14px;">
                    Please take appropriate action and contact local authorities if necessary.
                </p>
            </div>
            <div style="background-color: #1f2937; color: white; padding: 15px; text-align: center; font-size: 12px;">
                <p>NuuR Urban Safety Platform | Ethiopia</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        ANTI-THEFT ALERT
        
        {user_name} has triggered an anti-theft alert at {trigger_time}.
        
        Their device may have been stolen. Please track the device location at:
        {tracking_url}
        
        Contact local authorities if necessary.
        
        NuuR Urban Safety Platform
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_emergency_alert(
        self,
        to_email: str,
        report_type: str,
        location: str,
        description: str,
        report_url: str
    ) -> bool:
        """
        Send emergency report alert email
        
        Args:
            to_email: Recipient email
            report_type: Type of emergency
            location: Location description
            description: Emergency description
            report_url: URL to view full report
        
        Returns:
            True if sent successfully
        """
        subject = f"🚨 Emergency Alert: {report_type.upper()}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #dc2626; color: white; padding: 20px; text-align: center;">
                <h1>🚨 EMERGENCY ALERT</h1>
                <h2>{report_type.upper()}</h2>
            </div>
            <div style="padding: 20px; background-color: #f3f4f6;">
                <p><strong>Location:</strong> {location}</p>
                <p><strong>Description:</strong> {description}</p>
                <div style="margin: 30px 0; text-align: center;">
                    <a href="{report_url}" 
                       style="background-color: #dc2626; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Full Report
                    </a>
                </div>
            </div>
            <div style="background-color: #1f2937; color: white; padding: 15px; text-align: center; font-size: 12px;">
                <p>NuuR Urban Safety Platform | Ethiopia</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, html_content)


# Global email service instance
email_service = EmailService()

