from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core import get_db
from app.models import Review, Location, User
from app.schemas import Review as ReviewSchema, ReviewUpdate, ReviewReplyGenerate
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ReviewSchema])
def get_reviews(
    location_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews for current user"""
    query = db.query(Review).join(Location).filter(Location.user_id == current_user.id)
    
    if location_id:
        query = query.filter(Review.location_id == location_id)
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews


@router.get("/{review_id}", response_model=ReviewSchema)
def get_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific review"""
    review = db.query(Review).join(Location).filter(
        Review.id == review_id,
        Location.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return review


@router.put("/{review_id}", response_model=ReviewSchema)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a review (mainly for adding manual replies)"""
    review = db.query(Review).join(Location).filter(
        Review.id == review_id,
        Location.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # Update fields
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    
    return review


@router.post("/{review_id}/reply")
def reply_to_review(
    review_id: int,
    reply_text: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually reply to a review"""
    review = db.query(Review).join(Location).filter(
        Review.id == review_id,
        Location.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    location = db.query(Location).filter(Location.id == review.location_id).first()
    
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account not connected"
        )
    
    from app.services import GoogleBusinessService
    from datetime import datetime
    
    gb_service = GoogleBusinessService(
        access_token=current_user.google_access_token,
        refresh_token=current_user.google_refresh_token
    )
    
    result = gb_service.reply_to_review(review.google_review_id, reply_text)
    
    if result:
        review.reply_text = reply_text
        review.reply_at = datetime.utcnow()
        review.ai_generated_reply = False
        db.commit()
        
        return {"message": "Reply posted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to post reply"
        )


@router.post("/{review_id}/generate-reply")
def generate_reply(
    review_id: int,
    reply_data: ReviewReplyGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate an AI reply for a review"""
    review = db.query(Review).join(Location).filter(
        Review.id == review_id,
        Location.user_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    location = db.query(Location).filter(Location.id == review.location_id).first()
    
    from app.services import AIResponseService
    
    ai_service = AIResponseService()
    reply_text = ai_service.generate_review_reply(
        business_name=location.name,
        reviewer_name=review.reviewer_name,
        rating=review.rating,
        review_comment=review.comment,
        tone=reply_data.tone
    )
    
    if not reply_text:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reply"
        )
    
    return {"reply_text": reply_text}


@router.post("/sync")
def sync_reviews(
    location_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync reviews from Google Business Profile"""
    if not current_user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account not connected"
        )
    
    from app.tasks import sync_location_reviews, sync_reviews as sync_all_reviews
    
    if location_id:
        # Verify location belongs to user
        location = db.query(Location).filter(
            Location.id == location_id,
            Location.user_id == current_user.id
        ).first()
        
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        
        task = sync_location_reviews.delay(location_id)
        return {"message": f"Syncing reviews for location {location_id}", "task_id": task.id}
    else:
        task = sync_all_reviews.delay()
        return {"message": "Syncing reviews for all locations", "task_id": task.id}
