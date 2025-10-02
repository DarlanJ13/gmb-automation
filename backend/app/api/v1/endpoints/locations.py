from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core import get_db
from app.models import Location, User
from app.schemas import Location as LocationSchema, LocationCreate, LocationUpdate
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[LocationSchema])
def get_locations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all locations for current user"""
    locations = db.query(Location).filter(
        Location.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return locations


@router.get("/{location_id}", response_model=LocationSchema)
def get_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific location"""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == current_user.id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    return location


@router.post("/", response_model=LocationSchema, status_code=status.HTTP_201_CREATED)
def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new location"""
    # Check if location already exists
    existing = db.query(Location).filter(
        Location.google_location_id == location_data.google_location_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location already exists"
        )
    
    new_location = Location(
        user_id=current_user.id,
        **location_data.model_dump()
    )
    
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    
    return new_location


@router.put("/{location_id}", response_model=LocationSchema)
def update_location(
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a location"""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == current_user.id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    # Update fields
    update_data = location_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    
    db.commit()
    db.refresh(location)
    
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a location"""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == current_user.id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    db.delete(location)
    db.commit()
    
    return None


@router.post("/sync")
def sync_google_locations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync locations from Google Business Profile"""
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account not connected"
        )
    
    from app.services import GoogleBusinessService
    
    gb_service = GoogleBusinessService(
        access_token=current_user.google_access_token,
        refresh_token=current_user.google_refresh_token
    )
    
    # Get accounts
    accounts = gb_service.get_accounts()
    synced_count = 0
    
    for account in accounts:
        account_id = account.get('name', '').split('/')[-1]
        locations = gb_service.get_locations(account_id)
        
        for g_location in locations:
            google_location_id = g_location.get('name', '')
            
            # Check if location already exists
            existing = db.query(Location).filter(
                Location.google_location_id == google_location_id
            ).first()
            
            if not existing:
                new_location = Location(
                    user_id=current_user.id,
                    google_location_id=google_location_id,
                    name=g_location.get('title', ''),
                    address=g_location.get('storefrontAddress', {}).get('addressLines', [''])[0],
                    phone=g_location.get('phoneNumbers', {}).get('primaryPhone', ''),
                    website=g_location.get('websiteUri', ''),
                    category=g_location.get('categories', {}).get('primaryCategory', {}).get('displayName', '')
                )
                db.add(new_location)
                synced_count += 1
    
    db.commit()
    
    return {"message": f"Synced {synced_count} new locations"}
