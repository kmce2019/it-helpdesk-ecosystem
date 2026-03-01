from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.models import SLA
from ..schemas.schemas import SLACreate, SLAOut
from ..utils.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/slas", tags=["SLAs"])


@router.get("/", response_model=List[SLAOut])
def list_slas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(SLA).all()


@router.post("/", response_model=SLAOut, status_code=status.HTTP_201_CREATED)
def create_sla(sla_in: SLACreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if db.query(SLA).filter(SLA.priority == sla_in.priority).first():
        raise HTTPException(status_code=400, detail="SLA for this priority already exists")
    sla = SLA(**sla_in.model_dump())
    db.add(sla)
    db.commit()
    db.refresh(sla)
    return sla


@router.put("/{sla_id}", response_model=SLAOut)
def update_sla(sla_id: int, sla_in: SLACreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    sla = db.query(SLA).filter(SLA.id == sla_id).first()
    if not sla:
        raise HTTPException(status_code=404, detail="SLA not found")
    for key, value in sla_in.model_dump().items():
        setattr(sla, key, value)
    db.commit()
    db.refresh(sla)
    return sla


@router.delete("/{sla_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sla(sla_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    sla = db.query(SLA).filter(SLA.id == sla_id).first()
    if not sla:
        raise HTTPException(status_code=404, detail="SLA not found")
    db.delete(sla)
    db.commit()
