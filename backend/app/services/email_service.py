import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)


def send_email_sync(to_email: str, subject: str, body_html: str, body_text: Optional[str] = None):
    """Send an email synchronously using SMTP."""
    if not settings.SMTP_ENABLED:
        logger.info(f"SMTP disabled. Would have sent email to {to_email}: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls(context=context)
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


async def send_email(to_email: str, subject: str, body_html: str, body_text: Optional[str] = None):
    """Send an email asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, send_email_sync, to_email, subject, body_html, body_text)


def build_ticket_created_email(ticket_number: str, title: str, category: str,
                                priority: str, submitter_name: str) -> tuple[str, str]:
    """Build email content for a new ticket."""
    subject = f"[Ticket #{ticket_number}] New Ticket: {title}"
    body_html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1a56db; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">District IT Help Desk</h2>
            <p style="margin: 5px 0 0 0;">New Ticket Created</p>
        </div>
        <div style="background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; border-radius: 0 0 8px 8px;">
            <p>Hello {submitter_name},</p>
            <p>Your support ticket has been successfully created. Our team will review it shortly.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
                <tr><td style="padding: 8px; background: #e5e7eb; font-weight: bold; width: 40%;">Ticket Number</td>
                    <td style="padding: 8px; background: #f3f4f6;">#{ticket_number}</td></tr>
                <tr><td style="padding: 8px; background: #e5e7eb; font-weight: bold;">Title</td>
                    <td style="padding: 8px; background: #f3f4f6;">{title}</td></tr>
                <tr><td style="padding: 8px; background: #e5e7eb; font-weight: bold;">Category</td>
                    <td style="padding: 8px; background: #f3f4f6;">{category}</td></tr>
                <tr><td style="padding: 8px; background: #e5e7eb; font-weight: bold;">Priority</td>
                    <td style="padding: 8px; background: #f3f4f6;">{priority}</td></tr>
            </table>
            <p style="color: #6b7280; font-size: 12px;">This is an automated message from the District IT Help Desk system.</p>
        </div>
    </div>
    </body></html>
    """
    body_text = f"New ticket #{ticket_number} created: {title}\nCategory: {category}\nPriority: {priority}"
    return subject, body_html


def build_ticket_updated_email(ticket_number: str, title: str, update_type: str,
                                new_value: str, commenter_name: str) -> tuple[str, str]:
    """Build email content for a ticket update."""
    subject = f"[Ticket #{ticket_number}] Update: {update_type}"
    body_html = f"""
    <html><body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1a56db; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">District IT Help Desk</h2>
            <p style="margin: 5px 0 0 0;">Ticket Updated</p>
        </div>
        <div style="background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; border-radius: 0 0 8px 8px;">
            <p>Ticket <strong>#{ticket_number}</strong> - {title} has been updated.</p>
            <p><strong>{update_type}:</strong> {new_value}</p>
            <p><em>Updated by: {commenter_name}</em></p>
            <p style="color: #6b7280; font-size: 12px;">This is an automated message from the District IT Help Desk system.</p>
        </div>
    </div>
    </body></html>
    """
    return subject, body_html
