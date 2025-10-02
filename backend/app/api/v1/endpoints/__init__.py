from .auth import router as auth_router
from .locations import router as locations_router
from .posts import router as posts_router
from .reviews import router as reviews_router

__all__ = [
    "auth_router",
    "locations_router",
    "posts_router",
    "reviews_router"
]
