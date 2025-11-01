"""
Path tracking schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class PathPointCreate(BaseModel):
    """Path point creation schema"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime


class PathPointResponse(BaseModel):
    """Path point response schema"""
    id: int
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime


class PathCreate(BaseModel):
    """Path creation schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    path_type: Optional[str] = "other"


class PathUpdate(BaseModel):
    """Path update schema"""
    name: Optional[str] = None
    description: Optional[str] = None


class PathResponse(BaseModel):
    """Path response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    name: Optional[str] = None
    description: Optional[str] = None
    path_type: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool
    total_distance_meters: Optional[float] = None
    average_speed_mps: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PathDetailResponse(PathResponse):
    """Path detail response with points"""
    points: List[PathPointResponse] = []


class PathShareCreate(BaseModel):
    """Path share creation schema"""
    shared_with_email: Optional[str] = None
    shared_with_phone: Optional[str] = None
    expires_in_hours: int = 24


class PathShareResponse(BaseModel):
    """Path share response schema"""
    id: uuid.UUID
    path_id: uuid.UUID
    share_token: str
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

