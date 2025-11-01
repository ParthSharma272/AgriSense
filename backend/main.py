"""
FastAPI main application for AgriSense 2.0
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Agricultural Q&A System for India with RAG and Live Data Integration",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global state
class AppState:
    """Application state"""
    rag_pipeline = None
    data_fusion = None
    chart_builder = None
    data_fetcher = None
    initialized = False


state = AppState()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AgriSense 2.0...")
    
    try:
        # Import here to avoid circular dependencies
        from models.llm_rag import RAGPipeline
        from models.datafusion import DataFusion
        from utils.chart_builder import ChartBuilder
        from utils.fetch_datasets import DataGovFetcher
        
        # Initialize RAG pipeline
        if settings.HF_API_TOKEN:
            logger.info("Initializing RAG pipeline...")
            state.rag_pipeline = RAGPipeline(
                hf_token=settings.HF_API_TOKEN,
                hf_model=settings.HF_MODEL,
                embedding_model=settings.EMBEDDING_MODEL,
                chroma_persist_dir=settings.CHROMA_PERSIST_DIR,
                top_k=settings.TOP_K_RESULTS,
                similarity_threshold=settings.SIMILARITY_THRESHOLD
            )
            logger.info("RAG pipeline initialized")
        else:
            logger.warning("HF_API_TOKEN not set, RAG pipeline not initialized")
        
        # Initialize Data Fusion
        logger.info("Initializing Data Fusion...")
        state.data_fusion = DataFusion(settings.DATABASE_URL)
        
        # Initialize Chart Builder
        logger.info("Initializing Chart Builder...")
        state.chart_builder = ChartBuilder(
            width=settings.DEFAULT_CHART_WIDTH,
            height=settings.DEFAULT_CHART_HEIGHT
        )
        
        # Initialize Data Fetcher
        if settings.DATA_GOV_API_KEY:
            logger.info("Initializing Data Fetcher...")
            state.data_fetcher = DataGovFetcher(
                api_key=settings.DATA_GOV_API_KEY,
                base_url=settings.DATA_GOV_BASE_URL
            )
        else:
            logger.warning("DATA_GOV_API_KEY not set, data fetching limited")
        
        state.initialized = True
        logger.info("AgriSense 2.0 started successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        state.initialized = False


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AgriSense 2.0...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running" if state.initialized else "initializing",
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/chat",
            "visualize": "/api/visualize",
            "datasets": "/api/datasets",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if state.initialized else "starting",
        "services": {
            "rag_pipeline": state.rag_pipeline is not None,
            "data_fusion": state.data_fusion is not None,
            "chart_builder": state.chart_builder is not None,
            "data_fetcher": state.data_fetcher is not None
        }
    }


# Import and include routers
try:
    from routes import chat, visualize
    
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(visualize.router, prefix="/api", tags=["visualization"])
except Exception as e:
    logger.error(f"Error importing routes: {e}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
