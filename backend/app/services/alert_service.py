"""
alert_service.py
─────────────────
Business logic for alerts.
"""
from __future__ import annotations

import logging
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.schemas.alert import AlertResponse

logger = logging.getLogger(__name__)


async def list_alerts(
    db: AsyncSession,
    severity: str | None = None,
    alert_type: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[AlertResponse]:
    stmt = (
        select(Alert)
        .options(selectinload(Alert.supplier), selectinload(Alert.invoice))
        .order_by(desc(Alert.created_at))
        .limit(limit)
    )
    if severity:
        stmt = stmt.where(Alert.severity == severity.lower())
    if alert_type:
        stmt = stmt.where(Alert.alert_type == alert_type)
    if status:
        stmt = stmt.where(Alert.status == status)

    result = await db.execute(stmt)
    alerts = result.scalars().all()

    return [
        AlertResponse(
            id=a.id,
            type=a.alert_type,
            supplier=a.supplier.name,
            invoice=a.invoice_id,
            severity=a.severity,
            timestamp=a.created_at.strftime("%Y-%m-%d %H:%M"),
            status=a.status,
        )
        for a in alerts
    ]


async def update_alert_status(
    db: AsyncSession, alert_id: str, status: str
) -> Alert | None:
    from uuid import UUID
    try:
        uid = UUID(alert_id)
    except ValueError:
        return None

    alert = await db.get(Alert, uid)
    if not alert:
        return None
    alert.status = status
    db.add(alert)
    return alert
