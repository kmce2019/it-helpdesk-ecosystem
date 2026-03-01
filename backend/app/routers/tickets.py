from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timedelta
import random
import string
from ..database import get_db
from ..models.models import (
    Ticket, TicketComment, TicketHistory, SLA, User,
    TicketStatus, TicketPriority, TicketCategory, UserRole
)
from ..schemas.schemas import (
    TicketCreate, TicketUpdate, TicketOut, TicketListOut,
    TicketCommentCreate, TicketCommentOut
)
from ..utils.auth import get_current_user, require_technician_or_admin
from ..services.email_service import (
    send_email, build_ticket_created_email, build_ticket_updated_email
)
from ..services.google_chat_service import (
    notify_new_ticket, notify_ticket_assigned, notify_ticket_resolved, notify_sla_breach
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


def generate_ticket_number(db: Session) -> str:
    """Generate a unique ticket number."""
    year = datetime.utcnow().strftime("%Y")
    while True:
        suffix = ''.join(random.choices(string.digits, k=5))
        ticket_number = f"TKT-{year}-{suffix}"
        if not db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first():
            return ticket_number


def apply_sla(ticket: Ticket, db: Session):
    """Apply SLA deadlines based on ticket priority."""
    sla = db.query(SLA).filter(SLA.priority == ticket.priority).first()
    if sla:
        ticket.sla_id = sla.id
        ticket.sla_response_due = ticket.created_at + timedelta(hours=sla.response_time_hours)
        ticket.sla_resolution_due = ticket.created_at + timedelta(hours=sla.resolution_time_hours)


def record_history(db: Session, ticket_id: int, changed_by_id: int,
                   field: str, old_val: str, new_val: str):
    """Record a change in ticket history."""
    history = TicketHistory(
        ticket_id=ticket_id,
        changed_by_id=changed_by_id,
        field_changed=field,
        old_value=str(old_val) if old_val is not None else None,
        new_value=str(new_val) if new_val is not None else None,
    )
    db.add(history)


@router.get("/", response_model=List[TicketListOut])
def list_tickets(
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    assignee_id: Optional[int] = None,
    submitter_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Ticket).options(
        joinedload(Ticket.submitter),
        joinedload(Ticket.assignee),
        joinedload(Ticket.sla)
    )

    # End users can only see their own tickets
    if current_user.role == UserRole.end_user:
        query = query.filter(Ticket.submitter_id == current_user.id)

    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if assignee_id:
        query = query.filter(Ticket.assignee_id == assignee_id)
    if submitter_id:
        query = query.filter(Ticket.submitter_id == submitter_id)
    if search:
        query = query.filter(
            or_(
                Ticket.title.ilike(f"%{search}%"),
                Ticket.description.ilike(f"%{search}%"),
                Ticket.ticket_number.ilike(f"%{search}%")
            )
        )

    return query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    submitter_id = ticket_in.submitter_id or current_user.id

    ticket = Ticket(
        ticket_number=generate_ticket_number(db),
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority,
        category=ticket_in.category,
        location=ticket_in.location,
        asset_tag=ticket_in.asset_tag,
        tags=ticket_in.tags,
        submitter_id=submitter_id,
        status=TicketStatus.new,
    )
    db.add(ticket)
    db.flush()
    apply_sla(ticket, db)
    db.commit()
    db.refresh(ticket)

    # Reload with relationships
    ticket = db.query(Ticket).options(
        joinedload(Ticket.submitter),
        joinedload(Ticket.assignee),
        joinedload(Ticket.sla),
        joinedload(Ticket.comments).joinedload(TicketComment.author),
        joinedload(Ticket.history)
    ).filter(Ticket.id == ticket.id).first()

    # Background notifications
    submitter = db.query(User).filter(User.id == submitter_id).first()
    if submitter:
        subject, body = build_ticket_created_email(
            ticket.ticket_number, ticket.title,
            ticket.category.value, ticket.priority.value, submitter.full_name
        )
        background_tasks.add_task(send_email, submitter.email, subject, body)

    background_tasks.add_task(
        notify_new_ticket,
        ticket.ticket_number, ticket.title,
        ticket.priority.value, ticket.category.value,
        submitter.full_name if submitter else "Unknown"
    )

    return ticket


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).options(
        joinedload(Ticket.submitter),
        joinedload(Ticket.assignee),
        joinedload(Ticket.sla),
        joinedload(Ticket.comments).joinedload(TicketComment.author),
        joinedload(Ticket.history)
    ).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == UserRole.end_user and ticket.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ticket


