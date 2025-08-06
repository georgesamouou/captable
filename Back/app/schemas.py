from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, AuditAction


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime


# Shareholder schemas
class ShareholderProfileBase(BaseSchema):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None


class ShareholderProfileCreate(ShareholderProfileBase):
    email: EmailStr
    password: str


class ShareholderProfileUpdate(ShareholderProfileBase):
    pass


class ShareholderProfileResponse(ShareholderProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ShareholderWithShares(ShareholderProfileResponse):
    total_shares: int
    total_value: float


# Share Issuance schemas
class ShareIssuanceBase(BaseSchema):
    number_of_shares: int
    price_per_share: float
    notes: Optional[str] = None

    @validator('number_of_shares')
    def validate_shares(cls, v):
        if v <= 0:
            raise ValueError('Number of shares must be positive')
        return v

    @validator('price_per_share')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price per share cannot be negative')
        return v


class ShareIssuanceCreate(ShareIssuanceBase):
    shareholder_id: int


class ShareIssuanceResponse(ShareIssuanceBase):
    id: int
    shareholder_id: int
    total_value: float
    issuance_date: datetime
    certificate_number: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Authentication schemas
class Token(BaseSchema):
    access_token: str
    token_type: str


class TokenData(BaseSchema):
    email: Optional[str] = None


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


# Audit schemas
class AuditEventResponse(BaseSchema):
    id: int
    user_id: int
    action: AuditAction
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


# Dashboard schemas
class DashboardStats(BaseSchema):
    total_shareholders: int
    total_shares_issued: int
    total_value: float


class OwnershipDistribution(BaseSchema):
    shareholder_name: str
    shares: int
    percentage: float
    value: float 