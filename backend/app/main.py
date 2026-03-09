from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .utils.logger import logger

# Import routers
from .api import webhooks, websocket, calls

# Create FastAPI application
app = FastAPI(
    title="Twilio Voice Calling API",
    description="Backend API for Twilio voice calling application with real-time WebSocket support",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,  # Disable docs in production
    redoc_url="/redoc" if settings.is_development else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store settings in app state for access in routes
app.state.settings = settings


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info("Starting Twilio Voice Calling API...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"CORS origins: {settings.cors_origins_list}")

    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down Twilio Voice Calling API...")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Twilio Voice Calling API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(calls.router, prefix="/api/calls", tags=["calls"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(websocket.router, tags=["websocket"])

