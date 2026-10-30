"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
@router.get("/health")
async def health_check():
    """Health check for Cloud Run and monitoring."""
    return {
        "status": "healthy",
        "service": "planit-ai",
        "version": "1.0.0"
    }
