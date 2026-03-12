"""Business models — ORM and Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Enum as SAEnum
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
import enum

Base = declarative_base()


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Business(Base):
    """SQLAlchemy ORM model for a registered business."""
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    website = Column(String(300), nullable=True)
    owner_id = Column(Integer, nullable=True)          # foreign key to auth-service user
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    verification_status = Column(
        SAEnum(VerificationStatus, name="verificationstatus"),
        default=VerificationStatus.PENDING
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Pydantic schemas ──────────────────────────────────────────

class BusinessCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class BusinessResponse(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    website: Optional[str]
    owner_id: Optional[int]
    rating: float
    review_count: int
    is_active: bool
    verification_status: VerificationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[BusinessResponse]


BUSINESS_CATEGORIES = [
    "restaurant", "cafe", "retail", "grocery", "pharmacy",
    "salon", "spa", "gym", "clinic", "hospital",
    "hotel", "lodge", "event_venue", "catering",
    "auto_service", "electronics", "fashion", "jewellery",
    "real_estate", "interior_design", "photography",
    "education", "coaching", "legal", "accounting",
    "logistics", "travel", "entertainment", "other"
]
