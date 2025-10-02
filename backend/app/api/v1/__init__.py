from fastapi import APIRouter
from .endpoints import auth_router, locations_router, posts_router, reviews_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(locations_router, prefix="/locations", tags=["locations"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
