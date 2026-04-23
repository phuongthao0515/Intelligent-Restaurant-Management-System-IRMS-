from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel
from app.models.enums import OrderItemStatus, OrderPriority, OrderStatus

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem
    from app.models.order_event import OrderEvent
    from app.models.payment import Payment
    from app.models.restaurant_table import RestaurantTable
    from app.models.staff import Staff


class Order(BaseModel):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_status_created", "status", "created_at"),
    )

    server_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("restaurant_table.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.DRAFT,
    )
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[OrderPriority] = mapped_column(
        Enum(OrderPriority, name="order_priority"),
        nullable=False,
        default=OrderPriority.NORMAL,
    )

    server: Mapped["Staff"] = relationship(back_populates="served_orders")
    table: Mapped["RestaurantTable"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="order")
    events: Mapped[list["OrderEvent"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(BaseModel):
    __tablename__ = "order_item"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_item_unit_price_nonnegative"),
        Index("ix_order_item_status_station", "status", "station"),
        Index("ix_order_item_order", "order_id"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    menu_item_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("menu_item.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_chef_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="SET NULL"),
        nullable=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderItemStatus] = mapped_column(
        Enum(OrderItemStatus, name="order_item_status"),
        nullable=False,
        default=OrderItemStatus.QUEUED,
    )
    station: Mapped[str] = mapped_column(String(50), nullable=False)
    notes_allergy: Mapped[str | None] = mapped_column(Text, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship(back_populates="order_items")
    assigned_chef: Mapped["Staff | None"] = relationship(back_populates="assigned_items")
    events: Mapped[list["OrderEvent"]] = relationship(back_populates="order_item")
