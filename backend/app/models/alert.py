import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # alert_type: Revenue Mismatch | Cascade Risk | Velocity Anomaly |
    #              Carousel Risk | Duplicate | PO Mismatch
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False)   # high|medium|low
    status: Mapped[str] = mapped_column(String(20), default="Open")     # Open|Reviewed|Resolved
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    invoice: Mapped["Invoice"] = relationship(back_populates="alerts")  # noqa: F821
    supplier: Mapped["Supplier"] = relationship(back_populates="alerts")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Alert id={self.id} type={self.alert_type} severity={self.severity}>"
