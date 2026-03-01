"""
Pydantic schemas for Chromebook Check-In/Check-Out System
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ─── Chromebook Schemas ────────────────────────────────────────────────────

class ChromebookBase(BaseModel):
    asset_tag: str
    serial_number: str
    model: str
    mac_address: Optional[str] = None


class ChromebookCreate(ChromebookBase):
    purchase_date: Optional[datetime] = None
    warranty_expiration: Optional[datetime] = None


class ChromebookUpdate(BaseModel):
    status: Optional[str] = None
    current_damage_level: Optional[str] = None
    damage_notes: Optional[str] = None
    assigned_to_student_id: Optional[str] = None
    assigned_to_grade: Optional[str] = None
    assigned_to_class: Optional[str] = None


class ChromebookResponse(ChromebookBase):
    id: int
    status: str
    purchase_date: Optional[datetime]
    warranty_expiration: Optional[datetime]
    current_damage_level: str
    damage_notes: Optional[str]
    assigned_to_student_id: Optional[str]
    assigned_to_grade: Optional[str]
    assigned_to_class: Optional[str]
    total_checkouts: int
    last_checkout_date: Optional[datetime]
    last_checkin_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Chromebook Checkout Schemas ───────────────────────────────────────────

class ChromebookCheckoutCreate(BaseModel):
    chromebook_id: int
    student_id: str
    student_name: str
    grade_level: str
    class_name: str
    expected_return_date: datetime
    condition_at_checkout: str
    damage_at_checkout: Optional[str] = "none"
    checkout_notes: Optional[str] = None


class ChromebookCheckoutReturn(BaseModel):
    actual_return_date: datetime
    condition_at_return: str
    damage_at_return: Optional[str] = "none"
    return_notes: Optional[str] = None
    damage_report_id: Optional[int] = None


class ChromebookCheckoutResponse(BaseModel):
    id: int
    chromebook_id: int
    student_id: str
    student_name: str
    grade_level: str
    class_name: str
    checkout_date: datetime
    expected_return_date: datetime
    actual_return_date: Optional[datetime]
    status: str
    condition_at_checkout: str
    damage_at_checkout: str
    condition_at_return: Optional[str]
    damage_at_return: str
    checkout_notes: Optional[str]
    return_notes: Optional[str]
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChromebookCheckoutDetail(ChromebookCheckoutResponse):
    chromebook: Optional[ChromebookResponse] = None


# ─── Chromebook Damage Report Schemas ──────────────────────────────────────

class ChromebookDamageReportCreate(BaseModel):
    chromebook_id: int
    checkout_id: Optional[int] = None
    damage_level: str
    damage_description: str
    damage_photos: Optional[List[str]] = None
    incident_date: Optional[datetime] = None
    is_repairable: bool = True
    repair_cost_estimate: Optional[int] = None
    student_responsible: bool = False
    responsibility_notes: Optional[str] = None


class ChromebookDamageReportUpdate(BaseModel):
    damage_level: Optional[str] = None
    damage_description: Optional[str] = None
    is_repairable: Optional[bool] = None
    repair_cost_estimate: Optional[int] = None
    student_responsible: Optional[bool] = None
    responsibility_notes: Optional[str] = None
    is_resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class ChromebookDamageReportResponse(BaseModel):
    id: int
    chromebook_id: int
    checkout_id: Optional[int]
    damage_level: str
    damage_description: str
    damage_photos: Optional[List[str]]
    reported_date: datetime
    incident_date: Optional[datetime]
    is_repairable: bool
    repair_cost_estimate: Optional[int]
    repair_ticket: Optional[str]
    student_responsible: bool
    responsibility_notes: Optional[str]
    is_resolved: bool
    resolution_date: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Chromebook Checkout Policy Schemas ────────────────────────────────────

class ChromebookCheckoutPolicyBase(BaseModel):
    max_checkout_duration_days: int = 365
    max_concurrent_checkouts_per_student: int = 1
    allow_overnight_checkout: bool = False
    allow_weekend_checkout: bool = False
    student_liable_for_damage: bool = True
    damage_liability_threshold: Optional[int] = None
    send_overdue_notifications: bool = True
    overdue_notification_days: int = 7
    require_damage_inspection: bool = True
    require_parent_signature: bool = False


class ChromebookCheckoutPolicyCreate(ChromebookCheckoutPolicyBase):
    pass


class ChromebookCheckoutPolicyUpdate(ChromebookCheckoutPolicyBase):
    pass


class ChromebookCheckoutPolicyResponse(ChromebookCheckoutPolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Dashboard & Reporting Schemas ────────────────────────────────────────

class ChromebookInventorySummary(BaseModel):
    total_chromebooks: int
    available: int
    checked_out: int
    in_repair: int
    retired: int
    lost: int


class ChromebookCheckoutSummary(BaseModel):
    active_checkouts: int
    overdue_checkouts: int
    returned_this_week: int
    damage_reports_pending: int


class StudentCheckoutHistory(BaseModel):
    student_id: str
    student_name: str
    grade_level: str
    total_checkouts: int
    current_checkout: Optional[ChromebookCheckoutResponse] = None
    checkout_history: List[ChromebookCheckoutResponse]
    damage_reports: List[ChromebookDamageReportResponse]
