import uuid
from datetime import date, datetime
from sqlalchemy import String, Numeric, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount_paid: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="payments")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Payment id={self.id} invoice={self.invoice_id} amount={self.amount_paid}>"
