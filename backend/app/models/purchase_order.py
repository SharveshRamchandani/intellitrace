import uuid
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. PO-2024-0001
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    po_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    buyer: Mapped["Buyer"] = relationship(back_populates="purchase_orders")  # noqa: F821
    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")  # noqa: F821
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="purchase_order", lazy="select")  # noqa: F821

    def __repr__(self) -> str:
        return f"<PurchaseOrder id={self.id} amount={self.po_amount}>"
