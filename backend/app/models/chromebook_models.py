"""
Chromebook Check-In/Check-Out System Models
Tracks device assignments, usage, and compliance for student devices
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .models import Base


class ChromebookStatus(str, enum.Enum):
    available = "available"
    checked_out = "checked_out"
    in_repair = "in_repair"
    retired = "retired"
    lost = "lost"


class CheckoutStatus(str, enum.Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"
    lost = "lost"


class DamageLevel(str, enum.Enum):
    none = "none"
    minor = "minor"
    moderate = "moderate"
    severe = "severe"


class Chromebook(Base):
    __tablename__ = "chromebooks"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String(50), unique=True, nullable=False)  # Unique identifier
    serial_number = Column(String(100), unique=True, nullable=False)
    model = Column(String(100))  # e.g., "Lenovo 14e Chromebook"
    mac_address = Column(String(17), unique=True)
    
    status = Column(Enum(ChromebookStatus), default=ChromebookStatus.available)
    purchase_date = Column(DateTime)
    warranty_expiration = Column(DateTime, nullable=True)
    
    # Condition tracking
    current_damage_level = Column(Enum(DamageLevel), default=DamageLevel.none)
    damage_notes = Column(Text)
    
    # Assignment
    assigned_to_student_id = Column(String(50), nullable=True)  # Student ID
    assigned_to_grade = Column(String(20), nullable=True)  # Grade level
    assigned_to_class = Column(String(100), nullable=True)  # Class/Teacher
    
    # Tracking
    total_checkouts = Column(Integer, default=0)
    last_checkout_date = Column(DateTime, nullable=True)
    last_checkin_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    checkouts = relationship("ChromebookCheckout", back_populates="chromebook")
    damage_reports = relationship("ChromebookDamageReport", back_populates="chromebook")


class ChromebookCheckout(Base):
    __tablename__ = "chromebook_checkouts"
    
    id = Column(Integer, primary_key=True, index=True)
    chromebook_id = Column(Integer, ForeignKey("chromebooks.id"), nullable=False)
    
    # Student Information
    student_id = Column(String(50), nullable=False)
    student_name = Column(String(200), nullable=False)
    grade_level = Column(String(20))
    class_name = Column(String(100))
    
    # Checkout Details
    checkout_date = Column(DateTime, default=datetime.utcnow)
    expected_return_date = Column(DateTime, nullable=False)
    actual_return_date = Column(DateTime, nullable=True)
    
    status = Column(Enum(CheckoutStatus), default=CheckoutStatus.active)
    
    # Condition at Checkout
    condition_at_checkout = Column(String(200))  # Description of device condition
    damage_at_checkout = Column(Enum(DamageLevel), default=DamageLevel.none)
    
    # Condition at Return
    condition_at_return = Column(String(200), nullable=True)
    damage_at_return = Column(Enum(DamageLevel), default=DamageLevel.none)
    damage_report_id = Column(Integer, ForeignKey("chromebook_damage_reports.id"), nullable=True)
    
    # Checkout/Return Personnel
    checked_out_by = Column(Integer, ForeignKey("users.id"))  # Staff member ID
    checked_in_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Staff member ID
    
    # Notes
    checkout_notes = Column(Text)
    return_notes = Column(Text, nullable=True)
    
    # Compliance
    is_overdue = Column(Boolean, default=False)
    overdue_notification_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chromebook = relationship("Chromebook", back_populates="checkouts")
    checked_out_by_user = relationship("User", foreign_keys=[checked_out_by])
    checked_in_by_user = relationship("User", foreign_keys=[checked_in_by])
    damage_report = relationship("ChromebookDamageReport", back_populates="checkout")


class ChromebookDamageReport(Base):
    __tablename__ = "chromebook_damage_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    chromebook_id = Column(Integer, ForeignKey("chromebooks.id"), nullable=False)
    checkout_id = Column(Integer, ForeignKey("chromebook_checkouts.id"), nullable=True)
    
    # Damage Details
    damage_level = Column(Enum(DamageLevel), nullable=False)
    damage_description = Column(Text, nullable=False)
    damage_photos = Column(JSON)  # Array of photo URLs
    
    # Incident Details
    reported_by = Column(Integer, ForeignKey("users.id"))
    reported_date = Column(DateTime, default=datetime.utcnow)
    incident_date = Column(DateTime, nullable=True)
    
    # Repair Status
    is_repairable = Column(Boolean, default=True)
    repair_cost_estimate = Column(Integer, nullable=True)  # In cents
    repair_ticket = Column(String(50), nullable=True)  # Link to IT ticket
    
    # Responsibility
    student_responsible = Column(Boolean, default=False)
    responsibility_notes = Column(Text)
    
    # Resolution
    is_resolved = Column(Boolean, default=False)
    resolution_date = Column(DateTime, nullable=True)
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chromebook = relationship("Chromebook", back_populates="damage_reports")
    checkout = relationship("ChromebookCheckout", back_populates="damage_report")
    reported_by_user = relationship("User", foreign_keys=[reported_by])


class ChromebookCheckoutPolicy(Base):
    __tablename__ = "chromebook_checkout_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Policy Settings
    max_checkout_duration_days = Column(Integer, default=365)  # Annual checkout
    max_concurrent_checkouts_per_student = Column(Integer, default=1)
    allow_overnight_checkout = Column(Boolean, default=False)
    allow_weekend_checkout = Column(Boolean, default=False)
    
    # Damage Policy
    student_liable_for_damage = Column(Boolean, default=True)
    damage_liability_threshold = Column(Integer)  # In cents - damage above this is student's responsibility
    
    # Notification Settings
    send_overdue_notifications = Column(Boolean, default=True)
    overdue_notification_days = Column(Integer, default=7)  # Notify after X days overdue
    
    # Compliance
    require_damage_inspection = Column(Boolean, default=True)
    require_parent_signature = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
