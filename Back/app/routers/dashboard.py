from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_admin_user
from app.models import User
from app.schemas import DashboardStats, OwnershipDistribution
from app.services import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (Admin only)"""
    return DashboardService.get_dashboard_stats(db)


@router.get("/ownership-distribution", response_model=List[OwnershipDistribution])
async def get_ownership_distribution(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get ownership distribution for pie chart (Admin only)"""
    return DashboardService.get_ownership_distribution(db) 