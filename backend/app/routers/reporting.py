from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..database import get_db
from ..models.models import (
    Ticket, Asset, CVEAlert, TicketStatus, TicketPriority, TicketCategory
)
from ..schemas.schemas import DashboardStats, TicketListOut, CVEAlertOut
from ..utils.auth import get_current_user, require_technician_or_admin

router = APIRouter(prefix="/api/reports", tags=["Reports & Dashboards"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get comprehensive dashboard statistics."""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(
        Ticket.status.in_([TicketStatus.new, TicketStatus.open])
    ).count()
    in_progress_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.in_progress).count()
    resolved_today = db.query(Ticket).filter(
        and_(
            Ticket.status == TicketStatus.resolved,
            Ticket.resolved_at >= today_start
        )
    ).count()
    sla_breached = db.query(Ticket).filter(Ticket.sla_breached == True).count()
    critical_tickets = db.query(Ticket).filter(Ticket.priority == TicketPriority.critical).count()

    total_assets = db.query(Asset).count()
    active_assets = db.query(Asset).filter(Asset.is_active == True).count()

    critical_cves = db.query(CVEAlert).filter(CVEAlert.cvss_severity == "CRITICAL").count()
    high_cves = db.query(CVEAlert).filter(CVEAlert.cvss_severity == "HIGH").count()

    pending_updates = db.query(Asset).filter(
        Asset.update_status.any(update_status__pending_updates_count__gt=0)
    ).count()

    # Tickets by category
    category_counts = db.query(TicketCategory, func.count(Ticket.id)).join(
        Ticket, Ticket.category == TicketCategory
    ).group_by(TicketCategory).all()
    tickets_by_category = {cat.value: count for cat, count in category_counts}

    # Tickets by status
    status_counts = db.query(TicketStatus, func.count(Ticket.id)).join(
        Ticket, Ticket.status == TicketStatus
    ).group_by(TicketStatus).all()
    tickets_by_status = {status.value: count for status, count in status_counts}

    # Tickets by priority
    priority_counts = db.query(TicketPriority, func.count(Ticket.id)).join(
        Ticket, Ticket.priority == TicketPriority
    ).group_by(TicketPriority).all()
    tickets_by_priority = {priority.value: count for priority, count in priority_counts}

    # Recent tickets
    recent_tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(10).all()

    # Recent CVE alerts
    recent_cves = db.query(CVEAlert).order_by(CVEAlert.created_at.desc()).limit(10).all()

    return DashboardStats(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_today=resolved_today,
        sla_breached=sla_breached,
        critical_tickets=critical_tickets,
        total_assets=total_assets,
        active_assets=active_assets,
        critical_cves=critical_cves,
        high_cves=high_cves,
        pending_updates=pending_updates,
        tickets_by_category=tickets_by_category,
        tickets_by_status=tickets_by_status,
        tickets_by_priority=tickets_by_priority,
        recent_tickets=recent_tickets,
        recent_cve_alerts=recent_cves,
    )


@router.get("/tickets/by-status")
def tickets_by_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get ticket counts by status."""
    results = db.query(TicketStatus, func.count(Ticket.id)).join(
        Ticket, Ticket.status == TicketStatus
    ).group_by(TicketStatus).all()
    return {status.value: count for status, count in results}


@router.get("/tickets/by-priority")
def tickets_by_priority(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get ticket counts by priority."""
    results = db.query(TicketPriority, func.count(Ticket.id)).join(
        Ticket, Ticket.priority == TicketPriority
    ).group_by(TicketPriority).all()
    return {priority.value: count for priority, count in results}


@router.get("/tickets/by-category")
def tickets_by_category(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get ticket counts by category."""
    results = db.query(TicketCategory, func.count(Ticket.id)).join(
        Ticket, Ticket.category == TicketCategory
    ).group_by(TicketCategory).all()
    return {category.value: count for category, count in results}


@router.get("/tickets/resolution-time")
def avg_resolution_time(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get average ticket resolution time."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    resolved_tickets = db.query(Ticket).filter(
        and_(
            Ticket.resolved_at.isnot(None),
            Ticket.resolved_at >= cutoff
        )
    ).all()

    if not resolved_tickets:
        return {"average_hours": 0, "total_resolved": 0}

    total_hours = sum(
        (t.resolved_at - t.created_at).total_seconds() / 3600
        for t in resolved_tickets
    )
    avg_hours = total_hours / len(resolved_tickets)

    return {
        "average_hours": round(avg_hours, 2),
        "total_resolved": len(resolved_tickets),
        "period_days": days
    }


@router.get("/cves/by-severity")
def cves_by_severity(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get CVE counts by severity."""
    results = db.query(CVEAlert.cvss_severity, func.count(CVEAlert.id)).group_by(
        CVEAlert.cvss_severity
    ).all()
    return {severity or "UNKNOWN": count for severity, count in results}


@router.get("/cves/unacknowledged")
def unacknowledged_cves(
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get unacknowledged CVEs."""
    query = db.query(CVEAlert).filter(CVEAlert.is_acknowledged == False)
    if severity:
        query = query.filter(CVEAlert.cvss_severity == severity)
    return query.order_by(CVEAlert.cvss_score.desc()).all()


@router.get("/assets/by-type")
def assets_by_type(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get asset counts by device type."""
    results = db.query(Asset.device_type, func.count(Asset.id)).group_by(
        Asset.device_type
    ).all()
    return {device_type or "Unknown": count for device_type, count in results}


@router.get("/assets/by-department")
def assets_by_department(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get asset counts by department."""
    results = db.query(Asset.department, func.count(Asset.id)).group_by(
        Asset.department
    ).all()
    return {dept or "Unknown": count for dept, count in results}


@router.get("/sla/compliance")
def sla_compliance(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get SLA compliance metrics."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    tickets = db.query(Ticket).filter(Ticket.created_at >= cutoff).all()

    if not tickets:
        return {"compliance_percentage": 100, "total_tickets": 0, "breached": 0}

    total = len(tickets)
    breached = sum(1 for t in tickets if t.sla_breached)
    compliance = ((total - breached) / total * 100) if total > 0 else 100

    return {
        "compliance_percentage": round(compliance, 2),
        "total_tickets": total,
        "breached": breached,
        "period_days": days
    }
