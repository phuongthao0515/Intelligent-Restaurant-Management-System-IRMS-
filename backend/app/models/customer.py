from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseModel

if TYPE_CHECKING:
    from app.models.reservation import Reservation


class Customer(BaseModel):
    __tablename__ = "customer"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="customer")
