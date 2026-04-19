from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel

if TYPE_CHECKING:
    from app.models.order import OrderItem


class MenuItem(BaseModel):
    __tablename__ = "menu_item"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_menu_item_price_nonnegative"),
        CheckConstraint("prep_time_min >= 0", name="ck_menu_item_prep_time_nonnegative"),
        Index("ix_menu_item_category_available", "category", "is_available"),
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_combo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    station: Mapped[str] = mapped_column(String(50), nullable=False)
    prep_time_min: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="menu_item")
