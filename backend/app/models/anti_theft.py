"""
Anti-theft related models
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.core.database import Base


class AntiTheftConfig(Base):
    """Anti-theft configuration model"""
    
    __tablename__ = "anti_theft_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    trigger_keyword_hash = Column(String(255), nullable=False)
    is_enabled = Column(Boolean, default=True)
    enable_gps_tracking = Column(Boolean, default=True)
    enable_audio_recording = Column(Boolean, default=True)
    enable_video_recording = Column(Boolean, default=False)
    tracking_interval_seconds = Column(Integer, default=30)
    recording_duration_minutes = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="anti_theft_config")
    
    def __repr__(self):
        return f"<AntiTheftConfig user_id={self.user_id} enabled={self.is_enabled}>"


class AntiTheftEvent(Base):
    """Anti-theft event model"""
    
    __tablename__ = "anti_theft_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    triggered_by = Column(String(20))
    trigger_time = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), default="active", index=True)  # active, deactivated, resolved
    is_test = Column(Boolean, default=False)
    deactivated_at = Column(DateTime)
    notes = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="anti_theft_events")
    location_tracking = relationship("LocationTracking", back_populates="event", cascade="all, delete-orphan")
    media_recordings = relationship("MediaRecording", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AntiTheftEvent id={self.id} status={self.status}>"


class LocationTracking(Base):
    """Location tracking model for anti-theft events"""
    
    __tablename__ = "location_tracking"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("anti_theft_events.id", ondelete="CASCADE"), nullable=False, index=True)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    accuracy = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    heading = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    battery_level = Column(Integer)
    
    # Relationships
    event = relationship("AntiTheftEvent", back_populates="location_tracking")
    
    def __repr__(self):
        return f"<LocationTracking event_id={self.event_id} timestamp={self.timestamp}>"


class MediaRecording(Base):
    """Media recording model for anti-theft events"""
    
    __tablename__ = "media_recordings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("anti_theft_events.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(10), nullable=False)  # audio, video, photo
    file_url = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger)
    duration_seconds = Column(Integer)
    encryption_key_id = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    event = relationship("AntiTheftEvent", back_populates="media_recordings")
    
    def __repr__(self):
        return f"<MediaRecording id={self.id} type={self.media_type}>"

