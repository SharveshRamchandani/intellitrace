"""
seed_db.py
──────────
Run with: python seed_db.py

Populates the database with realistic supply chain data:
  - 8 suppliers (tiers 1-3), 5 buyers, 10 purchase orders
  - ~120 invoices over 12 months with pre-computed fraud scores
  - Alerts for high-risk invoices
  - Payments for settled invoices

Usage:
    python seed_db.py [--reset]   # --reset drops and recreates all tables
"""
from __future__ import annotations

import asyncio
import random
import sys
import uuid
from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ── Bootstrap env / settings before any app imports ──────────────────────────
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings  # noqa: E402
from app.database import AsyncSessionLocal, Base, engine  # noqa: E402
from app.models.supplier import Supplier  # noqa: E402
from app.models.buyer import Buyer  # noqa: E402
from app.models.purchase_order import PurchaseOrder  # noqa: E402
from app.models.invoice import Invoice  # noqa: E402
from app.models.payment import Payment  # noqa: E402
from app.models.alert import Alert  # noqa: E402

# Import all models so Base sees them all
import app.models  # noqa: F401

settings = get_settings()
random.seed(42)

RESET = "--reset" in sys.argv


# ── Seed Data Definitions ────────────────────────────────────────────────────

SUPPLIERS = [
    # (name, tier, annual_revenue)
    ("Apex Components Ltd",       1, 12_000_000.00),
    ("BlueStar Manufacturing",    1, 8_500_000.00),
    ("Cascade Metals Inc",        2, 3_200_000.00),
    ("DeltaForge Supplies",       2, 2_750_000.00),
    ("Echo Precision Parts",      2, 1_980_000.00),
    ("Frontier Raw Materials",    3, 950_000.00),
    ("GridLine Electronics",      3, 720_000.00),
    ("HorizonTech Components",    3, 610_000.00),
]

BUYERS = [
    "AutoNova Industries",
    "Zenith Manufacturing Corp",
    "PrimeFlow Logistics",
    "Nexus Assembly Ltd",
    "Atlas Production Systems",
]

# Fraud scenarios — which suppliers behave suspiciously
# Supplier index → scenario
FRAUD_SCENARIOS = {
    5: "carousel",       # Frontier Raw Materials — circular financing
    6: "velocity",       # GridLine Electronics — too many invoices
    2: "revenue",        # Cascade Metals — revenue mismatch
    7: "duplicate",      # HorizonTech — duplicate invoicing
}


def today_minus(days: int) -> date:
    return date.today() - timedelta(days=days)


def rand_date_in_month(months_ago: int) -> date:
    """Return a random date in a month `months_ago` months back."""
    ref = date.today().replace(day=1)
    for _ in range(months_ago):
        ref = (ref - timedelta(days=1)).replace(day=1)
    # Random day in that month
    next_month = (ref.replace(day=28) + timedelta(days=4)).replace(day=1)
    days_in_month = (next_month - ref).days
    return ref + timedelta(days=random.randint(0, days_in_month - 1))


async def reset_db() -> None:
    """Drop all tables and recreate. DESTRUCTIVE."""
    print("⚠️  Resetting database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables recreated.")


