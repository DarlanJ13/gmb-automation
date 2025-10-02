from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core import get_db
from app.models import Post, Location, User
from app.schemas import Post as PostSchema, PostCreate, PostUpdate, PostGenerate
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[PostSchema])
def get_posts(
    location_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all posts for current user"""
    query = db.query(Post).join(Location).filter(Location.user_id == current_user.id)
    
    if location_id:
        query = query.filter(Post.location_id == location_id)
    
    posts = query.offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostSchema)
def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific post"""
    post = db.query(Post).join(Location).filter(
        Post.id == post_id,
        Location.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.post("/", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    # Verify location belongs to user
    location = db.query(Location).filter(
        Location.id == post_data.location_id,
        Location.user_id == current_user.id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    new_post = Post(**post_data.model_dump())
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post


@router.put("/{post_id}", response_model=PostSchema)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a post"""
    post = db.query(Post).join(Location).filter(
        Post.id == post_id,
        Location.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Update fields
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    post = db.query(Post).join(Location).filter(
        Post.id == post_id,
        Location.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    
    return None


@router.post("/{post_id}/publish")
def publish_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a post immediately"""
    post = db.query(Post).join(Location).filter(
        Post.id == post_id,
        Location.user_id == current_user.id
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    from app.tasks import publish_post as publish_post_task
    task = publish_post_task.delay(post_id)
    
    return {"message": "Post queued for publishing", "task_id": task.id}


@router.post("/generate", response_model=PostSchema, status_code=status.HTTP_201_CREATED)
def generate_ai_post(
    post_data: PostGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a post using AI"""
    # Verify location belongs to user
    location = db.query(Location).filter(
        Location.id == post_data.location_id,
        Location.user_id == current_user.id
    ).first()
    
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    
    from app.services import AIResponseService
    
    ai_service = AIResponseService()
    content = ai_service.generate_post_content(
        business_name=location.name,
        business_category=location.category or "business",
        topic=post_data.topic,
        post_type=post_data.post_type.value
    )
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate post content"
        )
    
    new_post = Post(
        location_id=post_data.location_id,
        content=content,
        post_type=post_data.post_type,
        ai_generated=True
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post
