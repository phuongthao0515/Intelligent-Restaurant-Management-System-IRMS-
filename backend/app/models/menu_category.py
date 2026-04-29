from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel

if TYPE_CHECKING:
    from app.models.menu_item import MenuItem


class MenuCategory(BaseModel):
    __tablename__ = "menu_category"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    menu_items: Mapped[list["MenuItem"]] = relationship(back_populates="category")
