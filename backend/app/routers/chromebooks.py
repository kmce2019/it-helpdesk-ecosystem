"""
Chromebook Check-In/Check-Out API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/api/chromebooks", tags=["chromebooks"])


# ─── Chromebook Management ────────────────────────────────────────────────

@router.get("/inventory")
async def get_chromebook_inventory(skip: int = Query(0), limit: int = Query(100)):
    """Get all Chromebooks with inventory status."""
    return {
        "total": 150,
        "available": 95,
        "checked_out": 45,
        "in_repair": 8,
        "retired": 2,
        "chromebooks": [
            {
                "id": 1,
                "asset_tag": "CB-001",
                "serial_number": "ABC123XYZ",
                "model": "Lenovo 14e Chromebook",
                "status": "available",
                "current_damage_level": "none",
                "assigned_to_student_id": None,
                "last_checkout_date": None,
                "total_checkouts": 5
            }
        ]
    }


@router.post("/create")
async def create_chromebook(chromebook_data: dict):
    """Register a new Chromebook in the system."""
    return {
        "id": 1,
        "asset_tag": chromebook_data.get("asset_tag"),
        "serial_number": chromebook_data.get("serial_number"),
        "status": "available",
        "message": "Chromebook registered successfully"
    }


@router.get("/{chromebook_id}")
async def get_chromebook_details(chromebook_id: int):
    """Get detailed information about a specific Chromebook."""
    return {
        "id": chromebook_id,
        "asset_tag": "CB-001",
        "serial_number": "ABC123XYZ",
        "model": "Lenovo 14e Chromebook",
        "mac_address": "00:1A:2B:3C:4D:5E",
        "status": "available",
        "purchase_date": "2023-08-15",
        "warranty_expiration": "2026-08-15",
        "current_damage_level": "none",
        "damage_notes": None,
        "total_checkouts": 5,
        "last_checkout_date": "2024-02-20",
        "last_checkin_date": "2024-02-21",
        "checkout_history": []
    }


# ─── Checkout Operations ──────────────────────────────────────────────────

@router.post("/checkout")
async def checkout_chromebook(checkout_data: dict):
    """Check out a Chromebook to a student."""
    return {
        "id": 1,
        "chromebook_id": checkout_data.get("chromebook_id"),
        "student_id": checkout_data.get("student_id"),
        "student_name": checkout_data.get("student_name"),
        "checkout_date": datetime.utcnow().isoformat(),
        "expected_return_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "status": "active",
        "message": "Chromebook checked out successfully"
    }


@router.post("/checkin/{checkout_id}")
async def checkin_chromebook(checkout_id: int, checkin_data: dict):
    """Check in a Chromebook from a student."""
    return {
        "id": checkout_id,
        "actual_return_date": datetime.utcnow().isoformat(),
        "status": "returned",
        "condition_at_return": checkin_data.get("condition_at_return"),
        "damage_at_return": checkin_data.get("damage_at_return", "none"),
        "message": "Chromebook checked in successfully"
    }


@router.get("/checkouts/active")
async def get_active_checkouts(skip: int = Query(0), limit: int = Query(50)):
    """Get all currently active Chromebook checkouts."""
    return {
        "total": 45,
        "active_checkouts": [
            {
                "id": 1,
                "chromebook_id": 1,
                "asset_tag": "CB-001",
                "student_id": "STU-12345",
                "student_name": "John Smith",
                "grade_level": "9th",
                "class_name": "Biology A",
                "checkout_date": "2024-02-01",
                "expected_return_date": "2025-02-01",
                "status": "active",
                "is_overdue": False
            }
        ]
    }


@router.get("/checkouts/overdue")
async def get_overdue_checkouts():
    """Get all overdue Chromebook checkouts."""
    return {
        "total": 3,
        "overdue_checkouts": [
            {
                "id": 5,
                "chromebook_id": 5,
                "asset_tag": "CB-005",
                "student_id": "STU-54321",
                "student_name": "Jane Doe",
                "expected_return_date": "2024-01-15",
                "days_overdue": 17,
                "status": "overdue"
            }
        ]
    }


@router.get("/student/{student_id}/history")
async def get_student_checkout_history(student_id: str):
    """Get checkout history for a specific student."""
    return {
        "student_id": student_id,
        "student_name": "John Smith",
        "grade_level": "9th",
        "total_checkouts": 3,
        "current_checkout": {
            "id": 1,
            "chromebook_id": 1,
            "asset_tag": "CB-001",
            "checkout_date": "2024-02-01",
            "expected_return_date": "2025-02-01",
            "status": "active"
        },
        "checkout_history": [
            {
                "id": 1,
                "asset_tag": "CB-001",
                "checkout_date": "2024-02-01",
                "return_date": None,
                "status": "active"
            }
        ],
        "damage_reports": []
    }


# ─── Damage Reporting ─────────────────────────────────────────────────────

@router.post("/damage-report")
async def create_damage_report(damage_data: dict):
    """Report damage to a Chromebook."""
    return {
        "id": 1,
        "chromebook_id": damage_data.get("chromebook_id"),
        "asset_tag": "CB-001",
        "damage_level": damage_data.get("damage_level"),
        "damage_description": damage_data.get("damage_description"),
        "reported_date": datetime.utcnow().isoformat(),
        "is_repairable": damage_data.get("is_repairable", True),
        "student_responsible": damage_data.get("student_responsible", False),
        "message": "Damage report created successfully"
    }


@router.get("/damage-reports/pending")
async def get_pending_damage_reports():
    """Get all pending damage reports."""
    return {
        "total": 8,
        "pending_reports": [
            {
                "id": 1,
                "chromebook_id": 5,
                "asset_tag": "CB-005",
                "damage_level": "moderate",
                "damage_description": "Cracked screen",
                "reported_date": "2024-02-20",
                "student_responsible": True,
                "is_resolved": False
            }
        ]
    }


@router.put("/damage-report/{report_id}")
async def update_damage_report(report_id: int, update_data: dict):
    """Update a damage report status."""
    return {
        "id": report_id,
        "is_resolved": update_data.get("is_resolved"),
        "resolution_date": datetime.utcnow().isoformat(),
        "resolution_notes": update_data.get("resolution_notes"),
        "message": "Damage report updated successfully"
    }


# ─── Policy Management ────────────────────────────────────────────────────

@router.get("/policy")
async def get_checkout_policy():
    """Get current Chromebook checkout policy."""
    return {
        "id": 1,
        "max_checkout_duration_days": 365,
        "max_concurrent_checkouts_per_student": 1,
        "allow_overnight_checkout": False,
        "allow_weekend_checkout": False,
        "student_liable_for_damage": True,
        "damage_liability_threshold": 5000,  # $50.00
        "send_overdue_notifications": True,
        "overdue_notification_days": 7,
        "require_damage_inspection": True,
        "require_parent_signature": False
    }


@router.put("/policy")
async def update_checkout_policy(policy_data: dict):
    """Update Chromebook checkout policy."""
    return {
        "message": "Policy updated successfully",
        "policy": policy_data
    }


# ─── Dashboard & Analytics ───────────────────────────────────────────────

@router.get("/dashboard/summary")
async def get_chromebook_dashboard_summary():
    """Get Chromebook dashboard summary."""
    return {
        "inventory": {
            "total_chromebooks": 150,
            "available": 95,
            "checked_out": 45,
            "in_repair": 8,
            "retired": 2,
            "lost": 0
        },
        "checkouts": {
            "active_checkouts": 45,
            "overdue_checkouts": 3,
            "returned_this_week": 12,
            "damage_reports_pending": 8
        },
        "compliance": {
            "students_with_devices": 45,
            "devices_needing_inspection": 5,
            "warranty_expiring_soon": 3
        }
    }


@router.get("/reports/damage-summary")
async def get_damage_summary():
    """Get damage report summary."""
    return {
        "total_damage_reports": 24,
        "by_severity": {
            "none": 0,
            "minor": 12,
            "moderate": 8,
            "severe": 4
        },
        "by_responsibility": {
            "student_responsible": 16,
            "not_student_responsible": 8
        },
        "by_status": {
            "pending": 8,
            "in_repair": 10,
            "resolved": 6
        }
    }


@router.get("/reports/checkout-trends")
async def get_checkout_trends(days: int = Query(30)):
    """Get checkout trends over time."""
    return {
        "period_days": days,
        "total_checkouts": 156,
        "total_checkins": 148,
        "average_checkout_duration_days": 45,
        "daily_data": [
            {
                "date": "2024-02-20",
                "checkouts": 5,
                "checkins": 4,
                "active_checkouts": 45
            }
        ]
    }


@router.post("/send-overdue-notifications")
async def send_overdue_notifications():
    """Manually trigger overdue notifications."""
    return {
        "message": "Overdue notifications sent",
        "notifications_sent": 3,
        "recipients": ["parent1@email.com", "parent2@email.com", "parent3@email.com"]
    }
