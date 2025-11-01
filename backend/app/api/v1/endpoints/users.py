"""
User endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.emergency import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactResponse
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Args:
        current_user: Authenticated user
    
    Returns:
        User information
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    
    Args:
        user_update: Updated user data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated user
    """
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all emergency contacts for current user
    
    Args:
        current_user: Authenticated user
        db: Database session
    
    Returns:
        List of emergency contacts
    """
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == current_user.id,
        EmergencyContact.is_active == True
    ).order_by(EmergencyContact.priority).all()
    
    return contacts


@router.post("/contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new emergency contact
    
    Args:
        contact_data: Contact data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Created contact
    """
    contact = EmergencyContact(
        user_id=current_user.id,
        **contact_data.dict()
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact


@router.put("/contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: str,
    contact_update: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update emergency contact
    
    Args:
        contact_id: Contact ID
        contact_update: Updated contact data
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Updated contact
    
    Raises:
        HTTPException: If contact not found
    """
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    
    return contact


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete emergency contact
    
    Args:
        contact_id: Contact ID
        current_user: Authenticated user
        db: Database session
    
    Raises:
        HTTPException: If contact not found
    """
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    db.delete(contact)
    db.commit()
    
    return None

