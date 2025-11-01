"""
Emergency reporting models
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.core.database import Base


class EmergencyReport(Base):
    """Emergency report model"""
    
    __tablename__ = "emergency_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    report_type = Column(String(20), nullable=False, index=True)  # fire, medical, accident, security, other
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    address_text = Column(String)
    description = Column(String)
    status = Column(String(20), default="pending", index=True)  # pending, acknowledged, responding, resolved, cancelled
    is_anonymous = Column(Boolean, default=False)
    severity = Column(String(10))  # low, medium, high, critical
    reported_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emergency_reports")
    media = relationship("EmergencyReportMedia", back_populates="report", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EmergencyReport id={self.id} type={self.report_type} status={self.status}>"


class EmergencyReportMedia(Base):
    """Emergency report media model"""
    
    __tablename__ = "emergency_report_media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("emergency_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(10), nullable=False)  # photo, video, audio
    file_url = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    report = relationship("EmergencyReport", back_populates="media")
    
    def __repr__(self):
        return f"<EmergencyReportMedia report_id={self.report_id} type={self.media_type}>"

