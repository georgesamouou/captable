from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SHAREHOLDER = "shareholder"


class AuditAction(str, enum.Enum):
    LOGIN = "login"
    SHARE_ISSUANCE = "share_issuance"
    SHAREHOLDER_CREATED = "shareholder_created"
    SHAREHOLDER_UPDATED = "shareholder_updated"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(String, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    shareholder_profile = relationship("ShareholderProfile", back_populates="user", uselist=False)
    audit_events = relationship("AuditEvent", back_populates="user")


class ShareholderProfile(Base):
    __tablename__ = "shareholder_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(Text)
    tax_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="shareholder_profile")
    share_issuances = relationship("ShareIssuance", back_populates="shareholder")


class ShareIssuance(Base):
    __tablename__ = "share_issuances"

    id = Column(Integer, primary_key=True, index=True)
    shareholder_id = Column(Integer, ForeignKey("shareholder_profiles.id"), nullable=False)
    number_of_shares = Column(Integer, nullable=False)
    price_per_share = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    issuance_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    certificate_number = Column(String, unique=True, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    shareholder = relationship("ShareholderProfile", back_populates="share_issuances")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    details = Column(Text)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_events") 