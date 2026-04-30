from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel
from app.models.enums import PaymentMethod
from app.shared.models import now_ict

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.staff import Staff


class Payment(BaseModel):
    __tablename__ = "payment"

    order_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cashier_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    service_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0")
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0")
    )
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tip: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0")
    )
    method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method"), nullable=False
    )
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=now_ict,
        nullable=False,
    )

    order: Mapped["Order"] = relationship(back_populates="payments")
    cashier: Mapped["Staff"] = relationship(back_populates="cashier_payments")
