from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_admin_user
from app.models import User
from app.schemas import AuditEventResponse
from app.services import AuditService

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/", response_model=List[AuditEventResponse])
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of audit logs to return"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get audit logs (Admin only)"""
    return AuditService.get_audit_logs(db, limit=limit) 