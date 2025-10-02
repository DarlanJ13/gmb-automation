from .celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Post, Location, User
from app.models.post import PostStatus
from app.services import GoogleBusinessService, AIResponseService
from datetime import datetime


@celery_app.task
def publish_scheduled_posts():
    """Check for scheduled posts and publish them"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        scheduled_posts = db.query(Post).filter(
            Post.status == PostStatus.SCHEDULED,
            Post.scheduled_at <= now
        ).all()
        
        for post in scheduled_posts:
            publish_post.delay(post.id)
        
        return f"Queued {len(scheduled_posts)} posts for publishing"
    finally:
        db.close()


@celery_app.task
def publish_post(post_id: int):
    """Publish a single post to Google Business Profile"""
    db = SessionLocal()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return f"Post {post_id} not found"
        
        location = db.query(Location).filter(Location.id == post.location_id).first()
        if not location:
            return f"Location not found for post {post_id}"
        
        user = db.query(User).filter(User.id == location.user_id).first()
        if not user or not user.google_access_token:
            post.status = PostStatus.FAILED
            db.commit()
            return f"User credentials not found for post {post_id}"
        
        # Initialize Google Business service
        gb_service = GoogleBusinessService(
            access_token=user.google_access_token,
            refresh_token=user.google_refresh_token
        )
        
        # Prepare post data
        post_data = {
            "summary": post.content,
            "topicType": post.post_type.value
        }
        
        if post.media_url:
            post_data["media"] = [{"mediaFormat": "PHOTO", "sourceUrl": post.media_url}]
        
        # Publish to Google
        result = gb_service.create_post(location.google_location_id, post_data)
        
        if result:
            post.status = PostStatus.PUBLISHED
            post.published_at = datetime.utcnow()
            post.google_post_id = result.get('name', '')
            db.commit()
            return f"Post {post_id} published successfully"
        else:
            post.status = PostStatus.FAILED
            db.commit()
            return f"Failed to publish post {post_id}"
            
    except Exception as e:
        if post:
            post.status = PostStatus.FAILED
            db.commit()
        return f"Error publishing post {post_id}: {str(e)}"
    finally:
        db.close()


@celery_app.task
def generate_ai_post(location_id: int, topic: str = None, post_type: str = "UPDATE"):
    """Generate a post using AI"""
    db = SessionLocal()
    try:
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            return f"Location {location_id} not found"
        
        ai_service = AIResponseService()
        content = ai_service.generate_post_content(
            business_name=location.name,
            business_category=location.category or "business",
            topic=topic,
            post_type=post_type
        )
        
        if content:
            new_post = Post(
                location_id=location_id,
                content=content,
                post_type=post_type,
                status=PostStatus.DRAFT,
                ai_generated=True
            )
            db.add(new_post)
            db.commit()
            return f"AI post generated for location {location_id}"
        else:
            return f"Failed to generate AI post for location {location_id}"
            
    except Exception as e:
        return f"Error generating AI post: {str(e)}"
    finally:
        db.close()
