"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .api import events, health

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="PlanIt AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None  # Disable ReDoc for faster startup
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])

@app.get("/")
async def root():
    return {"message": "PlanIt AI", "version": "1.0.0", "status": "running"}
