from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_admin_user, get_current_shareholder_user
from app.models import User
from app.schemas import (
    ShareholderProfileCreate, 
    ShareholderProfileResponse, 
    ShareholderWithShares
)
from app.services import ShareholderService, AuditService
from app.models import AuditAction

router = APIRouter(prefix="/api/shareholders", tags=["shareholders"])


@router.get("/", response_model=List[ShareholderWithShares])
async def get_all_shareholders(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all shareholders with their total shares (Admin only)"""
    return ShareholderService.get_all_shareholders_with_shares(db)


@router.post("/", response_model=ShareholderProfileResponse)
async def create_shareholder(
    shareholder_data: ShareholderProfileCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Create a new shareholder (Admin only)"""
    try:
        shareholder = ShareholderService.create_shareholder(db, shareholder_data)
        
        # Log the event
        AuditService.log_event(
            db=db,
            user_id=current_user.id,
            action=AuditAction.SHAREHOLDER_CREATED,
            details=f"Created shareholder: {shareholder.first_name} {shareholder.last_name} ({shareholder_data.email})",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        return shareholder
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=ShareholderProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_shareholder_user),
    db: Session = Depends(get_db)
):
    """Get current shareholder's profile"""
    shareholder = ShareholderService.get_shareholder_by_user_id(db, current_user.id)
    if not shareholder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shareholder profile not found"
        )
    return shareholder 