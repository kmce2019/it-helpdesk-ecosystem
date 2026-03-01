"""
Extended models for Vehicle Requests, Inventory, Knowledge Base, and Branding
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .models import Base


class VehicleStatus(str, enum.Enum):
    available = "available"
    in_use = "in_use"
    maintenance = "maintenance"
    retired = "retired"


class VehicleRequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Van-001"
    make = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    license_plate = Column(String(20), unique=True)
    vin = Column(String(50), unique=True)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.available)
    capacity = Column(Integer)  # Number of passengers
    current_mileage = Column(Float, default=0.0)
    last_maintenance = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requests = relationship("VehicleRequest", back_populates="vehicle")
    maintenance_logs = relationship("VehicleMaintenanceLog", back_populates="vehicle")


class VehicleRequest(Base):
    __tablename__ = "vehicle_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    status = Column(Enum(VehicleRequestStatus), default=VehicleRequestStatus.pending)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    purpose = Column(String(200), nullable=False)
    destination = Column(String(200))
    estimated_mileage = Column(Float)
    actual_mileage = Column(Float, nullable=True)
    
    driver_name = Column(String(100))
    driver_license = Column(String(50))
    passengers = Column(Integer, default=1)
    
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="requests")
    requester = relationship("User", foreign_keys=[requester_id])
    approver = relationship("User", foreign_keys=[approved_by])


class VehicleMaintenanceLog(Base):
    __tablename__ = "vehicle_maintenance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    maintenance_type = Column(String(100))  # Oil change, tire rotation, inspection, etc.
    description = Column(Text)
    cost = Column(Float)
    maintenance_date = Column(DateTime, nullable=False)
    next_due_date = Column(DateTime, nullable=True)
    mileage_at_service = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="maintenance_logs")


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # Toner, Keyboards, Monitors, etc.
    description = Column(Text)
    sku = Column(String(50), unique=True)
    quantity_on_hand = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    unit_cost = Column(Float)
    supplier = Column(String(100))
    location = Column(String(100))  # Storage location
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = relationship("InventoryTransaction", back_populates="item")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(String(20))  # "in" or "out"
    quantity = Column(Integer)
    reason = Column(String(200))  # "Restock", "Ticket #1234", "Damage", etc.
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    item = relationship("InventoryItem", back_populates="transactions")
    user = relationship("User")


class KnowledgeBaseCategory(Base):
    __tablename__ = "kb_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), unique=True)
    description = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship("KnowledgeBaseArticle", back_populates="category")


class KnowledgeBaseArticle(Base):
    __tablename__ = "kb_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("kb_categories.id"), nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    is_published = Column(Boolean, default=True)
    views = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    unhelpful_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("KnowledgeBaseCategory", back_populates="articles")
    author = relationship("User")


class BrandingSettings(Base):
    __tablename__ = "branding_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Organization Info
    organization_name = Column(String(200), default="District IT Help Desk")
    logo_url = Column(String(500))  # URL to uploaded logo
    favicon_url = Column(String(500))
    
    # Color Scheme
    primary_color = Column(String(7), default="#667eea")  # Hex color
    secondary_color = Column(String(7), default="#764ba2")
    accent_color = Column(String(7), default="#05b981")
    danger_color = Column(String(7), default="#f02316")
    warning_color = Column(String(7), default="#f59e0b")
    success_color = Column(String(7), default="#05b981")
    
    # Typography
    font_family = Column(String(100), default="Inter")  # Font name
    heading_font = Column(String(100), default="Inter")
    
    # Additional Styling
    custom_css = Column(Text)  # Custom CSS overrides
    
    # Footer
    footer_text = Column(String(500))
    support_email = Column(String(100))
    support_phone = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
