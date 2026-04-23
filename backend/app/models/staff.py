from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel
from app.models.enums import StaffRole

if TYPE_CHECKING:
    from app.models.order import Order, OrderItem
    from app.models.order_event import OrderEvent
    from app.models.payment import Payment


class Staff(BaseModel):
    __tablename__ = "staff"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole, name="staff_role"), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    served_orders: Mapped[list["Order"]] = relationship(back_populates="server")
    assigned_items: Mapped[list["OrderItem"]] = relationship(back_populates="assigned_chef")
    cashier_payments: Mapped[list["Payment"]] = relationship(back_populates="cashier")
    actor_events: Mapped[list["OrderEvent"]] = relationship(back_populates="actor")
