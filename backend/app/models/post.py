from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PostType(str, enum.Enum):
    UPDATE = "UPDATE"
    EVENT = "EVENT"
    OFFER = "OFFER"


class PostStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Post data
    google_post_id = Column(String, unique=True, index=True, nullable=True)
    post_type = Column(Enum(PostType), default=PostType.UPDATE)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI Generated
    ai_generated = Column(Integer, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    location = relationship("Location", back_populates="posts")
