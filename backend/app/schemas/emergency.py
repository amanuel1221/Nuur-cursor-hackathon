"""
Emergency reporting schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import uuid


class EmergencyReportCreate(BaseModel):
    """Emergency report creation schema"""
    report_type: str
    latitude: float
    longitude: float
    address_text: Optional[str] = None
    description: Optional[str] = None
    is_anonymous: bool = False
    severity: Optional[str] = "medium"
    
    @validator("report_type")
    def validate_report_type(cls, v):
        valid_types = ["fire", "medical", "accident", "security", "other"]
        if v not in valid_types:
            raise ValueError(f"Report type must be one of: {', '.join(valid_types)}")
        return v
    
    @validator("severity")
    def validate_severity(cls, v):
        valid_severities = ["low", "medium", "high", "critical"]
        if v not in valid_severities:
            raise ValueError(f"Severity must be one of: {', '.join(valid_severities)}")
        return v


class EmergencyReportUpdate(BaseModel):
    """Emergency report update schema"""
    status: Optional[str] = None
    description: Optional[str] = None
    
    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["pending", "acknowledged", "responding", "resolved", "cancelled"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class EmergencyReportMediaResponse(BaseModel):
    """Emergency report media response schema"""
    id: uuid.UUID
    report_id: uuid.UUID
    media_type: str
    file_url: str
    file_size_bytes: Optional[int] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class EmergencyReportResponse(BaseModel):
    """Emergency report response schema"""
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    report_type: str
    latitude: float
    longitude: float
    address_text: Optional[str] = None
    description: Optional[str] = None
    status: str
    is_anonymous: bool
    severity: Optional[str] = None
    reported_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmergencyReportDetailResponse(EmergencyReportResponse):
    """Emergency report detail response with media"""
    media: List[EmergencyReportMediaResponse] = []


class EmergencyContactCreate(BaseModel):
    """Emergency contact creation schema"""
    contact_name: str
    phone_number: str
    email: Optional[str] = None
    relationship_type: Optional[str] = None
    priority: int = 1


class EmergencyContactUpdate(BaseModel):
    """Emergency contact update schema"""
    contact_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    relationship_type: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class EmergencyContactResponse(BaseModel):
    """Emergency contact response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    contact_name: str
    phone_number: str
    email: Optional[str] = None
    relationship_type: Optional[str] = None
    priority: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

