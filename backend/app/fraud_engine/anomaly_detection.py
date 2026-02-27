"""
anomaly_detection.py
─────────────────────
Rule-based anomaly detectors that run alongside the ML model.
Each detector returns a score contribution (0–100) and a description.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnomalyResult:
    flag: bool
    score: float          # contribution 0–100
    description: str


def detect_revenue_mismatch(
    revenue_ratio: float,
    threshold: float = 2.0,
) -> AnomalyResult:
    """Revenue Mismatch: total financed / annual revenue > threshold."""
    if revenue_ratio <= 1.0:
        return AnomalyResult(False, 0.0, "")
    # Scale: ratio=1x → 10pts, ratio=threshold → 95pts
    raw_score = min(95.0, (revenue_ratio / threshold) * 95.0)
    flag = revenue_ratio > threshold
    desc = (
        f"Revenue ratio {revenue_ratio:.2f}x — "
        f"{'abnormally high' if flag else 'elevated'} financing vs revenue"
    )
    return AnomalyResult(flag, round(raw_score, 1), desc if flag else "")


def detect_velocity_anomaly(
    invoice_count_30d: int,
    threshold: int = 20,
) -> AnomalyResult:
    """Velocity Anomaly: invoice submission rate exceeds threshold."""
    if invoice_count_30d <= threshold // 2:
        return AnomalyResult(False, 0.0, "")
    raw_score = min(90.0, (invoice_count_30d / threshold) * 90.0)
    flag = invoice_count_30d > threshold
    desc = f"Velocity anomaly: {invoice_count_30d} invoices in 30 days (threshold {threshold})" if flag else ""
    return AnomalyResult(flag, round(raw_score, 1), desc)


def detect_duplicate(
    duplicate_count: int,
) -> AnomalyResult:
    """Duplicate Financing: invoice financed more than once."""
    flag = duplicate_count > 1
    score = min(85.0, duplicate_count * 42.5) if flag else 0.0
    desc = f"Possible duplicate detected — financed {duplicate_count} times" if flag else ""
    return AnomalyResult(flag, round(score, 1), desc)


def detect_po_mismatch(
    invoice_amount: float,
    po_amount: float | None,
) -> AnomalyResult:
    """PO Mismatch: invoice amount significantly exceeds PO amount."""
    if po_amount is None or po_amount <= 0:
        return AnomalyResult(False, 0.0, "")
    ratio = invoice_amount / po_amount
    if ratio <= 1.05:   # 5% tolerance
        return AnomalyResult(False, 0.0, "")
    score = min(80.0, (ratio - 1.0) * 80.0)
    flag = ratio > 1.10
    desc = f"Invoice amount {ratio:.2f}x greater than PO amount" if flag else ""
    return AnomalyResult(flag, round(score, 1), desc)


def detect_cascade(
    cascade_depth: int,
    threshold: int = 3,
) -> AnomalyResult:
    """Cascade Risk: deep multi-tier supply chain detected."""
    if cascade_depth <= 1:
        return AnomalyResult(False, 0.0, "")
    score = min(90.0, (cascade_depth / threshold) * 90.0)
    flag = cascade_depth >= threshold
    desc = f"Cascade depth {cascade_depth} — cross-tier cascade risk" if flag else ""
    return AnomalyResult(flag, round(score, 1), desc)


def detect_carousel(
    cycle_flag: bool,
) -> AnomalyResult:
    """Carousel Risk: circular financing cycle detected in graph."""
    if not cycle_flag:
        return AnomalyResult(False, 0.0, "")
    return AnomalyResult(True, 92.0, "Circular financing carousel cycle detected")
