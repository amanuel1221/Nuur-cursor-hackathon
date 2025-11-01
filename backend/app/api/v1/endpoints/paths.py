"""
Path tracking endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_Length, ST_MakeLine
import secrets

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.path import Path, PathPoint, SharedPath
from app.schemas.path import (
    PathCreate,
    PathUpdate,
    PathResponse,
    PathDetailResponse,
    PathPointCreate,
    PathPointResponse,
    PathShareCreate,
    PathShareResponse
)

router = APIRouter()


@router.post("/start", response_model=PathResponse, status_code=status.HTTP_201_CREATED)
async def start_path_tracking(
    path_data: PathCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new path tracking session
    
    Args:
        path_data: Path data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created path
    """
    # Deactivate any active paths
    db.query(Path).filter(
        Path.user_id == current_user.id,
        Path.is_active == True
    ).update({"is_active": False})
    
    # Create new path
    path = Path(
        user_id=current_user.id,
        name=path_data.name,
        description=path_data.description,
        path_type=path_data.path_type,
        start_time=datetime.utcnow(),
        is_active=True
    )
    
    db.add(path)
    db.commit()
    db.refresh(path)
    
    return path


@router.post("/{path_id}/stop", response_model=PathResponse)
async def stop_path_tracking(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stop path tracking session
    
    Args:
        path_id: Path ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated path
    
    Raises:
        HTTPException: If path not found or not active
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    if not path.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is not active"
        )
    
    path.is_active = False
    path.end_time = datetime.utcnow()
    
    # Calculate total distance
    # Note: This is a simplified calculation, in production use ST_Length
    points_count = db.query(PathPoint).filter(PathPoint.path_id == path.id).count()
    
    if points_count > 1:
        # For simplicity, we'll calculate average speed if available
        first_point = db.query(PathPoint).filter(PathPoint.path_id == path.id).order_by(PathPoint.timestamp).first()
        last_point = db.query(PathPoint).filter(PathPoint.path_id == path.id).order_by(PathPoint.timestamp.desc()).first()
        
        if first_point and last_point:
            time_diff = (last_point.timestamp - first_point.timestamp).total_seconds()
            # This is a placeholder - actual distance calculation would use PostGIS functions
            path.total_distance_meters = 0.0  # Placeholder
            if time_diff > 0:
                path.average_speed_mps = path.total_distance_meters / time_diff if path.total_distance_meters else 0
    
    db.commit()
    db.refresh(path)
    
    return path


@router.post("/{path_id}/points", status_code=status.HTTP_201_CREATED)
async def add_path_points(
    path_id: str,
    points: List[PathPointCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add location points to path (batch upload)
    
    Args:
        path_id: Path ID
        points: List of location points
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If path not found
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    # Add points
    for point_data in points:
        point_geom = WKTElement(f'POINT({point_data.longitude} {point_data.latitude})', srid=4326)
        
        point = PathPoint(
            path_id=path.id,
            location=point_geom,
            accuracy=point_data.accuracy,
            altitude=point_data.altitude,
            speed=point_data.speed,
            heading=point_data.heading,
            timestamp=point_data.timestamp
        )
        db.add(point)
    
    db.commit()
    
    return {"message": f"Added {len(points)} points successfully"}


@router.get("", response_model=List[PathResponse])
async def get_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    skip: int = 0
):
    """
    Get user's paths
    
    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of paths to return
        skip: Number of paths to skip
    
    Returns:
        List of paths
    """
    paths = db.query(Path).filter(
        Path.user_id == current_user.id
    ).order_by(Path.start_time.desc()).offset(skip).limit(limit).all()
    
    return paths


@router.get("/{path_id}", response_model=PathDetailResponse)
async def get_path_detail(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get path details with all points
    
    Args:
        path_id: Path ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Path with points
    
    Raises:
        HTTPException: If path not found
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    # Get points
    points_data = db.query(PathPoint).filter(
        PathPoint.path_id == path.id
    ).order_by(PathPoint.timestamp).all()
    
    # Convert to response format
    points = []
    for p in points_data:
        point = to_shape(p.location)
        points.append({
            "id": p.id,
            "latitude": point.y,
            "longitude": point.x,
            "accuracy": p.accuracy,
            "altitude": p.altitude,
            "speed": p.speed,
            "heading": p.heading,
            "timestamp": p.timestamp
        })
    
    return {
        **path.__dict__,
        "points": points
    }


@router.put("/{path_id}", response_model=PathResponse)
async def update_path(
    path_id: str,
    path_update: PathUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update path details
    
    Args:
        path_id: Path ID
        path_update: Updated path data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated path
    
    Raises:
        HTTPException: If path not found
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    update_data = path_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(path, field, value)
    
    db.commit()
    db.refresh(path)
    
    return path


@router.delete("/{path_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_path(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete path
    
    Args:
        path_id: Path ID
        current_user: Authenticated user
        db: Database session
    
    Raises:
        HTTPException: If path not found
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    db.delete(path)
    db.commit()
    
    return None


@router.post("/{path_id}/share", response_model=PathShareResponse, status_code=status.HTTP_201_CREATED)
async def share_path(
    path_id: str,
    share_data: PathShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share path with someone
    
    Args:
        path_id: Path ID
        share_data: Share data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Share information with token
    
    Raises:
        HTTPException: If path not found
    """
    path = db.query(Path).filter(
        Path.id == path_id,
        Path.user_id == current_user.id
    ).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    # Generate share token
    share_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=share_data.expires_in_hours)
    
    shared_path = SharedPath(
        path_id=path.id,
        shared_with_email=share_data.shared_with_email,
        shared_with_phone=share_data.shared_with_phone,
        share_token=share_token,
        expires_at=expires_at
    )
    
    db.add(shared_path)
    db.commit()
    db.refresh(shared_path)
    
    # TODO: Send share notification via email/SMS
    
    return shared_path


@router.get("/shared/{share_token}", response_model=PathDetailResponse)
async def get_shared_path(
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    Get path using share token (no authentication required)
    
    Args:
        share_token: Share token
        db: Database session
    
    Returns:
        Shared path with points
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    shared = db.query(SharedPath).filter(
        SharedPath.share_token == share_token
    ).first()
    
    if not shared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared path not found"
        )
    
    if shared.expires_at and shared.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Share link has expired"
        )
    
    path = db.query(Path).filter(Path.id == shared.path_id).first()
    
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Path not found"
        )
    
    # Get points
    points_data = db.query(PathPoint).filter(
        PathPoint.path_id == path.id
    ).order_by(PathPoint.timestamp).all()
    
    points = []
    for p in points_data:
        point = to_shape(p.location)
        points.append({
            "id": p.id,
            "latitude": point.y,
            "longitude": point.x,
            "accuracy": p.accuracy,
            "altitude": p.altitude,
            "speed": p.speed,
            "heading": p.heading,
            "timestamp": p.timestamp
        })
    
    return {
        **path.__dict__,
        "points": points
    }

