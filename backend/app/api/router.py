"""Main API router aggregating all route modules."""

from fastapi import APIRouter

from app.api.words import router as words_router
from app.api.drills import router as drills_router
from app.api.topics import router as topics_router
from app.api.exercises import router as exercises_router
from app.api.progress import router as progress_router
from app.api.sessions import router as sessions_router

api_router = APIRouter()

api_router.include_router(words_router)
api_router.include_router(drills_router)
api_router.include_router(topics_router)
api_router.include_router(exercises_router)
api_router.include_router(progress_router)
api_router.include_router(sessions_router)
