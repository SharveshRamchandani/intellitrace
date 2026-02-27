import uuid
from datetime import date, datetime
from sqlalchemy import String, Numeric, Integer, Float, Date, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # INV-2024-XXXX

    # ── Foreign Keys ─────────────────────────────────────────────────────────
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    po_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True
    )

    # ── Invoice Data ─────────────────────────────────────────────────────────
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    grn_id: Mapped[str | None] = mapped_column(String(50), nullable=True)   # Goods Receipt Note
    lender_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    financing_count: Mapped[int] = mapped_column(Integer, default=1)         # times financed

    # ── Fraud Output ─────────────────────────────────────────────────────────
    fraud_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(10), nullable=True)  # low|medium|high
    risk_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    supplier: Mapped["Supplier"] = relationship(back_populates="invoices")  # noqa: F821
    buyer: Mapped["Buyer"] = relationship(back_populates="invoices")  # noqa: F821
    purchase_order: Mapped["PurchaseOrder | None"] = relationship(back_populates="invoices")  # noqa: F821
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice", lazy="select")  # noqa: F821
    alerts: Mapped[list["Alert"]] = relationship(back_populates="invoice", lazy="select")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Invoice id={self.id} amount={self.amount} score={self.fraud_score}>"
