from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Google Business Profile data
    google_location_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    website = Column(String)
    category = Column(String)
    
    # Settings
    auto_reply_enabled = Column(Boolean, default=False)
    auto_post_enabled = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="locations")
    posts = relationship("Post", back_populates="location")
    reviews = relationship("Review", back_populates="location")
