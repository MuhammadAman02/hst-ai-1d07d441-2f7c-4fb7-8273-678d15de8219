from fastapi import FastAPI
from app.routes import color_analysis
from app.config import get_settings

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Skin Tone Color Suggestion API",
        description="AI-powered color recommendations based on skin tone analysis",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Include routers
    app.include_router(color_analysis.router, prefix="/api/v1", tags=["color-analysis"])
    
    return app