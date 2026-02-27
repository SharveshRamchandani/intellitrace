"""
routes/alerts.py
─────────────────
GET  /api/alerts           — list alerts (filterable)
PATCH /api/alerts/{id}     — update alert status
"""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.alert import AlertResponse, AlertStatusUpdate
from app.services import list_alerts, update_alert_status

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

VALID_ALERT_TYPES = {
    "Revenue Mismatch", "Velocity Anomaly", "Cascade Risk",
    "Carousel Risk", "Duplicate", "PO Mismatch",
}
VALID_STATUSES = {"Open", "Reviewed", "Resolved"}
VALID_SEVERITIES = {"high", "medium", "low"}


@router.get("", response_model=list[AlertResponse])
async def get_alerts(
    severity: str | None = Query(default=None),
    alert_type: str | None = Query(default=None, alias="type"),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Return alerts with optional filters:
      - severity: high | medium | low
      - type: Revenue Mismatch | Cascade Risk | Velocity Anomaly | etc.
      - status: Open | Reviewed | Resolved

    Response matches frontend alertsData shape exactly.
    """
    if severity and severity.lower() not in VALID_SEVERITIES:
        raise HTTPException(status_code=422, detail=f"Invalid severity: {severity}")
    if alert_type and alert_type not in VALID_ALERT_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid alert type: {alert_type}")
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {status}")

    return await list_alerts(db, severity=severity, alert_type=alert_type, status=status, limit=limit)


@router.patch("/{alert_id}", response_model=dict)
async def patch_alert_status(
    alert_id: str,
    payload: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an alert's status (Open → Reviewed → Resolved)."""
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {payload.status}")

    alert = await update_alert_status(db, alert_id, payload.status)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    logger.info("alert_status_updated", alert_id=alert_id, status=payload.status)
    return {"id": alert_id, "status": payload.status}
