"""Custom exceptions and error handling for the Croatian Tutor API."""

from typing import Any


class CroatianTutorException(Exception):
    """Base exception for Croatian Tutor application."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class GeminiServiceError(CroatianTutorException):
    """Error from Gemini AI service."""

    def __init__(
        self,
        message: str = "AI service temporarily unavailable",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message=message, status_code=503, details=details)


class GeminiRateLimitError(GeminiServiceError):
    """Gemini API rate limit exceeded."""

    def __init__(self):
        super().__init__(
            message="AI service rate limit exceeded. Please try again later.",
            details={"retry_after": 60},
        )


class GeminiParseError(GeminiServiceError):
    """Failed to parse Gemini response."""

    def __init__(self, raw_response: str | None = None):
        super().__init__(
            message="Failed to process AI response",
            details={"raw_response": raw_response[:200] if raw_response else None},
        )


class WordNotFoundError(CroatianTutorException):
    """Requested word not found."""

    def __init__(self, word_id: int | None = None, word: str | None = None):
        details = {}
        if word_id:
            details["word_id"] = word_id
        if word:
            details["word"] = word
        super().__init__(
            message="Word not found",
            status_code=404,
            details=details,
        )


class TopicNotFoundError(CroatianTutorException):
    """Requested grammar topic not found."""

    def __init__(self, topic_id: int | None = None):
        super().__init__(
            message="Grammar topic not found",
            status_code=404,
            details={"topic_id": topic_id} if topic_id else {},
        )


class ValidationError(CroatianTutorException):
    """Validation error for request data."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(
            message=message,
            status_code=400,
            details={"field": field} if field else {},
        )


class DatabaseError(CroatianTutorException):
    """Database operation error."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, status_code=500)
