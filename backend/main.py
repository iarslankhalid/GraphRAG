"""
GraphRAG Explorer - Main FastAPI Application
A full-stack demo showcasing the difference between Plain RAG and GraphRAG.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from config import settings
from database.neo4j_manager import Neo4jManager
from database.sqlite_manager import SQLiteManager
from services.llm_service import LLMService
from routers import documents, graph, rag
from models.schemas import HealthCheckResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances (will be initialized in lifespan)
neo4j_manager = None
sqlite_manager = None
llm_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the application.
    Initializes and cleans up resources.
    """
    global neo4j_manager, sqlite_manager, llm_service
    
    logger.info("Starting GraphRAG Explorer...")
    
    # Ensure data directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.dirname(settings.sqlite_db_path), exist_ok=True)
    
    # Initialize database connections
    try:
        neo4j_manager = Neo4jManager(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password
        )
        logger.info("Neo4j connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        neo4j_manager = None
    
    try:
        sqlite_manager = SQLiteManager(db_path=settings.sqlite_db_path)
        logger.info("SQLite database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize SQLite: {e}")
        sqlite_manager = None
    
    # Initialize LLM service
    try:
        llm_service = LLMService(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            embedding_model=settings.embedding_model
        )
        logger.info("LLM service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        llm_service = None
    
    yield
    
    # Cleanup
    logger.info("Shutting down GraphRAG Explorer...")
    if neo4j_manager:
        neo4j_manager.close()
    if sqlite_manager:
        sqlite_manager.close()


# Create FastAPI application
app = FastAPI(
    title="GraphRAG Explorer",
    description="Compare Plain RAG vs GraphRAG for question answering",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection for database managers and services
def get_neo4j_manager() -> Neo4jManager:
    """Dependency for Neo4j manager."""
    if neo4j_manager is None:
        raise RuntimeError("Neo4j is not available")
    return neo4j_manager


def get_sqlite_manager() -> SQLiteManager:
    """Dependency for SQLite manager."""
    if sqlite_manager is None:
        raise RuntimeError("SQLite is not available")
    return sqlite_manager


def get_llm_service() -> LLMService:
    """Dependency for LLM service."""
    if llm_service is None:
        raise RuntimeError("LLM service is not available")
    return llm_service


# Override dependencies in routers
app.dependency_overrides[Neo4jManager] = get_neo4j_manager
app.dependency_overrides[SQLiteManager] = get_sqlite_manager
app.dependency_overrides[LLMService] = get_llm_service


# Health check endpoint
@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Check the health of the application and its dependencies.
    
    Returns:
        Health status of all components
    """
    neo4j_ok = neo4j_manager is not None
    sqlite_ok = sqlite_manager is not None
    llm_ok = llm_service is not None
    
    status = "healthy" if (neo4j_ok and sqlite_ok and llm_ok) else "degraded"
    
    issues = []
    if not neo4j_ok:
        issues.append("Neo4j connection failed")
    if not sqlite_ok:
        issues.append("SQLite initialization failed")
    if not llm_ok:
        issues.append("LLM service initialization failed")
    
    message = "All systems operational" if not issues else "; ".join(issues)
    
    return HealthCheckResponse(
        status=status,
        neo4j_connected=neo4j_ok,
        sqlite_connected=sqlite_ok,
        message=message
    )


# Include routers
app.include_router(documents.router)
app.include_router(graph.router)
app.include_router(rag.router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "GraphRAG Explorer API",
        "version": "1.0.0",
        "description": "Compare Plain RAG vs GraphRAG approaches",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
