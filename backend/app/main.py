"""
Agentic Assist API - Main Application Entry Point

AI-powered ordering assistant system for kiosks and voice ordering.
"""

import json
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.infrastructure.database.connection import init_db
from app.infrastructure.llm import LLMFactory
from app.api.v1.auth_router import router as auth_router
from app.api.v1.business_router import router as business_router
from app.api.v1.menu_router import router as menu_router
from app.api.v1.cart_router import router as cart_router
from app.api.v1.bill_router import router as bill_router
from app.api.v1.assistant_router import router as assistant_router
from app.api.websocket.handlers import router as websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        # Log request body for write operations
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes.decode())
            except Exception:
                body = None
            
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request = Request(request.scope, receive)
        
        logger.info(f"🚀 [{method}] {path}")
        if body and settings.DEBUG:
            logger.debug(f"📤 Request: {json.dumps(body, indent=2)}")
        
        response = await call_next(request)
        
        duration = round((time.time() - start_time) * 1000, 2)
        status = response.status_code
        emoji = "✅" if status < 400 else "❌"
        logger.info(f"{emoji} [{method}] {path} - {status} ({duration}ms)")
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    
    # === STARTUP ===
    logger.info("=" * 50)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 50)
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize LLM
    if LLMFactory.initialize():
        logger.info("✅ LLM provider ready")
    else:
        logger.warning("⚠️ LLM not configured - AI features disabled")
    
    logger.info("🎉 Application started!")
    logger.info("=" * 50)
    
    yield
    
    # === SHUTDOWN ===
    logger.info("👋 Shutting down...")
    await LLMFactory.shutdown()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered ordering assistant for kiosks and voice ordering",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(APILoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(business_router, prefix="/api/v1", tags=["Businesses"])
app.include_router(menu_router, prefix="/api/v1", tags=["Menu"])
app.include_router(cart_router, prefix="/api/v1", tags=["Cart"])
app.include_router(bill_router, prefix="/api/v1", tags=["Bills"])
app.include_router(assistant_router, prefix="/api/v1", tags=["Assistant"])
app.include_router(websocket_router, tags=["WebSocket"])


@app.get("/", tags=["Health"])
async def root():
    """API root - basic info."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_available": LLMFactory.is_available()
    }
