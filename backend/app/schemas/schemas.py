from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from ..models.models import UserRole, TicketStatus, TicketPriority, TicketCategory


# ─── Auth Schemas ──────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserOut"


class TokenData(BaseModel):
    username: Optional[str] = None


# ─── User Schemas ──────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.end_user
    department: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── SLA Schemas ──────────────────────────────────────────────────────────────

class SLABase(BaseModel):
    name: str
    priority: TicketPriority
    response_time_hours: float
    resolution_time_hours: float
    description: Optional[str] = None


class SLACreate(SLABase):
    pass


class SLAOut(SLABase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Ticket Schemas ────────────────────────────────────────────────────────────

class TicketCommentBase(BaseModel):
    content: str
    is_internal: bool = False


class TicketCommentCreate(TicketCommentBase):
    pass


class TicketCommentOut(TicketCommentBase):
    id: int
    ticket_id: int
    author: UserOut
    created_at: datetime

    class Config:
        from_attributes = True


class TicketHistoryOut(BaseModel):
    id: int
    field_changed: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_at: datetime
    changed_by_id: Optional[int]

    class Config:
        from_attributes = True


class TicketBase(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.medium
    category: TicketCategory = TicketCategory.other
    location: Optional[str] = None
    asset_tag: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketCreate(TicketBase):
    submitter_id: Optional[int] = None  # If None, uses current user


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assignee_id: Optional[int] = None
    location: Optional[str] = None
    asset_tag: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketOut(TicketBase):
    id: int
    ticket_number: str
    status: TicketStatus
    submitter: UserOut
    assignee: Optional[UserOut] = None
    sla: Optional[SLAOut] = None
    sla_response_due: Optional[datetime] = None
    sla_resolution_due: Optional[datetime] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sla_breached: bool
    created_at: datetime
    updated_at: datetime
    comments: List[TicketCommentOut] = []
    history: List[TicketHistoryOut] = []

    class Config:
        from_attributes = True


class TicketListOut(TicketBase):
    id: int
    ticket_number: str
    status: TicketStatus
    submitter: UserOut
    assignee: Optional[UserOut] = None
    sla_resolution_due: Optional[datetime] = None
    sla_breached: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── ITAM Schemas ──────────────────────────────────────────────────────────────

class InstalledSoftwareOut(BaseModel):
    id: int
    name: str
    version: Optional[str]
    vendor: Optional[str]
    install_date: Optional[str]

    class Config:
        from_attributes = True


class UpdateStatusOut(BaseModel):
    pending_updates_count: int
    critical_updates_count: int
    security_updates_count: int
    last_update_check: Optional[datetime]
    last_successful_update: Optional[datetime]
    update_details: Optional[Any]

    class Config:
        from_attributes = True


class AssetBase(BaseModel):
    asset_tag: str
    hostname: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_build: Optional[str] = None
    cpu: Optional[str] = None
    ram_gb: Optional[float] = None
    disk_total_gb: Optional[float] = None
    disk_free_gb: Optional[float] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    location: Optional[str] = None
    assigned_user: Optional[str] = None
    department: Optional[str] = None
    agent_version: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetOut(AssetBase):
    id: int
    last_seen: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    software: List[InstalledSoftwareOut] = []
    update_status: Optional[UpdateStatusOut] = None

    class Config:
        from_attributes = True


class AssetListOut(AssetBase):
    id: int
    last_seen: Optional[datetime]
    is_active: bool
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── CVE Schemas ──────────────────────────────────────────────────────────────

class CVEAlertOut(BaseModel):
    id: int
    asset_id: int
    cve_id: str
    software_name: Optional[str]
    software_version: Optional[str]
    cvss_score: Optional[float]
    cvss_severity: Optional[str]
    description: Optional[str]
    published_date: Optional[datetime]
    is_acknowledged: bool
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Agent Payload Schemas ─────────────────────────────────────────────────────

class SoftwareItem(BaseModel):
    name: str
    version: Optional[str] = None
    vendor: Optional[str] = None
    install_date: Optional[str] = None
    install_location: Optional[str] = None


class UpdateItem(BaseModel):
    title: Optional[str] = None
    kb_number: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None


class AgentPayload(BaseModel):
    asset_tag: str
    hostname: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_build: Optional[str] = None
    cpu: Optional[str] = None
    ram_gb: Optional[float] = None
    disk_total_gb: Optional[float] = None
    disk_free_gb: Optional[float] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    location: Optional[str] = None
    assigned_user: Optional[str] = None
    department: Optional[str] = None
    agent_version: Optional[str] = None
    software: List[SoftwareItem] = []
    pending_updates: List[UpdateItem] = []
    last_update_check: Optional[str] = None
    last_successful_update: Optional[str] = None


# ─── Report Schemas ────────────────────────────────────────────────────────────

class ReportFilter(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[List[TicketStatus]] = None
    priority: Optional[List[TicketPriority]] = None
    category: Optional[List[TicketCategory]] = None
    assignee_id: Optional[int] = None
    submitter_id: Optional[int] = None
    sla_breached: Optional[bool] = None


class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_today: int
    sla_breached: int
    critical_tickets: int
    total_assets: int
    active_assets: int
    critical_cves: int
    high_cves: int
    pending_updates: int
    tickets_by_category: dict
    tickets_by_status: dict
    tickets_by_priority: dict
    recent_tickets: List[TicketListOut]
    recent_cve_alerts: List[CVEAlertOut]


# ─── Settings Schemas ──────────────────────────────────────────────────────────

class SettingUpdate(BaseModel):
    value: str


class GoogleChatTest(BaseModel):
    message: str = "Test message from District IT Help Desk"


class EmailTest(BaseModel):
    to_email: EmailStr
    subject: str = "Test Email from District IT Help Desk"


Token.model_rebuild()
