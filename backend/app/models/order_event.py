from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel
from app.models.enums import OrderEventType

if TYPE_CHECKING:
    from app.models.order import Order, OrderItem
    from app.models.staff import Staff


class OrderEvent(BaseModel):
    __tablename__ = "order_event"
    __table_args__ = (
        Index("ix_order_event_order_created", "order_id", "created_at"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_item_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("order_item.id", ondelete="CASCADE"),
        nullable=True,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("staff.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[OrderEventType] = mapped_column(
        Enum(OrderEventType, name="order_event_type"), nullable=False
    )
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="events")
    order_item: Mapped["OrderItem | None"] = relationship(back_populates="events")
    actor: Mapped["Staff | None"] = relationship(back_populates="actor_events")
