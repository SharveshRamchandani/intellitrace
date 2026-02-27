"""
risk_scoring.py
───────────────
Combines ML probability + rule-based anomaly signals into a
final fraud_score (0–100) and a risk_level / risk_category.

Final score formula:
  ml_contribution  = ml_prob * 100 * 0.45
  rule_contribution = weighted_avg(anomaly_scores) * 0.55
  fraud_score = clamp(ml + rule, 0, 100)

Risk breakdown (matches frontend riskBreakdown shape):
  revenueMismatch, velocityAnomaly, cascadeRisk, carouselRisk, duplicateRisk
"""
from __future__ import annotations

from dataclasses import dataclass

from app.fraud_engine.feature_engineering import FeatureVector
from app.fraud_engine.anomaly_detection import (
    AnomalyResult,
    detect_revenue_mismatch,
    detect_velocity_anomaly,
    detect_duplicate,
    detect_po_mismatch,
    detect_cascade,
    detect_carousel,
)
from app.fraud_engine import model as fraud_model


# ── Output types ──────────────────────────────────────────────────────────────

@dataclass
class RiskBreakdown:
    revenueMismatch: float
    velocityAnomaly: float
    cascadeRisk: float
    carouselRisk: float
    duplicateRisk: float

    def to_dict(self) -> dict:
        return {
            "revenueMismatch": self.revenueMismatch,
            "velocityAnomaly": self.velocityAnomaly,
            "cascadeRisk": self.cascadeRisk,
            "carouselRisk": self.carouselRisk,
            "duplicateRisk": self.duplicateRisk,
        }


@dataclass
class ScoringResult:
    fraud_score: float               # 0–100
    risk_level: str                  # low | medium | high
    risk_category: str               # dominant alert type
    risk_breakdown: RiskBreakdown
    ml_probability: float            # raw ML output
    triggered_alerts: list[str]      # list of alert type strings
    alert_descriptions: dict[str, str]  # alert_type → human description


# ── Scoring pipeline ──────────────────────────────────────────────────────────

def compute_risk_score(
    *,
    features: FeatureVector,
    revenue_ratio: float,
    invoice_count_30d: int,
    financing_count: int,
    invoice_amount: float,
    po_amount: float | None,
    cascade_depth: int,
    cycle_flag: bool,
    revenue_ratio_threshold: float = 2.0,
    velocity_threshold: int = 20,
    cascade_depth_threshold: int = 3,
) -> ScoringResult:
    """
    Full scoring pipeline:
      1. Run ML model inference
      2. Run all rule-based detectorsN
      3. Combine into final score
      4. Determine risk level and primary category
    """
    # ── 1. ML inference ───────────────────────────────────────────────────────
    ml_prob = fraud_model.predict(features.to_list())

    # ── 2. Rule-based detectors ───────────────────────────────────────────────
    rev_result: AnomalyResult = detect_revenue_mismatch(revenue_ratio, revenue_ratio_threshold)
    vel_result: AnomalyResult = detect_velocity_anomaly(invoice_count_30d, velocity_threshold)
    dup_result: AnomalyResult = detect_duplicate(financing_count)
    po_result: AnomalyResult = detect_po_mismatch(invoice_amount, po_amount)
    cas_result: AnomalyResult = detect_cascade(cascade_depth, cascade_depth_threshold)
    car_result: AnomalyResult = detect_carousel(cycle_flag)

    # ── 3. Combine scores ─────────────────────────────────────────────────────
    ml_contribution = ml_prob * 100.0 * 0.45

    rule_scores = [
        rev_result.score,
        vel_result.score,
        dup_result.score,
        po_result.score,
        cas_result.score,
        car_result.score,
    ]
    rule_avg = sum(rule_scores) / len(rule_scores) if rule_scores else 0.0
    rule_contribution = rule_avg * 0.55

    fraud_score = round(min(100.0, max(0.0, ml_contribution + rule_contribution)), 1)

    # ── 4. Risk level ─────────────────────────────────────────────────────────
    if fraud_score >= 71:
        risk_level = "high"
    elif fraud_score >= 41:
        risk_level = "medium"
    else:
        risk_level = "low"

    # ── 5. Primary category (highest-scoring anomaly) ─────────────────────────
    category_map = {
        "Revenue Mismatch": rev_result.score,
        "Velocity Anomaly": vel_result.score,
        "Duplicate": dup_result.score,
        "PO Mismatch": po_result.score,
        "Cascade Risk": cas_result.score,
        "Carousel Risk": car_result.score,
    }
    risk_category = max(category_map, key=lambda k: category_map[k])

    # ── 6. Triggered alerts ───────────────────────────────────────────────────
    triggered: list[str] = []
    descriptions: dict[str, str] = {}

    result_map = {
        "Revenue Mismatch": rev_result,
        "Velocity Anomaly": vel_result,
        "Duplicate": dup_result,
        "PO Mismatch": po_result,
        "Cascade Risk": cas_result,
        "Carousel Risk": car_result,
    }
    for alert_type, result in result_map.items():
        if result.flag:
            triggered.append(alert_type)
            descriptions[alert_type] = result.description

    # ── 7. Risk breakdown ─────────────────────────────────────────────────────
    breakdown = RiskBreakdown(
        revenueMismatch=round(rev_result.score, 1),
        velocityAnomaly=round(vel_result.score, 1),
        cascadeRisk=round(cas_result.score, 1),
        carouselRisk=round(car_result.score, 1),
        duplicateRisk=round(dup_result.score, 1),
    )

    return ScoringResult(
        fraud_score=fraud_score,
        risk_level=risk_level,
        risk_category=risk_category,
        risk_breakdown=breakdown,
        ml_probability=ml_prob,
        triggered_alerts=triggered,
        alert_descriptions=descriptions,
    )


def severity_from_level(risk_level: str) -> str:
    """Map risk_level to alert severity string (same vocab)."""
    return risk_level  # one-to-one for now
