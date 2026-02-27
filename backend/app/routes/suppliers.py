"""
routes/suppliers.py
────────────────────
GET /api/suppliers         — list all suppliers
GET /api/suppliers/{id}    — full supplier profile with charts
POST /api/suppliers        — create supplier
"""
from __future__ import annotations

import uuid
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierResponse, SupplierProfileResponse, SupplierListItem
from app.services import get_supplier_profile, list_suppliers

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.get("", response_model=list[SupplierListItem])
async def get_suppliers(db: AsyncSession = Depends(get_db)):
    """List all suppliers with invoice count and avg risk score."""
    return await list_suppliers(db)


@router.get("/{supplier_id}", response_model=SupplierProfileResponse)
async def get_supplier(supplier_id: str, db: AsyncSession = Depends(get_db)):
    """
    Full supplier profile — matches frontend supplierData shape:
    name, tier, annualRevenue, totalFinancedValue, revenueRatio,
    isAbnormal, invoiceFrequency, riskScoreTrend
    """
    profile = await get_supplier_profile(db, supplier_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Supplier '{supplier_id}' not found")
    return profile


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(payload: SupplierCreate, db: AsyncSession = Depends(get_db)):
    """Create a new supplier."""
    supplier = Supplier(
        id=uuid.uuid4(),
        name=payload.name,
        tier_level=payload.tier_level,
        annual_revenue=payload.annual_revenue,
    )
    db.add(supplier)
    await db.flush()
    logger.info("supplier_created", id=str(supplier.id), name=supplier.name)
    return supplier
