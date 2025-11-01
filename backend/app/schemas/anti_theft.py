"""
Anti-theft schemas
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import uuid


class AntiTheftConfigBase(BaseModel):
    """Base anti-theft config schema"""
    trigger_keyword: str
    is_enabled: bool = True
    enable_gps_tracking: bool = True
    enable_audio_recording: bool = True
    enable_video_recording: bool = False
    tracking_interval_seconds: int = 30
    recording_duration_minutes: int = 5


class AntiTheftConfigCreate(AntiTheftConfigBase):
    """Anti-theft config creation schema"""
    
    @validator("trigger_keyword")
    def validate_keyword(cls, v):
        if len(v) < 4:
            raise ValueError("Trigger keyword must be at least 4 characters")
        return v
    
    @validator("recording_duration_minutes")
    def validate_duration(cls, v):
        if v < 1 or v > 30:
            raise ValueError("Recording duration must be between 1 and 30 minutes")
        return v


class AntiTheftConfigUpdate(BaseModel):
    """Anti-theft config update schema"""
    trigger_keyword: Optional[str] = None
    is_enabled: Optional[bool] = None
    enable_gps_tracking: Optional[bool] = None
    enable_audio_recording: Optional[bool] = None
    enable_video_recording: Optional[bool] = None
    tracking_interval_seconds: Optional[int] = None
    recording_duration_minutes: Optional[int] = None


class AntiTheftConfigResponse(BaseModel):
    """Anti-theft config response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    is_enabled: bool
    enable_gps_tracking: bool
    enable_audio_recording: bool
    enable_video_recording: bool
    tracking_interval_seconds: int
    recording_duration_minutes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LocationPoint(BaseModel):
    """Location point schema"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: datetime
    battery_level: Optional[int] = None


class AntiTheftEventCreate(BaseModel):
    """Anti-theft event creation schema"""
    triggered_by: str
    is_test: bool = False


class AntiTheftEventResponse(BaseModel):
    """Anti-theft event response schema"""
    id: uuid.UUID
    user_id: uuid.UUID
    triggered_by: str
    trigger_time: datetime
    status: str
    is_test: bool
    deactivated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MediaRecordingResponse(BaseModel):
    """Media recording response schema"""
    id: uuid.UUID
    event_id: uuid.UUID
    media_type: str
    file_url: str
    file_size_bytes: Optional[int] = None
    duration_seconds: Optional[int] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class AntiTheftStatusResponse(BaseModel):
    """Anti-theft status response schema"""
    is_enabled: bool
    active_event: Optional[AntiTheftEventResponse] = None
    location_history: List[LocationPoint] = []
    media_recordings: List[MediaRecordingResponse] = []

