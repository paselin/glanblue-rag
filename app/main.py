"""
Main FastAPI application.
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.endpoints import chat, search
from app.models.schemas import HealthResponse

# Setup
settings = get_settings()
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Granblue RAG System...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    
    # Initialize vector store
    from app.rag.vector_store import get_vector_store
    vector_store = get_vector_store()
    stats = vector_store.get_collection_stats()
    logger.info(f"Vector store initialized: {stats}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Granblue RAG System...")


# Create app
app = FastAPI(
    title="Granblue Fantasy RAG API",
    description="AI-powered Granblue Fantasy strategy guide system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Granblue Fantasy RAG API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now(),
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
