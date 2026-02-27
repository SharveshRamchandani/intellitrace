"""
routes/dashboard.py
────────────────────
GET /api/dashboard — aggregated KPIs, charts, and sparkline data.
"""
import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services import get_dashboard

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def dashboard(db: AsyncSession = Depends(get_db)):
    """
    Returns all data needed for the frontend dashboard:
      - KPI cards (total invoices, high-risk, suspicious suppliers, exposure)
      - Sparkline arrays (12 months)
      - Fraud risk distribution (bar chart)
      - Invoice volume vs revenue (area chart)
    """
    return await get_dashboard(db)
