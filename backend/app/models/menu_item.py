from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel

if TYPE_CHECKING:
    from app.models.menu_category import MenuCategory
    from app.models.order import OrderItem
    from app.models.station import Station


class MenuItem(BaseModel):
    __tablename__ = "menu_item"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_menu_item_price_nonnegative"),
        CheckConstraint("prep_time_min >= 0", name="ck_menu_item_prep_time_nonnegative"),
        Index("ix_menu_item_category_available", "category_id", "is_available"),
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("menu_category.id", ondelete="RESTRICT"),
        nullable=False,
    )
    station_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("station.id", ondelete="RESTRICT"),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_combo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prep_time_min: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    customization_schema: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    category: Mapped["MenuCategory"] = relationship(back_populates="menu_items")
    station: Mapped["Station"] = relationship(back_populates="menu_items")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="menu_item")
