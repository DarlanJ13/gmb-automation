from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Google Review data
    google_review_id = Column(String, unique=True, index=True)
    reviewer_name = Column(String)
    reviewer_profile_photo = Column(String, nullable=True)
    
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    
    # Reply data
    reply_text = Column(Text, nullable=True)
    reply_at = Column(DateTime(timezone=True), nullable=True)
    ai_generated_reply = Column(Boolean, default=False)
    
    review_created_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    location = relationship("Location", back_populates="reviews")
