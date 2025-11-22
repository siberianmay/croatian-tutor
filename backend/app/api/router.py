"""Main API router aggregating all route modules."""

from fastapi import APIRouter

from app.api.words import router as words_router
from app.api.drills import router as drills_router
from app.api.topics import router as topics_router
from app.api.exercises import router as exercises_router

api_router = APIRouter()

api_router.include_router(words_router)
api_router.include_router(drills_router)
api_router.include_router(topics_router)
api_router.include_router(exercises_router)
