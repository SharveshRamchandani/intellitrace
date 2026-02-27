from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict


class FrequencyDataPoint(BaseModel):
    month: str
    count: int


class RiskTrendDataPoint(BaseModel):
    month: str
    score: float


# ── Request ───────────────────────────────────────────────────────────────────

class SupplierCreate(BaseModel):
    name: str
    tier_level: int
    annual_revenue: float

    @field_validator("tier_level")
    @classmethod
    def valid_tier(cls, v: int) -> int:
        if v not in (1, 2, 3):
            raise ValueError("tier_level must be 1, 2, or 3")
        return v

    @field_validator("annual_revenue")
    @classmethod
    def revenue_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("annual_revenue must be positive")
        return v


# ── Responses ─────────────────────────────────────────────────────────────────

class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    tier_level: int
    annual_revenue: float
    created_at: datetime


class SupplierProfileResponse(BaseModel):
    """
    Full supplier profile — matches frontend supplierData shape exactly.
    Used by GET /api/suppliers/{id}
    """
    id: uuid.UUID
    name: str
    tier: int                       # tier_level alias
    annualRevenue: float
    totalFinancedValue: float        # SUM of invoice amounts
    revenueRatio: float             # totalFinancedValue / annualRevenue
    isAbnormal: bool
    invoiceFrequency: list[FrequencyDataPoint]
    riskScoreTrend: list[RiskTrendDataPoint]


class SupplierListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    tier_level: int
    annual_revenue: float
    invoice_count: int = 0
    avg_risk_score: float = 0.0
