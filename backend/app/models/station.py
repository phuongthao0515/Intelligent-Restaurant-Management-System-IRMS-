from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem
    from app.models.order import OrderItem


class Station(BaseModel):
    __tablename__ = "station"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    menu_items: Mapped[list["MenuItem"]] = relationship(back_populates="station")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="station")
