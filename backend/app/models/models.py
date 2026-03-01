from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    admin = "admin"
    technician = "technician"
    end_user = "end_user"


class TicketStatus(str, enum.Enum):
    new = "new"
    open = "open"
    in_progress = "in_progress"
    pending = "pending"
    resolved = "resolved"
    closed = "closed"
    cancelled = "cancelled"


class TicketPriority(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TicketCategory(str, enum.Enum):
    hardware = "hardware"
    software = "software"
    network = "network"
    account_access = "account_access"
    email = "email"
    printing = "printing"
    security = "security"
    classroom_tech = "classroom_tech"
    infrastructure = "infrastructure"
    other = "other"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.end_user, nullable=False)
    department = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submitted_tickets = relationship("Ticket", foreign_keys="Ticket.submitter_id", back_populates="submitter")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assignee_id", back_populates="assignee")
    comments = relationship("TicketComment", back_populates="author")


class SLA(Base):
    __tablename__ = "slas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    priority = Column(Enum(TicketPriority), unique=True, nullable=False)
    response_time_hours = Column(Float, nullable=False)  # Time to first response
    resolution_time_hours = Column(Float, nullable=False)  # Time to resolve
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="sla")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.new, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.medium, nullable=False)
    category = Column(Enum(TicketCategory), default=TicketCategory.other, nullable=False)

    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sla_id = Column(Integer, ForeignKey("slas.id"), nullable=True)

    location = Column(String(255), nullable=True)
    asset_tag = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)

    # SLA tracking
    sla_response_due = Column(DateTime, nullable=True)
    sla_resolution_due = Column(DateTime, nullable=True)
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    sla_breached = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submitter = relationship("User", foreign_keys=[submitter_id], back_populates="submitted_tickets")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tickets")
    sla = relationship("SLA", back_populates="tickets")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes vs. public replies
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", back_populates="comments")


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="attachments")


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    field_changed = Column(String(100), nullable=False)
    old_value = Column(String(500), nullable=True)
    new_value = Column(String(500), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="history")


# ─── ITAM Models ───────────────────────────────────────────────────────────────

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_tag = Column(String(100), unique=True, nullable=False, index=True)
    hostname = Column(String(255), nullable=True)
    device_type = Column(String(100), nullable=True)  # desktop, laptop, server, etc.
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    os_name = Column(String(100), nullable=True)
    os_version = Column(String(100), nullable=True)
    os_build = Column(String(100), nullable=True)
    cpu = Column(String(255), nullable=True)
    ram_gb = Column(Float, nullable=True)
    disk_total_gb = Column(Float, nullable=True)
    disk_free_gb = Column(Float, nullable=True)
    ip_address = Column(String(50), nullable=True)
    mac_address = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    assigned_user = Column(String(255), nullable=True)
    department = Column(String(100), nullable=True)
    last_seen = Column(DateTime, nullable=True)
    agent_version = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    software = relationship("InstalledSoftware", back_populates="asset", cascade="all, delete-orphan")
    cve_alerts = relationship("CVEAlert", back_populates="asset", cascade="all, delete-orphan")
    update_status = relationship("UpdateStatus", back_populates="asset", uselist=False, cascade="all, delete-orphan")


class InstalledSoftware(Base):
    __tablename__ = "installed_software"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(100), nullable=True)
    vendor = Column(String(255), nullable=True)
    install_date = Column(String(50), nullable=True)
    install_location = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="software")


class CVEAlert(Base):
    __tablename__ = "cve_alerts"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    cve_id = Column(String(50), nullable=False, index=True)
    software_name = Column(String(255), nullable=True)
    software_version = Column(String(100), nullable=True)
    cvss_score = Column(Float, nullable=True)
    cvss_severity = Column(String(20), nullable=True)  # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(Text, nullable=True)
    published_date = Column(DateTime, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset", back_populates="cve_alerts")


class UpdateStatus(Base):
    __tablename__ = "update_status"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), unique=True, nullable=False)
    pending_updates_count = Column(Integer, default=0)
    critical_updates_count = Column(Integer, default=0)
    security_updates_count = Column(Integer, default=0)
    last_update_check = Column(DateTime, nullable=True)
    last_successful_update = Column(DateTime, nullable=True)
    update_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    asset = relationship("Asset", back_populates="update_status")


# ─── Settings Model ────────────────────────────────────────────────────────────

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
