from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.post import PostType, PostStatus


class PostBase(BaseModel):
    title: Optional[str] = None
    content: str
    post_type: PostType = PostType.UPDATE
    media_url: Optional[str] = None


class PostCreate(PostBase):
    location_id: int
    scheduled_at: Optional[datetime] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    post_type: Optional[PostType] = None
    media_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[PostStatus] = None


class PostInDB(PostBase):
    id: int
    location_id: int
    google_post_id: Optional[str]
    status: PostStatus
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    ai_generated: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Post(PostInDB):
    pass


class PostGenerate(BaseModel):
    location_id: int
    topic: Optional[str] = None
    post_type: PostType = PostType.UPDATE