@router.put("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # End users can only update their own tickets and only certain fields
    if current_user.role == UserRole.end_user:
        if ticket.submitter_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        # End users cannot change status, priority, or assignee
        ticket_in.status = None
        ticket_in.priority = None
        ticket_in.assignee_id = None

    update_data = ticket_in.model_dump(exclude_unset=True, exclude_none=True)

    for field, new_value in update_data.items():
        old_value = getattr(ticket, field)
        if old_value != new_value:
            record_history(db, ticket.id, current_user.id, field, old_value, new_value)
            setattr(ticket, field, new_value)

            # Handle status transitions
            if field == "status":
                if new_value == TicketStatus.in_progress and not ticket.first_response_at:
                    ticket.first_response_at = datetime.utcnow()
                elif new_value in [TicketStatus.resolved, TicketStatus.closed]:
                    ticket.resolved_at = datetime.utcnow()
                    background_tasks.add_task(
                        notify_ticket_resolved,
                        ticket.ticket_number, ticket.title, current_user.full_name
                    )

            # Handle assignment
            if field == "assignee_id" and new_value:
                assignee = db.query(User).filter(User.id == new_value).first()
                if assignee:
                    background_tasks.add_task(
                        notify_ticket_assigned,
                        ticket.ticket_number, ticket.title, assignee.full_name
                    )
                ticket.status = TicketStatus.open

            # Re-apply SLA if priority changes
            if field == "priority":
                apply_sla(ticket, db)

    ticket.updated_at = datetime.utcnow()
    db.commit()

    ticket = db.query(Ticket).options(
        joinedload(Ticket.submitter),
        joinedload(Ticket.assignee),
        joinedload(Ticket.sla),
        joinedload(Ticket.comments).joinedload(TicketComment.author),
        joinedload(Ticket.history)
    ).filter(Ticket.id == ticket_id).first()

    return ticket


@router.post("/{ticket_id}/comments", response_model=TicketCommentOut)
async def add_comment(
    ticket_id: int,
    comment_in: TicketCommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role == UserRole.end_user and ticket.submitter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Internal notes only for technicians/admins
    if comment_in.is_internal and current_user.role == UserRole.end_user:
        comment_in.is_internal = False

    comment = TicketComment(
        ticket_id=ticket_id,
        author_id=current_user.id,
        content=comment_in.content,
        is_internal=comment_in.is_internal,
    )
    db.add(comment)

    # Mark first response
    if not ticket.first_response_at and current_user.role in [UserRole.admin, UserRole.technician]:
        ticket.first_response_at = datetime.utcnow()
        if ticket.status == TicketStatus.new:
            ticket.status = TicketStatus.open

    db.commit()
    db.refresh(comment)

    # Notify submitter of the reply (if it's a public comment from a technician)
    if not comment_in.is_internal and current_user.role in [UserRole.admin, UserRole.technician]:
        submitter = db.query(User).filter(User.id == ticket.submitter_id).first()
        if submitter:
            subject, body = build_ticket_updated_email(
                ticket.ticket_number, ticket.title,
                "New Reply", comment_in.content[:200], current_user.full_name
            )
            background_tasks.add_task(send_email, submitter.email, subject, body)

    return db.query(TicketComment).options(
        joinedload(TicketComment.author)
    ).filter(TicketComment.id == comment.id).first()


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_technician_or_admin)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
