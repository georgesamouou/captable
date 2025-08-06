from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_admin_user, get_current_shareholder_user
from app.models import User
from app.schemas import ShareIssuanceCreate, ShareIssuanceResponse
from app.services import ShareIssuanceService, AuditService
from app.models import AuditAction
from app.pdf_generator import PDFCertificateGenerator
from io import BytesIO

router = APIRouter(prefix="/api/issuances", tags=["issuances"])


@router.get("/", response_model=List[ShareIssuanceResponse])
async def get_issuances(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all share issuances (Admin only)"""
    return ShareIssuanceService.get_all_issuances(db)


@router.get("/my", response_model=List[ShareIssuanceResponse])
async def get_my_issuances(
    current_user: User = Depends(get_current_shareholder_user),
    db: Session = Depends(get_db)
):
    """Get current shareholder's issuances"""
    return ShareIssuanceService.get_shareholder_issuances(db, current_user.id)


@router.post("/", response_model=ShareIssuanceResponse)
async def create_issuance(
    issuance_data: ShareIssuanceCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Create a new share issuance (Admin only)"""
    try:
        issuance = ShareIssuanceService.create_issuance(db, issuance_data)
        
        # Log the event
        AuditService.log_event(
            db=db,
            user_id=current_user.id,
            action=AuditAction.SHARE_ISSUANCE,
            details=f"Issued {issuance.number_of_shares} shares to shareholder ID {issuance.shareholder_id}",
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        
        return issuance
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the issuance"
        )


@router.get("/{issuance_id}/certificate/")
async def get_certificate(
    issuance_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Generate PDF certificate for a share issuance (Admin only)"""
    issuance = ShareIssuanceService.get_issuance_by_id(db, issuance_id)
    if not issuance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issuance not found"
        )
    
    # Get shareholder details
    from app.models import ShareholderProfile
    shareholder = db.query(ShareholderProfile).filter(
        ShareholderProfile.id == issuance.shareholder_id
    ).first()
    
    if not shareholder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shareholder not found"
        )
    
    # Generate PDF
    pdf_generator = PDFCertificateGenerator()
    pdf_bytes = pdf_generator.generate_certificate_pdf(issuance, shareholder)
    
    # Return PDF as streaming response
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{issuance.certificate_number}.pdf"
        }
    )


@router.get("/{issuance_id}/certificate/my/")
async def get_my_certificate(
    issuance_id: int,
    current_user: User = Depends(get_current_shareholder_user),
    db: Session = Depends(get_db)
):
    """Generate PDF certificate for current shareholder's issuance"""
    # Get shareholder profile
    from app.services import ShareholderService
    shareholder = ShareholderService.get_shareholder_by_user_id(db, current_user.id)
    if not shareholder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shareholder profile not found"
        )
    
    # Get issuance and verify ownership
    issuance = ShareIssuanceService.get_issuance_by_id(db, issuance_id)
    if not issuance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issuance not found"
        )
    
    if issuance.shareholder_id != shareholder.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this certificate"
        )
    
    # Generate PDF
    pdf_generator = PDFCertificateGenerator()
    pdf_bytes = pdf_generator.generate_certificate_pdf(issuance, shareholder)
    
    # Return PDF as streaming response
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=certificate_{issuance.certificate_number}.pdf"
        }
    ) 