from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models.models import Asset, InstalledSoftware, CVEAlert, UpdateStatus
from ..schemas.schemas import AssetCreate, AssetOut, AssetListOut, CVEAlertOut, UpdateStatusOut
from ..utils.auth import get_current_user, require_technician_or_admin

router = APIRouter(prefix="/api/assets", tags=["Assets / ITAM"])


@router.get("/", response_model=List[AssetListOut])
def list_assets(
    search: Optional[str] = None,
    device_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Asset)

    if search:
        query = query.filter(
            or_(
                Asset.asset_tag.ilike(f"%{search}%"),
                Asset.hostname.ilike(f"%{search}%"),
                Asset.ip_address.ilike(f"%{search}%"),
                Asset.assigned_user.ilike(f"%{search}%")
            )
        )
    if device_type:
        query = query.filter(Asset.device_type == device_type)
    if is_active is not None:
        query = query.filter(Asset.is_active == is_active)

    return query.order_by(Asset.updated_at.desc()).offset(skip).limit(limit).all()


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    asset = db.query(Asset).options(
        joinedload(Asset.software),
        joinedload(Asset.cve_alerts),
        joinedload(Asset.update_status)
    ).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.get("/{asset_id}/cves", response_model=List[CVEAlertOut])
def get_asset_cves(
    asset_id: int,
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(CVEAlert).filter(CVEAlert.asset_id == asset_id)

    if severity:
        query = query.filter(CVEAlert.cvss_severity == severity)
    if acknowledged is not None:
        query = query.filter(CVEAlert.is_acknowledged == acknowledged)

    return query.order_by(CVEAlert.cvss_score.desc()).all()


@router.put("/{asset_id}/cves/{cve_id}/acknowledge", status_code=status.HTTP_204_NO_CONTENT)
def acknowledge_cve(
    asset_id: int,
    cve_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_technician_or_admin)
):
    alert = db.query(CVEAlert).filter(
        CVEAlert.asset_id == asset_id,
        CVEAlert.cve_id == cve_id
    ).first()

    if not alert:
        raise HTTPException(status_code=404, detail="CVE alert not found")

    alert.is_acknowledged = True
    alert.acknowledged_by = current_user.full_name
    alert.acknowledged_at = datetime.utcnow()
    db.commit()


@router.put("/{asset_id}", response_model=AssetOut)
def update_asset(
    asset_id: int,
    asset_in: AssetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_technician_or_admin)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    for key, value in asset_in.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)

    asset.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(asset)

    return db.query(Asset).options(
        joinedload(Asset.software),
        joinedload(Asset.cve_alerts),
        joinedload(Asset.update_status)
    ).filter(Asset.id == asset_id).first()


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_technician_or_admin)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
