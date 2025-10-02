from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None


class LocationCreate(LocationBase):
    google_location_id: str


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    auto_reply_enabled: Optional[bool] = None
    auto_post_enabled: Optional[bool] = None


class LocationInDB(LocationBase):
    id: int
    user_id: int
    google_location_id: str
    auto_reply_enabled: bool
    auto_post_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Location(LocationInDB):
    pass
