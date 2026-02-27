"""
dashboard_service.py
─────────────────────
Aggregates all data for the GET /api/dashboard endpoint.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, timedelta, datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.supplier import Supplier
from app.schemas.dashboard import (
    DashboardResponse, KPIMetric, RiskDistributionItem,
    VolumeDataPoint, SparklineData,
)

logger = logging.getLogger(__name__)

MONTH_ABBREVS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

RISK_CATEGORIES = [
    ("Revenue Mismatch", "high"),
    ("Velocity Anomaly", "medium"),
    ("Cascade Risk", "high"),
    ("Carousel Risk", "medium"),
    ("Duplicate", "low"),
    ("PO Mismatch", "low"),
]


async def get_dashboard(db: AsyncSession) -> DashboardResponse:
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    # ── Total invoices today ──────────────────────────────────────────────────
    today_count = await _count_invoices(db, today, today)
    yesterday_count = await _count_invoices(db, yesterday, yesterday)
    total_trend = _pct_change(today_count, yesterday_count)

    # ── High-risk invoices (score >= 71) ─────────────────────────────────────
    high_risk_today = await _count_invoices(db, today, today, min_score=71.0)
    high_risk_yesterday = await _count_invoices(db, yesterday, yesterday, min_score=71.0)
    high_risk_trend = _pct_change(high_risk_today, high_risk_yesterday)

    # ── Suspicious suppliers (at least one high-risk invoice this week) ──────
    susp_stmt = (
        select(func.count(func.distinct(Invoice.supplier_id)))
        .where(
            Invoice.fraud_score >= 71.0,
            Invoice.invoice_date >= last_week,
        )
    )
    susp_result = await db.execute(susp_stmt)
    suspicious_count = susp_result.scalar_one() or 0

    susp_last = (
        select(func.count(func.distinct(Invoice.supplier_id)))
        .where(
            Invoice.fraud_score >= 71.0,
            Invoice.invoice_date >= last_week - timedelta(days=7),
            Invoice.invoice_date < last_week,
        )
    )
    susp_last_result = await db.execute(susp_last)
    suspicious_last = susp_last_result.scalar_one() or 0
    susp_trend = _pct_change(suspicious_count, suspicious_last)

    # ── Exposure value (sum of high-risk invoice amounts today) ───────────────
    exp_stmt = select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(
        Invoice.fraud_score >= 71.0,
        Invoice.invoice_date >= today - timedelta(days=30),
    )
    exp_result = await db.execute(exp_stmt)
    exposure = float(exp_result.scalar_one())

    exp_prev_stmt = select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(
        Invoice.fraud_score >= 71.0,
        Invoice.invoice_date >= today - timedelta(days=60),
        Invoice.invoice_date < today - timedelta(days=30),
    )
    exp_prev_result = await db.execute(exp_prev_stmt)
    exposure_prev = float(exp_prev_result.scalar_one())
    exposure_trend = _pct_change(exposure, exposure_prev)

    # ── Fraud risk distribution ───────────────────────────────────────────────
    distribution: list[RiskDistributionItem] = []
    for category, risk_level in RISK_CATEGORIES:
        count_stmt = select(func.count()).where(Invoice.risk_category == category)
        count_result = await db.execute(count_stmt)
        cat_count = count_result.scalar_one() or 0
        distribution.append(RiskDistributionItem(
            category=category, count=cat_count, risk=risk_level
        ))

    # ── Invoice volume data (last 7 months) ───────────────────────────────────
    volume_data: list[VolumeDataPoint] = await _build_volume_data(db, today)

    # ── Sparkline data (12 data points each) ─────────────────────────────────
    sparklines = await _build_sparklines(db, today)

    return DashboardResponse(
        totalInvoices=KPIMetric(
            value=today_count,
            trend=round(abs(total_trend), 1),
            direction="up" if total_trend >= 0 else "down",
        ),
        highRiskInvoices=KPIMetric(
            value=high_risk_today,
            trend=round(abs(high_risk_trend), 1),
            direction="up" if high_risk_trend >= 0 else "down",
        ),
        suspiciousSuppliers=KPIMetric(
            value=suspicious_count,
            trend=round(abs(susp_trend), 1),
            direction="up" if susp_trend >= 0 else "down",
        ),
        exposureValue=KPIMetric(
            value=round(exposure, 2),
            trend=round(abs(exposure_trend), 1),
            direction="up" if exposure_trend >= 0 else "down",
        ),
        sparklineData=sparklines,
        fraudRiskDistribution=distribution,
        invoiceVolumeData=volume_data,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _count_invoices(
    db: AsyncSession,
    from_date: date,
    to_date: date,
    min_score: float | None = None,
) -> int:
    stmt = select(func.count()).where(
        Invoice.invoice_date >= from_date,
        Invoice.invoice_date <= to_date,
    )
    if min_score is not None:
        stmt = stmt.where(Invoice.fraud_score >= min_score)
    result = await db.execute(stmt)
    return result.scalar_one() or 0


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


async def _build_volume_data(db: AsyncSession, today: date) -> list[VolumeDataPoint]:
    points: list[VolumeDataPoint] = []
    for i in range(6, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=30 * i))
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        abbrev = MONTH_ABBREVS[month_start.month - 1]

        count_stmt = select(func.count()).where(
            Invoice.invoice_date >= month_start,
            Invoice.invoice_date <= month_end,
        )
        rev_stmt = select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(
            Invoice.invoice_date >= month_start,
            Invoice.invoice_date <= month_end,
        )
        count_r = await db.execute(count_stmt)
        rev_r = await db.execute(rev_stmt)
        points.append(VolumeDataPoint(
            month=abbrev,
            invoices=count_r.scalar_one() or 0,
            revenue=round(float(rev_r.scalar_one()) / 1000, 1),  # in $K
        ))
    return points


async def _build_sparklines(db: AsyncSession, today: date) -> SparklineData:
    """Build 12 data points (one per month for the last year) for each KPI."""
    total_pts, high_pts, susp_pts, exp_pts = [], [], [], []

    for i in range(11, -1, -1):
        month_start = (today.replace(day=1) - timedelta(days=30 * i))
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        t_stmt = select(func.count()).where(
            Invoice.invoice_date >= month_start, Invoice.invoice_date <= month_end
        )
        h_stmt = select(func.count()).where(
            Invoice.invoice_date >= month_start,
            Invoice.invoice_date <= month_end,
            Invoice.fraud_score >= 71.0,
        )
        e_stmt = select(func.coalesce(func.sum(Invoice.amount), 0.0)).where(
            Invoice.invoice_date >= month_start,
            Invoice.invoice_date <= month_end,
            Invoice.fraud_score >= 71.0,
        )
        s_stmt = select(func.count(func.distinct(Invoice.supplier_id))).where(
            Invoice.invoice_date >= month_start,
            Invoice.invoice_date <= month_end,
            Invoice.fraud_score >= 71.0,
        )

        for stmt, pts in [(t_stmt, total_pts), (h_stmt, high_pts), (s_stmt, susp_pts)]:
            r = await db.execute(stmt)
            pts.append(float(r.scalar_one() or 0))

        e_r = await db.execute(e_stmt)
        exp_pts.append(round(float(e_r.scalar_one()) / 1_000_000, 2))  # in $M

    return SparklineData(
        totalInvoices=total_pts,
        highRiskInvoices=high_pts,
        suspiciousSuppliers=susp_pts,
        exposureValue=exp_pts,
    )
