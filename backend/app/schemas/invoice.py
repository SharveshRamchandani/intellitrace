from __future__ import annotations
import uuid
from datetime import date, datetime
from pydantic import BaseModel, field_validator, ConfigDict


# ── Sub-schemas ───────────────────────────────────────────────────────────────

class RiskBreakdown(BaseModel):
    """Matches frontend riskBreakdown shape exactly."""
    revenueMismatch: float = 0.0
    velocityAnomaly: float = 0.0
    cascadeRisk: float = 0.0
    carouselRisk: float = 0.0
    duplicateRisk: float = 0.0


# ── Request ───────────────────────────────────────────────────────────────────

class InvoiceCreate(BaseModel):
    """Payload to POST /api/invoices."""
    id: str                             # e.g. INV-2024-0001
    supplier_id: uuid.UUID
    buyer_id: uuid.UUID
    amount: float
    invoice_date: date
    po_id: str | None = None
    grn_id: str | None = None
    lender_id: uuid.UUID | None = None
    financing_count: int = 1

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("amount must be positive")
        return v

    @field_validator("id")
    @classmethod
    def id_format(cls, v: str) -> str:
        if not v.startswith("INV-"):
            raise ValueError("Invoice ID must start with 'INV-'")
        return v


# ── Responses ─────────────────────────────────────────────────────────────────

class InvoiceListItem(BaseModel):
    """Compact invoice row — matches frontend FlaggedInvoice type."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    supplier: str           # supplier.name (denormalized)
    tier: int               # supplier.tier_level
    amount: float
    riskScore: float | None = None
    riskCategory: str | None = None


class InvoiceResponse(BaseModel):
    """Standard invoice response after creation."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    supplier_id: uuid.UUID
    buyer_id: uuid.UUID
    amount: float
    invoice_date: date
    fraud_score: float | None = None
    risk_level: str | None = None
    risk_category: str | None = None
    created_at: datetime


class InvoiceDetailResponse(BaseModel):
    """
    Full invoice detail — matches frontend invoiceDetail shape.
    Used by GET /api/invoices/{id}
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    supplier: str
    buyer: str
    tier: int
    amount: float
    poMatch: bool
    grnMatch: bool
    duplicateStatus: str | None
    financingCount: int
    riskScore: float
    riskBreakdown: RiskBreakdown
    createdAt: datetime


class TaskAccepted(BaseModel):
    """Response when a Celery task is dispatched."""
    invoice_id: str
    task_id: str
    message: str = "Fraud scoring queued"
