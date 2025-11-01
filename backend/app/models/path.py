"""
Path tracking models
"""
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from app.core.database import Base


class Path(Base):
    """Path tracking model"""
    
    __tablename__ = "paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200))
    description = Column(String)
    path_type = Column(String(20))  # walk, commute, taxi, other
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=False)
    total_distance_meters = Column(Float)
    average_speed_mps = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="paths")
    points = relationship("PathPoint", back_populates="path", cascade="all, delete-orphan", order_by="PathPoint.timestamp")
    shared_with = relationship("SharedPath", back_populates="path", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Path id={self.id} name={self.name}>"


class PathPoint(Base):
    """Path point model"""
    
    __tablename__ = "path_points"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    path_id = Column(UUID(as_uuid=True), ForeignKey("paths.id", ondelete="CASCADE"), nullable=False, index=True)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    accuracy = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    heading = Column(Float)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Relationships
    path = relationship("Path", back_populates="points")
    
    def __repr__(self):
        return f"<PathPoint path_id={self.path_id} timestamp={self.timestamp}>"


class SharedPath(Base):
    """Shared path model"""
    
    __tablename__ = "shared_paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_id = Column(UUID(as_uuid=True), ForeignKey("paths.id", ondelete="CASCADE"), nullable=False)
    shared_with_email = Column(String(255))
    shared_with_phone = Column(String(20))
    share_token = Column(String(100), unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    path = relationship("Path", back_populates="shared_with")
    
    def __repr__(self):
        return f"<SharedPath path_id={self.path_id} token={self.share_token}>"

