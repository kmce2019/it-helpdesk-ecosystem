"""
Extended Pydantic schemas for Vehicle Requests, Inventory, Knowledge Base, and Branding
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ─── Vehicle Schemas ────────────────────────────────────────────────────────

class VehicleBase(BaseModel):
    name: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: str
    vin: str
    capacity: Optional[int] = None
    notes: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    current_mileage: Optional[float] = None
    last_maintenance: Optional[datetime] = None
    notes: Optional[str] = None


class VehicleResponse(VehicleBase):
    id: int
    status: str
    current_mileage: float
    last_maintenance: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Vehicle Request Schemas ───────────────────────────────────────────────

class VehicleRequestBase(BaseModel):
    start_date: datetime
    end_date: datetime
    purpose: str
    destination: Optional[str] = None
    estimated_mileage: Optional[float] = None
    driver_name: str
    driver_license: str
    passengers: int = 1


class VehicleRequestCreate(VehicleRequestBase):
    pass


class VehicleRequestUpdate(BaseModel):
    status: Optional[str] = None
    actual_mileage: Optional[float] = None
    approval_notes: Optional[str] = None


class VehicleRequestApprove(BaseModel):
    vehicle_id: int
    approval_notes: Optional[str] = None


class VehicleRequestResponse(VehicleRequestBase):
    id: int
    requester_id: int
    vehicle_id: Optional[int]
    status: str
    actual_mileage: Optional[float]
    approved_by: Optional[int]
    approval_date: Optional[datetime]
    approval_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Vehicle Maintenance Schemas ───────────────────────────────────────────

class VehicleMaintenanceLogCreate(BaseModel):
    vehicle_id: int
    maintenance_type: str
    description: Optional[str] = None
    cost: Optional[float] = None
    maintenance_date: datetime
    next_due_date: Optional[datetime] = None
    mileage_at_service: Optional[float] = None


class VehicleMaintenanceLogResponse(BaseModel):
    id: int
    vehicle_id: int
    maintenance_type: str
    description: Optional[str]
    cost: Optional[float]
    maintenance_date: datetime
    next_due_date: Optional[datetime]
    mileage_at_service: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Inventory Schemas ─────────────────────────────────────────────────────

class InventoryItemBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    sku: str
    quantity_on_hand: int
    reorder_level: int = 10
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None
    location: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity_on_hand: Optional[int] = None
    reorder_level: Optional[int] = None
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None
    location: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    item_id: int
    transaction_type: str  # "in" or "out"
    quantity: int
    reason: str


class InventoryTransactionResponse(BaseModel):
    id: int
    item_id: int
    transaction_type: str
    quantity: int
    reason: str
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Knowledge Base Schemas ────────────────────────────────────────────────

class KnowledgeBaseCategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0


class KnowledgeBaseCategoryCreate(KnowledgeBaseCategoryBase):
    pass


class KnowledgeBaseCategoryResponse(KnowledgeBaseCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBaseArticleBase(BaseModel):
    category_id: int
    title: str
    slug: str
    content: str
    is_published: bool = True


class KnowledgeBaseArticleCreate(KnowledgeBaseArticleBase):
    pass


class KnowledgeBaseArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None


class KnowledgeBaseArticleResponse(KnowledgeBaseArticleBase):
    id: int
    author_id: Optional[int]
    views: int
    helpful_count: int
    unhelpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBaseArticleDetail(KnowledgeBaseArticleResponse):
    category: Optional[KnowledgeBaseCategoryResponse] = None


# ─── Branding Schemas ──────────────────────────────────────────────────────

class BrandingSettingsBase(BaseModel):
    organization_name: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    danger_color: Optional[str] = None
    warning_color: Optional[str] = None
    success_color: Optional[str] = None
    font_family: Optional[str] = None
    heading_font: Optional[str] = None
    custom_css: Optional[str] = None
    footer_text: Optional[str] = None
    support_email: Optional[str] = None
    support_phone: Optional[str] = None


class BrandingSettingsCreate(BrandingSettingsBase):
    pass


class BrandingSettingsUpdate(BrandingSettingsBase):
    pass


class BrandingSettingsResponse(BrandingSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
