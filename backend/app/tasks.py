"""
tasks.py – Celery background task definitions.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import date, timedelta

import structlog
from celery import Celery
from sqlalchemy import select, func

from app.config import get_settings
from app.fraud_engine.graph_builder import SupplyChainGraph
from app.fraud_engine.feature_engineering import compute_features
from app.fraud_engine.risk_scoring import compute_risk_score, severity_from_level

settings = get_settings()

celery_app = Celery(
    "intellitrace",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    timezone="UTC",
)

logger = structlog.get_logger(__name__)


def _run_async(coro):
    """Helper to run async code inside a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10, name="tasks.compute_fraud_score")
def compute_fraud_score(self, invoice_id: str) -> dict:
    """
    Background fraud scoring pipeline.

    Steps:
      1. Fetch invoice from DB
      2. Fetch supplier history
      3. Build supply chain graph
      4. Compute feature vector
      5. Run risk scoring (ML + rules)
      6. Persist fraud_score / risk_level / breakdown to invoice
      7. Generate alerts if triggered
    """
    try:
        result = _run_async(_score_invoice(invoice_id))
        logger.info("fraud_score_computed", invoice_id=invoice_id, score=result.get("fraud_score"))
        return result
    except Exception as exc:
        logger.error("fraud_score_failed", invoice_id=invoice_id, error=str(exc))
        raise self.retry(exc=exc)


async def _score_invoice(invoice_id: str) -> dict:
    from app.database import AsyncSessionLocal
    from app.models.invoice import Invoice
    from app.models.supplier import Supplier
    from app.models.alert import Alert
    from app.models.purchase_order import PurchaseOrder

    async with AsyncSessionLocal() as db:
        # ── 1. Fetch invoice ──────────────────────────────────────────────────
        invoice = await db.get(Invoice, invoice_id)
        if not invoice:
            raise ValueError(f"Invoice {invoice_id} not found")

        supplier = await db.get(Supplier, invoice.supplier_id)
        if not supplier:
            raise ValueError(f"Supplier {invoice.supplier_id} not found")

        # ── 2. Supplier invoice history in last 30 days ───────────────────────
        window_start = date.today() - timedelta(days=settings.VELOCITY_WINDOW_DAYS)
        stmt = select(func.count()).where(
            Invoice.supplier_id == supplier.id,
            Invoice.invoice_date >= window_start,
        )
        result = await db.execute(stmt)
        invoice_count_30d: int = result.scalar_one()

        # Total financed value for this supplier
        stmt = select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(
            Invoice.supplier_id == supplier.id
        )
        result = await db.execute(stmt)
        total_financed: float = float(result.scalar_one())

        # Supplier age in days
        days_active = max(1, (date.today() - supplier.created_at.date()).days)

        # ── 3. PO amount lookup ───────────────────────────────────────────────
        po_amount: float | None = None
        if invoice.po_id:
            po = await db.get(PurchaseOrder, invoice.po_id)
            po_amount = float(po.po_amount) if po else None

        # ── 4. Build graph ────────────────────────────────────────────────────
        graph = SupplyChainGraph()
        graph.add_invoice(
            invoice_id=invoice.id,
            supplier_id=str(supplier.id),
            buyer_id=str(invoice.buyer_id),
            lender_id=str(invoice.lender_id) if invoice.lender_id else None,
            tier=supplier.tier_level,
        )
        graph_features = graph.extract_features_for_supplier(str(supplier.id))

        # ── 5. Feature engineering ────────────────────────────────────────────
        revenue_ratio = total_financed / float(supplier.annual_revenue) if supplier.annual_revenue else 0.0
        features = compute_features(
            total_financed_value=total_financed,
            annual_revenue=float(supplier.annual_revenue),
            invoice_count_30d=invoice_count_30d,
            velocity_window_days=settings.VELOCITY_WINDOW_DAYS,
            financing_count=invoice.financing_count,
            days_active=days_active,
            is_duplicate=invoice.financing_count > 1,
            graph_features=graph_features,
            revenue_ratio_threshold=settings.REVENUE_RATIO_THRESHOLD,
            velocity_threshold=settings.VELOCITY_THRESHOLD,
            cascade_depth_threshold=settings.CASCADE_DEPTH_THRESHOLD,
        )

        # ── 6. Risk scoring ───────────────────────────────────────────────────
        scoring = compute_risk_score(
            features=features,
            revenue_ratio=revenue_ratio,
            invoice_count_30d=invoice_count_30d,
            financing_count=invoice.financing_count,
            invoice_amount=float(invoice.amount),
            po_amount=po_amount,
            cascade_depth=graph_features.cascade_depth,
            cycle_flag=graph_features.cycle_flag,
            revenue_ratio_threshold=settings.REVENUE_RATIO_THRESHOLD,
            velocity_threshold=settings.VELOCITY_THRESHOLD,
            cascade_depth_threshold=settings.CASCADE_DEPTH_THRESHOLD,
        )

        # ── 7. Persist ────────────────────────────────────────────────────────
        invoice.fraud_score = scoring.fraud_score
        invoice.risk_level = scoring.risk_level
        invoice.risk_category = scoring.risk_category
        invoice.risk_breakdown = scoring.risk_breakdown.to_dict()
        db.add(invoice)

        # ── 8. Generate alerts ────────────────────────────────────────────────
        for alert_type in scoring.triggered_alerts:
            alert = Alert(
                id=uuid.uuid4(),
                invoice_id=invoice.id,
                supplier_id=supplier.id,
                alert_type=alert_type,
                severity=severity_from_level(scoring.risk_level),
                status="Open",
            )
            db.add(alert)

        await db.commit()

        return {
            "invoice_id": invoice_id,
            "fraud_score": scoring.fraud_score,
            "risk_level": scoring.risk_level,
            "risk_category": scoring.risk_category,
            "triggered_alerts": scoring.triggered_alerts,
        }
