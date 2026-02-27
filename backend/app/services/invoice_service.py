"""
invoice_service.py
──────────────────
Business logic for invoice operations.
"""
from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.invoice import Invoice
from app.models.supplier import Supplier
from app.models.buyer import Buyer
from app.schemas.invoice import InvoiceCreate, InvoiceDetailResponse, InvoiceListItem, RiskBreakdown

logger = logging.getLogger(__name__)


async def create_invoice(db: AsyncSession, data: InvoiceCreate) -> Invoice:
    invoice = Invoice(
        id=data.id,
        supplier_id=data.supplier_id,
        buyer_id=data.buyer_id,
        amount=data.amount,
        invoice_date=data.invoice_date,
        po_id=data.po_id,
        grn_id=data.grn_id,
        lender_id=data.lender_id,
        financing_count=data.financing_count,
    )
    db.add(invoice)
    await db.flush()
    return invoice


async def get_invoice_detail(db: AsyncSession, invoice_id: str) -> InvoiceDetailResponse | None:
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.supplier), selectinload(Invoice.buyer))
        .where(Invoice.id == invoice_id)
    )
    result = await db.execute(stmt)
    inv = result.scalar_one_or_none()
    if not inv:
        return None

    # Determine PO/GRN match flags
    po_match = inv.po_id is not None  # simplification: having a po_id = matched
    grn_match = inv.grn_id is not None

    # Build duplicate status string
    dup_status: str | None = None
    if inv.financing_count > 1:
        dup_status = f"Possible duplicate detected — financed {inv.financing_count} times"

    breakdown_raw = inv.risk_breakdown or {}
    breakdown = RiskBreakdown(
        revenueMismatch=breakdown_raw.get("revenueMismatch", 0.0),
        velocityAnomaly=breakdown_raw.get("velocityAnomaly", 0.0),
        cascadeRisk=breakdown_raw.get("cascadeRisk", 0.0),
        carouselRisk=breakdown_raw.get("carouselRisk", 0.0),
        duplicateRisk=breakdown_raw.get("duplicateRisk", 0.0),
    )

    return InvoiceDetailResponse(
        id=inv.id,
        supplier=inv.supplier.name,
        buyer=inv.buyer.name,
        tier=inv.supplier.tier_level,
        amount=float(inv.amount),
        poMatch=po_match,
        grnMatch=grn_match,
        duplicateStatus=dup_status,
        financingCount=inv.financing_count,
        riskScore=inv.fraud_score or 0.0,
        riskBreakdown=breakdown,
        createdAt=inv.created_at,
    )


async def list_flagged_invoices(
    db: AsyncSession,
    limit: int = 50,
    min_risk_score: float | None = None,
) -> list[InvoiceListItem]:
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.supplier))
        .order_by(desc(Invoice.fraud_score))
        .limit(limit)
    )
    if min_risk_score is not None:
        stmt = stmt.where(Invoice.fraud_score >= min_risk_score)

    result = await db.execute(stmt)
    invoices = result.scalars().all()

    return [
        InvoiceListItem(
            id=inv.id,
            supplier=inv.supplier.name,
            tier=inv.supplier.tier_level,
            amount=float(inv.amount),
            riskScore=inv.fraud_score,
            riskCategory=inv.risk_category,
        )
        for inv in invoices
    ]
