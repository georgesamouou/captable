from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
import uuid
from app.models import User, ShareholderProfile, ShareIssuance, AuditEvent, AuditAction, UserRole
from app.schemas import ShareholderProfileCreate, ShareIssuanceCreate
from app.auth import get_password_hash


class ShareholderService:
    @staticmethod
    def create_shareholder(db: Session, shareholder_data: ShareholderProfileCreate) -> ShareholderProfile:
        """Create a new shareholder with user account"""
        # Create user account
        user = User(
            email=shareholder_data.email,
            hashed_password=get_password_hash(shareholder_data.password),
            role=UserRole.SHAREHOLDER
        )
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create shareholder profile
        shareholder = ShareholderProfile(
            user_id=user.id,
            first_name=shareholder_data.first_name,
            last_name=shareholder_data.last_name,
            phone=shareholder_data.phone,
            address=shareholder_data.address,
            tax_id=shareholder_data.tax_id
        )
        db.add(shareholder)
        db.commit()
        db.refresh(shareholder)
        return shareholder

    @staticmethod
    def get_all_shareholders_with_shares(db: Session) -> List[dict]:
        """Get all shareholders with their total shares and value"""
        result = db.query(
            ShareholderProfile,
            func.coalesce(func.sum(ShareIssuance.number_of_shares), 0).label('total_shares'),
            func.coalesce(func.sum(ShareIssuance.total_value), 0).label('total_value')
        ).outerjoin(ShareIssuance).group_by(ShareholderProfile.id).all()
        
        return [
            {
                "id": shareholder.id,
                "first_name": shareholder.first_name,
                "last_name": shareholder.last_name,
                "email": shareholder.user.email,
                "total_shares": int(total_shares),
                "total_value": float(total_value)
            }
            for shareholder, total_shares, total_value in result
        ]

    @staticmethod
    def get_shareholder_by_user_id(db: Session, user_id: int) -> Optional[ShareholderProfile]:
        """Get shareholder profile by user ID"""
        return db.query(ShareholderProfile).filter(ShareholderProfile.user_id == user_id).first()


class ShareIssuanceService:
    @staticmethod
    def create_issuance(db: Session, issuance_data: ShareIssuanceCreate) -> ShareIssuance:
        """Create a new share issuance"""
        # Validate shareholder exists
        shareholder = db.query(ShareholderProfile).filter(
            ShareholderProfile.id == issuance_data.shareholder_id
        ).first()
        if not shareholder:
            raise ValueError("Shareholder not found")
        
        # Calculate total value
        total_value = issuance_data.number_of_shares * issuance_data.price_per_share
        
        # Generate certificate number
        certificate_number = f"CERT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create issuance
        issuance = ShareIssuance(
            shareholder_id=issuance_data.shareholder_id,
            number_of_shares=issuance_data.number_of_shares,
            price_per_share=issuance_data.price_per_share,
            total_value=total_value,
            certificate_number=certificate_number,
            notes=issuance_data.notes
        )
        db.add(issuance)
        db.commit()
        db.refresh(issuance)
        return issuance

    @staticmethod
    def get_all_issuances(db: Session) -> List[ShareIssuance]:
        """Get all share issuances (admin only)"""
        return db.query(ShareIssuance).all()

    @staticmethod
    def get_shareholder_issuances(db: Session, user_id: int) -> List[ShareIssuance]:
        """Get issuances for a specific shareholder"""
        return db.query(ShareIssuance).join(ShareholderProfile).filter(
            ShareholderProfile.user_id == user_id
        ).all()

    @staticmethod
    def get_issuance_by_id(db: Session, issuance_id: int) -> Optional[ShareIssuance]:
        """Get issuance by ID"""
        return db.query(ShareIssuance).filter(ShareIssuance.id == issuance_id).first()


class AuditService:
    @staticmethod
    def log_event(
        db: Session, 
        user_id: int, 
        action: AuditAction, 
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEvent:
        """Log an audit event"""
        audit_event = AuditEvent(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_event)
        db.commit()
        db.refresh(audit_event)
        return audit_event

    @staticmethod
    def get_audit_logs(db: Session, limit: int = 100) -> List[AuditEvent]:
        """Get recent audit logs"""
        return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).all()


class DashboardService:
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        """Get dashboard statistics"""
        total_shareholders = db.query(ShareholderProfile).count()
        
        shares_result = db.query(
            func.coalesce(func.sum(ShareIssuance.number_of_shares), 0).label('total_shares'),
            func.coalesce(func.sum(ShareIssuance.total_value), 0).label('total_value')
        ).first()
        
        return {
            "total_shareholders": total_shareholders,
            "total_shares_issued": int(shares_result.total_shares),
            "total_value": float(shares_result.total_value)
        }

    @staticmethod
    def get_ownership_distribution(db: Session) -> List[dict]:
        """Get ownership distribution for pie chart"""
        # Get total shares for percentage calculation
        total_shares_result = db.query(
            func.coalesce(func.sum(ShareIssuance.number_of_shares), 0)
        ).scalar()
        total_shares = int(total_shares_result) if total_shares_result else 0
        
        if total_shares == 0:
            return []
        
        # Get distribution
        result = db.query(
            ShareholderProfile,
            func.coalesce(func.sum(ShareIssuance.number_of_shares), 0).label('shares'),
            func.coalesce(func.sum(ShareIssuance.total_value), 0).label('value')
        ).outerjoin(ShareIssuance).group_by(ShareholderProfile.id).all()
        
        return [
            {
                "shareholder_name": f"{shareholder.first_name} {shareholder.last_name}",
                "shares": int(shares),
                "percentage": round((shares / total_shares) * 100, 2),
                "value": float(value)
            }
            for shareholder, shares, value in result
            if shares > 0
        ] 