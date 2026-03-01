import httpx
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)


async def send_google_chat_message(message: str, webhook_url: Optional[str] = None) -> bool:
    """Send a message to a Google Chat space via webhook."""
    url = webhook_url or settings.GOOGLE_CHAT_WEBHOOK_URL

    if not settings.GOOGLE_CHAT_ENABLED or not url:
        logger.info(f"Google Chat disabled or no webhook URL. Would have sent: {message[:100]}")
        return False

    payload = {"text": message}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        logger.info("Google Chat message sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send Google Chat message: {e}")
        return False


async def notify_new_ticket(ticket_number: str, title: str, priority: str,
                             category: str, submitter: str) -> bool:
    """Notify Google Chat about a new ticket."""
    priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority.lower(), "⚪")
    message = (
        f"{priority_emoji} *New Ticket #{ticket_number}*\n"
        f"*Title:* {title}\n"
        f"*Priority:* {priority.upper()}\n"
        f"*Category:* {category}\n"
        f"*Submitted by:* {submitter}"
    )
    return await send_google_chat_message(message)


async def notify_ticket_assigned(ticket_number: str, title: str, assignee: str) -> bool:
    """Notify Google Chat about a ticket assignment."""
    message = (
        f"🔧 *Ticket #{ticket_number} Assigned*\n"
        f"*Title:* {title}\n"
        f"*Assigned to:* {assignee}"
    )
    return await send_google_chat_message(message)


async def notify_ticket_resolved(ticket_number: str, title: str, resolved_by: str) -> bool:
    """Notify Google Chat about a ticket resolution."""
    message = (
        f"✅ *Ticket #{ticket_number} Resolved*\n"
        f"*Title:* {title}\n"
        f"*Resolved by:* {resolved_by}"
    )
    return await send_google_chat_message(message)


async def notify_sla_breach(ticket_number: str, title: str, priority: str) -> bool:
    """Notify Google Chat about an SLA breach."""
    message = (
        f"⚠️ *SLA BREACH - Ticket #{ticket_number}*\n"
        f"*Title:* {title}\n"
        f"*Priority:* {priority.upper()}\n"
        f"This ticket has exceeded its SLA resolution time!"
    )
    return await send_google_chat_message(message)


async def notify_critical_cve(asset_hostname: str, cve_id: str, cvss_score: float,
                               software_name: str) -> bool:
    """Notify Google Chat about a critical CVE."""
    message = (
        f"🚨 *Critical CVE Detected*\n"
        f"*CVE ID:* {cve_id}\n"
        f"*Asset:* {asset_hostname}\n"
        f"*Software:* {software_name}\n"
        f"*CVSS Score:* {cvss_score}/10.0\n"
        f"Immediate attention required!"
    )
    return await send_google_chat_message(message)
