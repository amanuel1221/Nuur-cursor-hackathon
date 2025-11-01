"""
Anti-theft protection endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import hash_keyword, verify_keyword
from app.models.user import User
from app.models.anti_theft import AntiTheftConfig, AntiTheftEvent, LocationTracking, MediaRecording
from app.schemas.anti_theft import (
    AntiTheftConfigCreate,
    AntiTheftConfigUpdate,
    AntiTheftConfigResponse,
    AntiTheftEventCreate,
    AntiTheftEventResponse,
    AntiTheftStatusResponse,
    LocationPoint
)

router = APIRouter()


@router.post("/setup", response_model=AntiTheftConfigResponse, status_code=status.HTTP_201_CREATED)
async def setup_anti_theft(
    config_data: AntiTheftConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup or update anti-theft configuration
    
    Args:
        config_data: Anti-theft configuration
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created or updated configuration
    """
    # Check if config already exists
    config = db.query(AntiTheftConfig).filter(
        AntiTheftConfig.user_id == current_user.id
    ).first()
    
    keyword_hash = hash_keyword(config_data.trigger_keyword)
    
    if config:
        # Update existing config
        config.trigger_keyword_hash = keyword_hash
        config.is_enabled = config_data.is_enabled
        config.enable_gps_tracking = config_data.enable_gps_tracking
        config.enable_audio_recording = config_data.enable_audio_recording
        config.enable_video_recording = config_data.enable_video_recording
        config.tracking_interval_seconds = config_data.tracking_interval_seconds
        config.recording_duration_minutes = config_data.recording_duration_minutes
    else:
        # Create new config
        config = AntiTheftConfig(
            user_id=current_user.id,
            trigger_keyword_hash=keyword_hash,
            is_enabled=config_data.is_enabled,
            enable_gps_tracking=config_data.enable_gps_tracking,
            enable_audio_recording=config_data.enable_audio_recording,
            enable_video_recording=config_data.enable_video_recording,
            tracking_interval_seconds=config_data.tracking_interval_seconds,
            recording_duration_minutes=config_data.recording_duration_minutes
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    
    return config


@router.get("/config", response_model=AntiTheftConfigResponse)
async def get_anti_theft_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get anti-theft configuration
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Anti-theft configuration
    
    Raises:
        HTTPException: If configuration not found
    """
    config = db.query(AntiTheftConfig).filter(
        AntiTheftConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anti-theft configuration not found. Please setup first."
        )
    
    return config


@router.post("/trigger", response_model=AntiTheftEventResponse, status_code=status.HTTP_201_CREATED)
async def trigger_anti_theft(
    trigger_data: AntiTheftEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger anti-theft (for testing or manual activation)
    
    Args:
        trigger_data: Trigger data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created anti-theft event
    
    Raises:
        HTTPException: If anti-theft not configured or disabled
    """
    # Check if anti-theft is configured
    config = db.query(AntiTheftConfig).filter(
        AntiTheftConfig.user_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anti-theft not configured"
        )
    
    if not config.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anti-theft is disabled"
        )
    
    # Create anti-theft event
    event = AntiTheftEvent(
        user_id=current_user.id,
        triggered_by=trigger_data.triggered_by,
        is_test=trigger_data.is_test,
        status="active"
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # TODO: Send alerts to emergency contacts
    # TODO: Start GPS tracking
    # TODO: Start media recording
    
    return event


@router.post("/events/{event_id}/location")
async def add_location_tracking(
    event_id: str,
    location: LocationPoint,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add location point to anti-theft event
    
    Args:
        event_id: Event ID
        location: Location point
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If event not found or not active
    """
    # Verify event belongs to user and is active
    event = db.query(AntiTheftEvent).filter(
        AntiTheftEvent.id == event_id,
        AntiTheftEvent.user_id == current_user.id,
        AntiTheftEvent.status == "active"
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active event not found"
        )
    
    # Create location tracking point
    point = WKTElement(f'POINT({location.longitude} {location.latitude})', srid=4326)
    
    tracking = LocationTracking(
        event_id=event.id,
        location=point,
        accuracy=location.accuracy,
        altitude=location.altitude,
        speed=location.speed,
        heading=location.heading,
        timestamp=location.timestamp,
        battery_level=location.battery_level
    )
    
    db.add(tracking)
    db.commit()
    
    return {"message": "Location added successfully"}


@router.post("/events/{event_id}/deactivate")
async def deactivate_anti_theft_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate anti-theft event
    
    Args:
        event_id: Event ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If event not found
    """
    event = db.query(AntiTheftEvent).filter(
        AntiTheftEvent.id == event_id,
        AntiTheftEvent.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    event.status = "deactivated"
    event.deactivated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Anti-theft deactivated successfully"}


@router.get("/status", response_model=AntiTheftStatusResponse)
async def get_anti_theft_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current anti-theft status
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Anti-theft status
    """
    # Get configuration
    config = db.query(AntiTheftConfig).filter(
        AntiTheftConfig.user_id == current_user.id
    ).first()
    
    is_enabled = config.is_enabled if config else False
    
    # Get active event
    active_event = db.query(AntiTheftEvent).filter(
        AntiTheftEvent.user_id == current_user.id,
        AntiTheftEvent.status == "active"
    ).first()
    
    location_history = []
    media_recordings = []
    
    if active_event:
        # Get location history
        locations = db.query(LocationTracking).filter(
            LocationTracking.event_id == active_event.id
        ).order_by(LocationTracking.timestamp.desc()).limit(100).all()
        
        for loc in locations:
            point = to_shape(loc.location)
            location_history.append({
                "latitude": point.y,
                "longitude": point.x,
                "accuracy": loc.accuracy,
                "altitude": loc.altitude,
                "speed": loc.speed,
                "heading": loc.heading,
                "timestamp": loc.timestamp,
                "battery_level": loc.battery_level
            })
        
        # Get media recordings
        media_recordings = db.query(MediaRecording).filter(
            MediaRecording.event_id == active_event.id
        ).all()
    
    return {
        "is_enabled": is_enabled,
        "active_event": active_event,
        "location_history": location_history,
        "media_recordings": media_recordings
    }


@router.get("/events", response_model=List[AntiTheftEventResponse])
async def get_anti_theft_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get anti-theft event history
    
    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of events to return
    
    Returns:
        List of events
    """
    events = db.query(AntiTheftEvent).filter(
        AntiTheftEvent.user_id == current_user.id
    ).order_by(AntiTheftEvent.trigger_time.desc()).limit(limit).all()
    
    return events

