from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlertCreate(BaseModel):
    invoice_id: str
    supplier_id: uuid.UUID
    alert_type: str
    severity: str   # high | medium | low


class AlertResponse(BaseModel):
    """Matches frontend alertsData shape."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str           # alert_type alias for frontend
    supplier: str       # supplier name (denormalized)
    invoice: str        # invoice_id alias for frontend
    severity: str
    timestamp: str      # formatted "YYYY-MM-DD HH:MM"
    status: str


class AlertStatusUpdate(BaseModel):
    status: str         # Open | Reviewed | Resolved
