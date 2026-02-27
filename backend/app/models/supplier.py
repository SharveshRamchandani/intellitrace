import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    tier_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 | 2 | 3
    annual_revenue: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="supplier", lazy="select")  # noqa: F821
    alerts: Mapped[list["Alert"]] = relationship(back_populates="supplier", lazy="select")  # noqa: F821
    purchase_orders: Mapped[list["PurchaseOrder"]] = relationship(back_populates="supplier", lazy="select")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} name={self.name} tier={self.tier_level}>"
