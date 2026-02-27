"""
feature_engineering.py
───────────────────────
Extracts a normalized feature vector from invoice + graph data.

Feature vector (7 dimensions):
  [0] revenue_ratio       – total financed / annual revenue
  [1] invoice_frequency   – invoices submitted in last 30 days (normalized)
  [2] financing_velocity  – financing_count / days_active (normalized)
  [3] duplicate_flag      – 0 or 1
  [4] cascade_depth       – BFS depth (normalized by threshold)
  [5] degree_centrality   – 0.0–1.0
  [6] cycle_flag          – 0 or 1
"""
from __future__ import annotations

from dataclasses import dataclass
from app.fraud_engine.graph_builder import GraphFeatures


@dataclass
class FeatureVector:
    revenue_ratio: float = 0.0
    invoice_frequency: float = 0.0
    financing_velocity: float = 0.0
    duplicate_flag: float = 0.0
    cascade_depth: float = 0.0
    degree_centrality: float = 0.0
    cycle_flag: float = 0.0

    def to_list(self) -> list[float]:
        return [
            self.revenue_ratio,
            self.invoice_frequency,
            self.financing_velocity,
            self.duplicate_flag,
            self.cascade_depth,
            self.degree_centrality,
            self.cycle_flag,
        ]


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def compute_features(
    *,
    total_financed_value: float,
    annual_revenue: float,
    invoice_count_30d: int,
    velocity_window_days: int,
    financing_count: int,
    days_active: int,
    is_duplicate: bool,
    graph_features: GraphFeatures,
    revenue_ratio_threshold: float = 2.0,
    velocity_threshold: int = 20,
    cascade_depth_threshold: int = 3,
) -> FeatureVector:
    """
    Compute & normalize all features into [0, 1].
    """
    # 1. Revenue ratio — normalize against threshold (threshold = 1.0)
    revenue_ratio = (total_financed_value / annual_revenue) if annual_revenue > 0 else 0.0
    norm_revenue_ratio = _clamp(revenue_ratio / revenue_ratio_threshold)

    # 2. Invoice frequency — invoices in window vs threshold
    norm_frequency = _clamp(invoice_count_30d / velocity_threshold)

    # 3. Financing velocity — times financed per day active
    if days_active > 0 and financing_count > 1:
        raw_velocity = financing_count / days_active
        norm_velocity = _clamp(raw_velocity * 30)   # per-month scale
    else:
        norm_velocity = 0.0

    # 4. Duplicate flag
    dup = 1.0 if is_duplicate else 0.0

    # 5. Cascade depth — normalize against threshold
    norm_cascade = _clamp(graph_features.cascade_depth / cascade_depth_threshold)

    # 6. Degree centrality already 0–1
    centrality = _clamp(graph_features.degree_centrality)

    # 7. Cycle flag
    cycle = 1.0 if graph_features.cycle_flag else 0.0

    return FeatureVector(
        revenue_ratio=round(norm_revenue_ratio, 4),
        invoice_frequency=round(norm_frequency, 4),
        financing_velocity=round(norm_velocity, 4),
        duplicate_flag=dup,
        cascade_depth=round(norm_cascade, 4),
        degree_centrality=centrality,
        cycle_flag=cycle,
    )
