"""
Main FastAPI Application
Nifty Stock Intelligence Platform
"""
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.core.logging import setup_logging, logger
from app.core.exceptions import AppException
from app.api.v1 import chat, stocks, analysis, health, documents
from app.dependencies import get_aws_clients

# Setup logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Nifty Stock Intelligence Platform API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    
    # Initialize AWS clients
    try:
        aws_clients = await get_aws_clients()
        logger.info("✅ AWS clients initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AWS clients: {e}")
        raise
    
    # Warm up Bedrock connection
    try:
        await aws_clients["bedrock_runtime"].list_foundation_models()
        logger.info("✅ Bedrock connection verified")
    except Exception as e:
        logger.warning(f"⚠️  Bedrock connection check failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Nifty Stock Intelligence Platform API")


# Create FastAPI app
app = FastAPI(
    title="Nifty Stock Intelligence Platform API",
    description="AI-Powered Real-Time Stock Analysis & Prediction Engine for Indian Equity Markets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# AWS X-Ray (optional) - Registered AFTER 'app' is created
#if settings.ENABLE_XRAY:
#    from aws_xray_sdk.core import xray_recorder, patch_all
#    from aws_xray_sdk.ext.fastapi.middleware import XRayMiddleware
#    
#    xray_recorder.configure(service='NiftyStockIntelligence')
#    patch_all()
#    app.add_middleware(XRayMiddleware)


# ============================================
# Middleware Configuration
# ============================================

# CORS Middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Gzip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.3f}s"
    )
    
    return response


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# ============================================
# API Routers
# ============================================

app.include_router(health.router, tags=["Health"], prefix="")
app.include_router(chat.router, tags=["Chat"], prefix="/api/v1/chat")
app.include_router(stocks.router, tags=["Stocks"], prefix="/api/v1/stocks")
app.include_router(analysis.router, tags=["Analysis"], prefix="/api/v1/analysis")
app.include_router(documents.router, tags=["Documents"], prefix="/api/v1/documents")

# ============================================
# Root Endpoint
# ============================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    return {
        "name": "Nifty Stock Intelligence Platform API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "dev",
        log_level=settings.LOG_LEVEL.lower()
    )