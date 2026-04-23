from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel
from app.models.enums import ReservationStatus

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.restaurant_table import RestaurantTable


class Reservation(BaseModel):
    __tablename__ = "reservation"
    __table_args__ = (
        CheckConstraint("party_size > 0", name="ck_reservation_party_size_positive"),
        Index("ix_reservation_table_reserved", "table_id", "reserved_at"),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("restaurant_table.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status"),
        nullable=False,
        default=ReservationStatus.PENDING,
    )
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped["Customer"] = relationship(back_populates="reservations")
    table: Mapped["RestaurantTable"] = relationship(back_populates="reservations")
