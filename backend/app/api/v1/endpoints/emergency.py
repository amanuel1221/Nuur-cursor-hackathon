"""
Emergency reporting endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.emergency import EmergencyReport, EmergencyReportMedia
from app.schemas.emergency import (
    EmergencyReportCreate,
    EmergencyReportUpdate,
    EmergencyReportResponse,
    EmergencyReportDetailResponse
)

router = APIRouter()


@router.post("/report", response_model=EmergencyReportResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency_report(
    report_data: EmergencyReportCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create emergency report
    
    Args:
        report_data: Report data
        current_user: Authenticated user (optional for anonymous reports)
        db: Database session
    
    Returns:
        Created report
    """
    # Create location point
    location = WKTElement(f'POINT({report_data.longitude} {report_data.latitude})', srid=4326)
    
    report = EmergencyReport(
        user_id=current_user.id if current_user and not report_data.is_anonymous else None,
        report_type=report_data.report_type,
        location=location,
        address_text=report_data.address_text,
        description=report_data.description,
        is_anonymous=report_data.is_anonymous,
        severity=report_data.severity,
        status="pending"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # TODO: Send alerts to emergency services
    # TODO: Notify emergency contacts
    # TODO: Trigger failsafe mechanisms
    
    # Convert location for response
    point = to_shape(report.location)
    response_data = {
        **report.__dict__,
        "latitude": point.y,
        "longitude": point.x
    }
    
    return response_data


@router.get("/reports", response_model=List[EmergencyReportResponse])
async def get_emergency_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0
):
    """
    Get user's emergency reports
    
    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of reports to return
        skip: Number of reports to skip
    
    Returns:
        List of reports
    """
    reports = db.query(EmergencyReport).filter(
        EmergencyReport.user_id == current_user.id
    ).order_by(EmergencyReport.reported_at.desc()).offset(skip).limit(limit).all()
    
    # Convert locations for response
    response_data = []
    for report in reports:
        point = to_shape(report.location)
        response_data.append({
            **report.__dict__,
            "latitude": point.y,
            "longitude": point.x
        })
    
    return response_data


@router.get("/reports/{report_id}", response_model=EmergencyReportDetailResponse)
async def get_emergency_report_detail(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get emergency report details
    
    Args:
        report_id: Report ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Report details
    
    Raises:
        HTTPException: If report not found
    """
    report = db.query(EmergencyReport).filter(
        EmergencyReport.id == report_id,
        EmergencyReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get media
    media = db.query(EmergencyReportMedia).filter(
        EmergencyReportMedia.report_id == report.id
    ).all()
    
    # Convert location for response
    point = to_shape(report.location)
    
    return {
        **report.__dict__,
        "latitude": point.y,
        "longitude": point.x,
        "media": media
    }


@router.put("/reports/{report_id}/status", response_model=EmergencyReportResponse)
async def update_report_status(
    report_id: str,
    status_update: EmergencyReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update emergency report status
    
    Args:
        report_id: Report ID
        status_update: Status update
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated report
    
    Raises:
        HTTPException: If report not found
    """
    report = db.query(EmergencyReport).filter(
        EmergencyReport.id == report_id,
        EmergencyReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    update_data = status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    db.commit()
    db.refresh(report)
    
    # Convert location for response
    point = to_shape(report.location)
    
    return {
        **report.__dict__,
        "latitude": point.y,
        "longitude": point.x
    }


@router.post("/reports/{report_id}/media", status_code=status.HTTP_201_CREATED)
async def upload_report_media(
    report_id: str,
    file: UploadFile = File(...),
    media_type: str = "photo",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload media file for emergency report
    
    Args:
        report_id: Report ID
        file: Media file
        media_type: Type of media (photo, video, audio)
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If report not found
    """
    report = db.query(EmergencyReport).filter(
        EmergencyReport.id == report_id,
        EmergencyReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # TODO: Upload file to cloud storage (S3/Cloudinary)
    # TODO: Virus scan
    # For now, we'll just return a placeholder
    
    file_url = f"https://storage.nuur.et/emergency/{report_id}/{file.filename}"
    
    media = EmergencyReportMedia(
        report_id=report.id,
        media_type=media_type,
        file_url=file_url,
        file_size_bytes=0  # Placeholder
    )
    
    db.add(media)
    db.commit()
    
    return {
        "message": "Media uploaded successfully",
        "file_url": file_url
    }


@router.get("/nearby", response_model=List[EmergencyReportResponse])
async def get_nearby_reports(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get emergency reports near a location (public endpoint)
    
    Args:
        latitude: Latitude
        longitude: Longitude
        radius_km: Search radius in kilometers
        db: Database session
        limit: Maximum number of reports to return
    
    Returns:
        List of nearby reports
    """
    # Create point for search
    point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
    
    # Query nearby reports (within radius)
    # Note: This is a simplified query, in production use ST_DWithin
    reports = db.query(EmergencyReport).filter(
        EmergencyReport.status.in_(["pending", "acknowledged", "responding"])
    ).order_by(EmergencyReport.reported_at.desc()).limit(limit).all()
    
    # TODO: Filter by distance using PostGIS ST_DWithin
    
    # Convert locations for response
    response_data = []
    for report in reports:
        point = to_shape(report.location)
        response_data.append({
            **report.__dict__,
            "latitude": point.y,
            "longitude": point.x,
            "user_id": None  # Don't expose user ID for privacy
        })
    
    return response_data

