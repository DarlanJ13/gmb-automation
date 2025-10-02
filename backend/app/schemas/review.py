from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    rating: float
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    location_id: int
    google_review_id: str
    reviewer_name: str
    reviewer_profile_photo: Optional[str] = None
    review_created_at: datetime


class ReviewUpdate(BaseModel):
    reply_text: Optional[str] = None


class ReviewInDB(ReviewBase):
    id: int
    location_id: int
    google_review_id: str
    reviewer_name: str
    reviewer_profile_photo: Optional[str] = None
    reply_text: Optional[str] = None
    reply_at: Optional[datetime] = None
    ai_generated_reply: bool
    review_created_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class Review(ReviewInDB):
    pass


class ReviewReplyGenerate(BaseModel):
    review_id: int
    tone: Optional[str] = "professional"
