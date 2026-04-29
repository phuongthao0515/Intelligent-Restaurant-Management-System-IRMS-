from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel
from app.models.enums import TableStatus

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.reservation import Reservation


class RestaurantTable(BaseModel):
    __tablename__ = "restaurant_table"
    __table_args__ = (
        CheckConstraint("seats > 0", name="ck_restaurant_table_seats_positive"),
    )

    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[TableStatus] = mapped_column(
        Enum(TableStatus, name="table_status"),
        nullable=False,
        default=TableStatus.AVAILABLE,
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="table")
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="table")
