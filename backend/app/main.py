from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json
import time
from app.core.config import settings
from app.infrastructure.database.connection import init_db
from app.api.v1.menu_router import router as menu_router
from app.api.v1.cart_router import router as cart_router
from app.api.v1.order_router import router as order_router
from app.api.v1.assistant_router import router as assistant_router
from app.api.websocket.handlers import router as websocket_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")


class APILoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            start_time = time.time()
            
            method = request.method
            path = request.url.path
            query = str(request.query_params) if request.query_params else ""
            
            body = None
            if method in ["POST", "PUT", "PATCH"]:
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        body = json.loads(body_bytes.decode())
                except:
                    body = None
                
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request = Request(request.scope, receive)
            
            logger.info(f"🚀 [{method}] {path} {query}")
            if body:
                logger.info(f"📤 Request Body: {json.dumps(body, indent=2)}")
            
            response = await call_next(request)
            
            duration = round((time.time() - start_time) * 1000, 2)
            status = response.status_code
            
            status_emoji = "✅" if status < 400 else "❌"
            logger.info(f"{status_emoji} [{method}] {path} - Status: {status} ({duration}ms)")
            
            return response
        
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered ordering assistant system for kiosks, voice, and call agents",
    lifespan=lifespan
)

app.add_middleware(APILoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(menu_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(assistant_router, prefix="/api/v1")
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

