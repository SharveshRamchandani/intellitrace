"""
main.py – FastAPI application entry point.
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.fraud_engine.model import load_model
from app.routes import (
    invoices_router, dashboard_router, suppliers_router,
    network_router, alerts_router,
)
from app.utils.logging import setup_logging
from app.utils.exceptions import register_exception_handlers

settings = get_settings()
setup_logging(debug=settings.DEBUG)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    logger.info("startup", app=settings.APP_NAME, version=settings.APP_VERSION)
    # Initialise DB tables (runs CREATE TABLE IF NOT EXISTS)
    await init_db()
    # Pre-warm the PyTorch model so first inference is fast
    load_model()
    logger.info("model_loaded")
    yield
    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Multi-Tier Supply Chain Fraud Detection & Management Platform. "
        "Combines ML inference (PyTorch MLP) with rule-based anomaly detection "
        "to score every invoice for fraud risk in real time."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(dashboard_router)
app.include_router(invoices_router)
app.include_router(suppliers_router)
app.include_router(network_router)
app.include_router(alerts_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