async def create_tables() -> None:
    """Create tables if they don't already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed(db: AsyncSession) -> None:  # noqa: C901
    print("🌱 Starting seed...")

    # ── 1. Suppliers ──────────────────────────────────────────────────────────
    supplier_objs: list[Supplier] = []
    for name, tier, revenue in SUPPLIERS:
        s = Supplier(
            id=uuid.uuid4(),
            name=name,
            tier_level=tier,
            annual_revenue=revenue,
        )
        db.add(s)
        supplier_objs.append(s)
    await db.flush()
    print(f"  ✓ {len(supplier_objs)} suppliers")

    # ── 2. Buyers ─────────────────────────────────────────────────────────────
    buyer_objs: list[Buyer] = []
    for name in BUYERS:
        b = Buyer(id=uuid.uuid4(), name=name)
        db.add(b)
        buyer_objs.append(b)
    await db.flush()
    print(f"  ✓ {len(buyer_objs)} buyers")

    # ── 3. Purchase Orders ────────────────────────────────────────────────────
    po_objs: list[PurchaseOrder] = []
    for i, supplier in enumerate(supplier_objs[:5]):  # Tier 1+2 only get POs
        for j in range(2):
            po_id = f"PO-2024-{i * 2 + j + 1:04d}"
            buyer = buyer_objs[i % len(buyer_objs)]
            po = PurchaseOrder(
                id=po_id,
                buyer_id=buyer.id,
                supplier_id=supplier.id,
                po_amount=round(random.uniform(50_000, 500_000), 2),
            )
            db.add(po)
            po_objs.append(po)
    await db.flush()
    print(f"  ✓ {len(po_objs)} purchase orders")

    # ── 4. Invoices ───────────────────────────────────────────────────────────
    invoices: list[Invoice] = []
    inv_counter = 1

    def make_invoice_id() -> str:
        nonlocal inv_counter
        iid = f"INV-2024-{inv_counter:04d}"
        inv_counter += 1
        return iid

    # Normal invoices across all suppliers (months 1–12)
    for sup_idx, supplier in enumerate(supplier_objs):
        scenario = FRAUD_SCENARIOS.get(sup_idx)
        months_range = 12
        invoices_per_month = 2

        # Velocity-fraud supplier gets 8+ invoices per month
        if scenario == "velocity":
            invoices_per_month = 9

        for months_ago in range(months_range, -1, -1):
            for _ in range(invoices_per_month):
                buyer = random.choice(buyer_objs)
                inv_date = rand_date_in_month(months_ago)

                # Base amount
                base_amount = random.uniform(10_000, 200_000)

                # Revenue mismatch: inflate amounts heavily
                if scenario == "revenue":
                    base_amount *= random.uniform(3.5, 5.0)

                # Duplicate: same invoice submitted multiple times
                financing_count = 1
                if scenario == "duplicate" and random.random() < 0.4:
                    financing_count = random.choice([2, 3])

                # Assign PO if available
                po_id = None
                po_obj = None
                supplier_pos = [p for p in po_objs if p.supplier_id == supplier.id]
                if supplier_pos and random.random() < 0.7:
                    po_obj = random.choice(supplier_pos)
                    po_id = po_obj.id
                    # PO mismatch: occasionally bill more than PO
                    if random.random() < 0.2:
                        base_amount = float(po_obj.po_amount) * random.uniform(1.15, 1.8)

                amount = round(base_amount, 2)

                # Pre-compute a realistic fraud score
                fraud_score, risk_level, risk_category, breakdown = _compute_seed_score(
                    sup_idx, scenario, financing_count, po_obj, amount
                )

                lender_id = None
                if scenario == "carousel" and random.random() < 0.6:
                    lender_id = uuid.uuid4()  # external lender node

                inv = Invoice(
                    id=make_invoice_id(),
                    supplier_id=supplier.id,
                    buyer_id=buyer.id,
                    amount=amount,
                    invoice_date=inv_date,
                    po_id=po_id,
                    grn_id=f"GRN-{inv_counter - 1:04d}" if random.random() < 0.8 else None,
                    lender_id=lender_id,
                    financing_count=financing_count,
                    fraud_score=fraud_score,
                    risk_level=risk_level,
                    risk_category=risk_category,
                    risk_breakdown=breakdown,
                )
                db.add(inv)
                invoices.append(inv)

    await db.flush()
    print(f"  ✓ {len(invoices)} invoices")

    # ── 5. Payments (for ~60% of invoices) ────────────────────────────────────
    payment_count = 0
    for inv in invoices:
        if random.random() < 0.6:
            pay_date = inv.invoice_date + timedelta(days=random.randint(7, 45))
            if pay_date > date.today():
                continue
            p = Payment(
                id=uuid.uuid4(),
                invoice_id=inv.id,
                amount_paid=inv.amount,
                payment_date=pay_date,
            )
            db.add(p)
            payment_count += 1
    await db.flush()
    print(f"  ✓ {payment_count} payments")

    # ── 6. Alerts (for high-risk invoices) ────────────────────────────────────
    alert_count = 0
    for inv in invoices:
        if inv.fraud_score is not None and inv.fraud_score >= 55.0:
            severity = "high" if inv.fraud_score >= 71 else "medium"
            # Determine alert types to fire
            alert_types = _get_alert_types(inv)
            for alert_type in alert_types:
                a = Alert(
                    id=uuid.uuid4(),
                    invoice_id=inv.id,
                    supplier_id=inv.supplier_id,
                    alert_type=alert_type,
                    severity=severity,
                    status=random.choice(["Open", "Open", "Open", "Reviewed", "Resolved"]),
                )
                db.add(a)
                alert_count += 1
    await db.flush()
    print(f"  ✓ {alert_count} alerts")

    await db.commit()
    print("✅ Seed complete!")


def _compute_seed_score(
    sup_idx: int,
    scenario: str | None,
    financing_count: int,
    po_obj: PurchaseOrder | None,
    amount: float,
) -> tuple[float, str, str, dict]:
    """
    Deterministic fraud scoring for seed data.
    Matches the same risk thresholds used by the real fraud engine.
    """
    score = random.uniform(5, 25)  # baseline noise

    if scenario == "revenue":
        score = random.uniform(72, 95)
        risk_category = "Revenue Mismatch"
        breakdown = {"revenueMismatch": score * 0.9, "velocityAnomaly": 0, "cascadeRisk": 0, "carouselRisk": 0, "duplicateRisk": 0}
    elif scenario == "velocity":
        score = random.uniform(65, 88)
        risk_category = "Velocity Anomaly"
        breakdown = {"revenueMismatch": 0, "velocityAnomaly": score * 0.85, "cascadeRisk": 0, "carouselRisk": 0, "duplicateRisk": 0}
    elif scenario == "carousel":
        score = random.uniform(78, 97)
        risk_category = "Carousel Risk"
        breakdown = {"revenueMismatch": 0, "velocityAnomaly": 0, "cascadeRisk": score * 0.4, "carouselRisk": score * 0.9, "duplicateRisk": 0}
    elif scenario == "duplicate" and financing_count > 1:
        score = random.uniform(70, 90)
        risk_category = "Duplicate"
        breakdown = {"revenueMismatch": 0, "velocityAnomaly": 0, "cascadeRisk": 0, "carouselRisk": 0, "duplicateRisk": score * 0.85}
    else:
        # Normal supplier — mostly low risk with occasional medium
        if random.random() < 0.15:
            score = random.uniform(42, 65)
            risk_category = random.choice(["PO Mismatch", "Velocity Anomaly"])
        else:
            score = random.uniform(5, 38)
            risk_category = random.choice(["Revenue Mismatch", "PO Mismatch"])
        breakdown = {
            "revenueMismatch": round(random.uniform(0, score * 0.5), 1),
            "velocityAnomaly": round(random.uniform(0, score * 0.3), 1),
            "cascadeRisk": round(random.uniform(0, score * 0.2), 1),
            "carouselRisk": 0.0,
            "duplicateRisk": 0.0,
        }

    score = round(min(100.0, max(0.0, score)), 1)
    risk_level = "high" if score >= 71 else ("medium" if score >= 41 else "low")

    if scenario not in ("revenue", "velocity", "carousel", "duplicate"):
        pass  # breakdown already set above

    # Normalize breakdown dict
    if isinstance(breakdown, dict):
        for k in breakdown:
            breakdown[k] = round(float(breakdown[k]), 1)

    return score, risk_level, risk_category, breakdown


def _get_alert_types(inv: Invoice) -> list[str]:
    """Determine which alert types to raise for a seeded invoice."""
    types: list[str] = []
    bd = inv.risk_breakdown or {}

    if bd.get("revenueMismatch", 0) > 40:
        types.append("Revenue Mismatch")
    if bd.get("velocityAnomaly", 0) > 40:
        types.append("Velocity Anomaly")
    if bd.get("cascadeRisk", 0) > 40:
        types.append("Cascade Risk")
    if bd.get("carouselRisk", 0) > 50:
        types.append("Carousel Risk")
    if bd.get("duplicateRisk", 0) > 40:
        types.append("Duplicate")
    if inv.po_id is None and float(inv.amount) > 50_000:
        if random.random() < 0.2:
            types.append("PO Mismatch")

    # Always add at least one alert for high-risk invoices
    if not types:
        types.append("Revenue Mismatch")

    return types


async def main() -> None:
    if RESET:
        await reset_db()
    else:
        await create_tables()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select, func
        count_result = await db.execute(select(func.count()).select_from(Supplier))
        existing = count_result.scalar_one()
        if existing > 0 and not RESET:
            print(f"⚠️  Database already has {existing} suppliers. Run with --reset to reseed.")
            return

        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
