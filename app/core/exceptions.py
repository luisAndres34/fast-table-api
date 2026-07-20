from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.core.logger import logger

def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Globally catches database Integrity Errors (like unique constraint violations)
    and returns a clean 409 Conflict response instead of a 500 Internal Server Error.
    """
    logger.error(f"Integrity error occurred on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, 
        content={
            "error": "Integrity Error", 
            "detail": "A record with this unique data already exists."
        }
    )
