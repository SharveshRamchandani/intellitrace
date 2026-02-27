"""
supplier_service.py
────────────────────
Business logic for supplier operations.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.supplier import Supplier
from app.models.invoice import Invoice
from app.schemas.supplier import (
    SupplierProfileResponse,
    SupplierListItem,
    FrequencyDataPoint,
    RiskTrendDataPoint,
)

logger = logging.getLogger(__name__)

MONTH_ABBREVS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


async def get_supplier_profile(
    db: AsyncSession, supplier_id: str
) -> SupplierProfileResponse | None:
    import uuid as _uuid
    try:
        uid = _uuid.UUID(supplier_id)
    except ValueError:
        return None
    supplier = await db.get(Supplier, uid)
    if not supplier:
        return None

    # Fetch all invoices for this supplier
    stmt = (
        select(Invoice)
        .where(Invoice.supplier_id == supplier.id)
        .order_by(Invoice.invoice_date)
    )
    result = await db.execute(stmt)
    invoices = result.scalars().all()

    total_financed = sum(float(inv.amount) for inv in invoices)
    annual_revenue = float(supplier.annual_revenue)
    revenue_ratio = round(total_financed / annual_revenue, 2) if annual_revenue > 0 else 0.0
    is_abnormal = revenue_ratio > 2.0

    # Build monthly frequency and risk trend (last 7 months)
    today = date.today()
    months = [(today.replace(day=1) - timedelta(days=30 * i)) for i in range(6, -1, -1)]

    freq_map: dict[str, int] = defaultdict(int)
    risk_map: dict[str, list[float]] = defaultdict(list)

    for inv in invoices:
        key = MONTH_ABBREVS[inv.invoice_date.month - 1]
        freq_map[key] += 1
        if inv.fraud_score is not None:
            risk_map[key].append(inv.fraud_score)

    invoice_frequency: list[FrequencyDataPoint] = []
    risk_score_trend: list[RiskTrendDataPoint] = []

    for m in months:
        abbrev = MONTH_ABBREVS[m.month - 1]
        invoice_frequency.append(FrequencyDataPoint(month=abbrev, count=freq_map.get(abbrev, 0)))
        scores = risk_map.get(abbrev, [])
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        risk_score_trend.append(RiskTrendDataPoint(month=abbrev, score=avg_score))

    return SupplierProfileResponse(
        id=supplier.id,
        name=supplier.name,
        tier=supplier.tier_level,
        annualRevenue=annual_revenue,
        totalFinancedValue=round(total_financed, 2),
        revenueRatio=revenue_ratio,
        isAbnormal=is_abnormal,
        invoiceFrequency=invoice_frequency,
        riskScoreTrend=risk_score_trend,
    )


async def list_suppliers(db: AsyncSession) -> list[SupplierListItem]:
    stmt = select(Supplier).order_by(Supplier.tier_level, Supplier.name)
    result = await db.execute(stmt)
    suppliers = result.scalars().all()

    items: list[SupplierListItem] = []
    for s in suppliers:
        # Count invoices and avg risk score
        inv_stmt = select(func.count(), func.avg(Invoice.fraud_score)).where(
            Invoice.supplier_id == s.id
        )
        inv_result = await db.execute(inv_stmt)
        count, avg_score = inv_result.one()
        items.append(SupplierListItem(
            id=s.id,
            name=s.name,
            tier_level=s.tier_level,
            annual_revenue=float(s.annual_revenue),
            invoice_count=count or 0,
            avg_risk_score=round(float(avg_score or 0), 1),
        ))

    return items
