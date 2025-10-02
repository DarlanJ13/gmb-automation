from .celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Review, Location, User
from app.services import GoogleBusinessService, AIResponseService
from datetime import datetime


@celery_app.task
def sync_reviews():
    """Sync reviews from Google Business Profile for all locations"""
    db = SessionLocal()
    try:
        locations = db.query(Location).filter(Location.auto_reply_enabled == True).all()
        
        for location in locations:
            sync_location_reviews.delay(location.id)
        
        return f"Queued {len(locations)} locations for review sync"
    finally:
        db.close()


@celery_app.task
def sync_location_reviews(location_id: int):
    """Sync reviews for a specific location"""
    db = SessionLocal()
    try:
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            return f"Location {location_id} not found"
        
        user = db.query(User).filter(User.id == location.user_id).first()
        if not user or not user.google_access_token:
            return f"User credentials not found for location {location_id}"
        
        # Initialize Google Business service
        gb_service = GoogleBusinessService(
            access_token=user.google_access_token,
            refresh_token=user.google_refresh_token
        )
        
        # Get reviews from Google
        google_reviews = gb_service.get_reviews(location.google_location_id)
        
        new_reviews_count = 0
        for g_review in google_reviews:
            # Check if review already exists
            existing_review = db.query(Review).filter(
                Review.google_review_id == g_review.get('reviewId')
            ).first()
            
            if not existing_review:
                # Create new review
                new_review = Review(
                    location_id=location_id,
                    google_review_id=g_review.get('reviewId'),
                    reviewer_name=g_review.get('reviewer', {}).get('displayName', 'Anonymous'),
                    reviewer_profile_photo=g_review.get('reviewer', {}).get('profilePhotoUrl'),
                    rating=g_review.get('starRating', 0),
                    comment=g_review.get('comment'),
                    review_created_at=datetime.fromisoformat(g_review.get('createTime', datetime.utcnow().isoformat()))
                )
                db.add(new_review)
                new_reviews_count += 1
                
                # Auto-reply if enabled
                if location.auto_reply_enabled and not g_review.get('reviewReply'):
                    generate_and_reply_to_review.delay(new_review.id)
        
        db.commit()
        return f"Synced {new_reviews_count} new reviews for location {location_id}"
        
    except Exception as e:
        return f"Error syncing reviews for location {location_id}: {str(e)}"
    finally:
        db.close()


@celery_app.task
def generate_and_reply_to_review(review_id: int, tone: str = "professional"):
    """Generate AI reply and post it to Google Business Profile"""
    db = SessionLocal()
    try:
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return f"Review {review_id} not found"
        
        location = db.query(Location).filter(Location.id == review.location_id).first()
        if not location:
            return f"Location not found for review {review_id}"
        
        user = db.query(User).filter(User.id == location.user_id).first()
        if not user or not user.google_access_token:
            return f"User credentials not found for review {review_id}"
        
        # Generate AI reply
        ai_service = AIResponseService()
        reply_text = ai_service.generate_review_reply(
            business_name=location.name,
            reviewer_name=review.reviewer_name,
            rating=review.rating,
            review_comment=review.comment,
            tone=tone
        )
        
        if not reply_text:
            return f"Failed to generate reply for review {review_id}"
        
        # Post reply to Google
        gb_service = GoogleBusinessService(
            access_token=user.google_access_token,
            refresh_token=user.google_refresh_token
        )
        
        result = gb_service.reply_to_review(review.google_review_id, reply_text)
        
        if result:
            review.reply_text = reply_text
            review.reply_at = datetime.utcnow()
            review.ai_generated_reply = True
            db.commit()
            return f"Reply posted for review {review_id}"
        else:
            return f"Failed to post reply for review {review_id}"
            
    except Exception as e:
        return f"Error replying to review {review_id}: {str(e)}"
    finally:
        db.close()
