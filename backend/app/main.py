import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import CroatianTutorException, GeminiServiceError

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Croatian Language Tutor API",
    description="AI-powered Croatian language learning backend",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(CroatianTutorException)
async def croatian_tutor_exception_handler(
    request: Request,
    exc: CroatianTutorException,
) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(f"{exc.__class__.__name__}: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(GeminiServiceError)
async def gemini_service_error_handler(
    request: Request,
    exc: GeminiServiceError,
) -> JSONResponse:
    """Handle Gemini AI service errors with user-friendly messages."""
    logger.error(f"Gemini service error: {exc.message}", extra=exc.details)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "AIServiceError",
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all handler for unexpected exceptions."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"type": exc.__class__.__name__} if settings.DEBUG else {},
        },
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


# API routes
from app.api.router import api_router

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
