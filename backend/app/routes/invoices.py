"""
routes/invoices.py
───────────────────
POST /api/invoices        — create invoice + trigger fraud scoring
GET  /api/invoices        — list flagged invoices
GET  /api/invoices/{id}   — full invoice detail with risk breakdown
"""
from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceDetailResponse, InvoiceListItem, TaskAccepted
from app.services import create_invoice, get_invoice_detail, list_flagged_invoices
from app.tasks import compute_fraud_score

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


@router.post("", response_model=TaskAccepted, status_code=status.HTTP_202_ACCEPTED)
async def create_invoice_endpoint(
    payload: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create an invoice and immediately queue a Celery fraud-scoring task.
    Returns 202 Accepted with a task_id for status polling.
    """
    try:
        invoice = await create_invoice(db, payload)
    except Exception as exc:
        logger.error("invoice_create_failed", error=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))

    # Dispatch Celery task (non-blocking)
    task = compute_fraud_score.delay(invoice.id)
    logger.info("fraud_task_queued", invoice_id=invoice.id, task_id=task.id)

    return TaskAccepted(invoice_id=invoice.id, task_id=task.id)


@router.get("", response_model=list[InvoiceListItem])
async def list_invoices(
    min_risk_score: float | None = Query(default=None, ge=0, le=100),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Return flagged invoices sorted by risk score descending."""
    return await list_flagged_invoices(db, limit=limit, min_risk_score=min_risk_score)


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Full invoice detail view including risk breakdown per category."""
    detail = await get_invoice_detail(db, invoice_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found")
    return detail
