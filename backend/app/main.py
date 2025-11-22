from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Croatian Language Tutor API",
    description="AI-powered Croatian language learning backend",
    version="0.1.0",
)

# CORS configuration for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "croatian-tutor-backend",
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Croatian Language Tutor API",
        "docs": "/docs",
        "health": "/health",
    }


# API router will be added here
# from app.api.router import api_router
# app.include_router(api_router, prefix=settings.api_v1_prefix)
