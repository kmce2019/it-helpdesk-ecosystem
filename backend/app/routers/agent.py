from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models.models import Asset, InstalledSoftware, UpdateStatus, TicketCategory, TicketPriority
from ..schemas.schemas import AgentPayload, TicketCreate
from ..config import settings
from ..services.cve_service import run_cve_scan_for_asset
from .tickets import create_ticket
from fastapi import BackgroundTasks

router = APIRouter(prefix="/api/agent", tags=["Agent"])


def verify_agent_key(x_agent_key: str = Header(...)):
    """Verify the agent API key."""
    if x_agent_key != settings.AGENT_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid agent key")
    return x_agent_key


@router.post("/report", status_code=status.HTTP_200_OK)
async def agent_report(
    payload: AgentPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    agent_key: str = Depends(verify_agent_key)
):
    """
    Receive data from the deployed agent.
    This endpoint updates or creates an asset record and triggers CVE scanning.
    """
    # Find or create asset
    asset = db.query(Asset).filter(Asset.asset_tag == payload.asset_tag).first()
    if not asset:
        asset = Asset(asset_tag=payload.asset_tag)
        db.add(asset)

    # Update asset fields
    asset.hostname = payload.hostname
    asset.device_type = payload.device_type
    asset.manufacturer = payload.manufacturer
    asset.model = payload.model
    asset.serial_number = payload.serial_number
    asset.os_name = payload.os_name
    asset.os_version = payload.os_version
    asset.os_build = payload.os_build
    asset.cpu = payload.cpu
    asset.ram_gb = payload.ram_gb
    asset.disk_total_gb = payload.disk_total_gb
    asset.disk_free_gb = payload.disk_free_gb
    asset.ip_address = payload.ip_address
    asset.mac_address = payload.mac_address
    asset.location = payload.location
    asset.assigned_user = payload.assigned_user
    asset.department = payload.department
    asset.agent_version = payload.agent_version
    asset.last_seen = datetime.utcnow()
    asset.is_active = True

    db.flush()

    # Update installed software
    db.query(InstalledSoftware).filter(InstalledSoftware.asset_id == asset.id).delete()
    for sw in payload.software:
        installed_sw = InstalledSoftware(
            asset_id=asset.id,
            name=sw.name,
            version=sw.version,
            vendor=sw.vendor,
            install_date=sw.install_date,
            install_location=sw.install_location,
        )
        db.add(installed_sw)

    # Update or create update status
    update_status = db.query(UpdateStatus).filter(UpdateStatus.asset_id == asset.id).first()
    if not update_status:
        update_status = UpdateStatus(asset_id=asset.id)
        db.add(update_status)

    update_status.pending_updates_count = len(payload.pending_updates)
    update_status.critical_updates_count = sum(
        1 for u in payload.pending_updates if u.severity and u.severity.lower() == "critical"
    )
    update_status.security_updates_count = sum(
        1 for u in payload.pending_updates if u.severity and u.severity.lower() in ["critical", "security"]
    )
    update_status.last_update_check = datetime.utcnow()
    update_status.update_details = [u.model_dump() for u in payload.pending_updates]

    db.commit()

    # Trigger CVE scan in background
    background_tasks.add_task(run_cve_scan_for_asset, db, asset)

    # If there are critical updates, optionally create a ticket
    if update_status.critical_updates_count > 0:
        ticket_in = TicketCreate(
            title=f"Critical Updates Available - {asset.hostname}",
            description=f"Asset {asset.hostname} has {update_status.critical_updates_count} critical updates pending.",
            priority=TicketPriority.high,
            category=TicketCategory.infrastructure,
            asset_tag=asset.asset_tag,
            location=asset.location,
        )
        # Create ticket with system user (would need a system user in the DB)
        # For now, we'll skip auto-ticket creation to keep it simple

    return {
        "status": "success",
        "asset_id": asset.id,
        "asset_tag": asset.asset_tag,
        "message": "Asset data received and processed"
    }


@router.get("/health", status_code=status.HTTP_200_OK)
def agent_health(agent_key: str = Depends(verify_agent_key)):
    """Health check endpoint for the agent."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
