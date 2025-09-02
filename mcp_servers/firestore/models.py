"""
Pydantic models for Firestore data structures.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    GUEST = "guest"
    HOST = "host"
    ADMIN = "admin"


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PropertyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class User(BaseModel):
    uid: str
    name: str
    email: str  # unique constraint
    role: UserRole
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    last_login: Optional[datetime] = None


class Location(BaseModel):
    address: str
    city: str
    country: str
    lat: float
    lng: float


class Property(BaseModel):
    property_id: str
    user_id: str  # host FK
    name: str
    description: str
    status: PropertyStatus
    location: Location
    minimum_price: float
    property_type: str
    guest_space: int
    check_in_time: str  # "15:00"
    check_out_time: str  # "11:00"
    prices: Dict[str, float]  # {"weekday": 100, "weekend": 150}
    amenities: List[str]
    images: List[str]
    created_at: datetime
    updated_at: datetime


class Booking(BaseModel):
    booking_id: str
    property_id: str
    host_id: str
    guest_id: str
    check_in_date: datetime
    check_out_date: datetime
    number_of_guests: int
    total_price: float
    status: BookingStatus
    add_ons: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    review: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @field_validator('check_out_date')
    @classmethod
    def validate_dates(cls, v: datetime, info) -> datetime:
        if 'check_in_date' in info.data and v <= info.data['check_in_date']:
            raise ValueError('check_out_date must be after check_in_date')
        return v


class FeaturePackage(BaseModel):
    package_id: str
    name: str
    description: str
    features: List[str]
    price: float
    duration_days: int
    status: str
    index: int
    created_at: datetime


class SessionState(BaseModel):
    """Session state for conversation tracking."""
    session_id: str
    user_id: Optional[str] = None
    current_agent: str = "inquiry"
    slots: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    ttl_minutes: int = 30