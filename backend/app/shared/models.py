from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


Money = Decimal
Customizations = dict[str, Any]


class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    PLACED = "PLACED"
    IN_KITCHEN = "IN_KITCHEN"
    READY = "READY"
    SERVED = "SERVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class OrderType(str, Enum):
    DINE_IN = "DINE_IN"
    TAKEAWAY = "TAKEAWAY"


class ItemStatus(str, Enum):
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    READY = "READY"
    SERVED = "SERVED"
    VOIDED = "VOIDED"


class EventType(str, Enum):
    PLACED = "PLACED"
    ROUTED = "ROUTED"
    STATUS_CHANGED = "STATUS_CHANGED"
    RECALLED = "RECALLED"
    CANCELLED = "CANCELLED"


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class MenuCategory(BaseModel):
    id: UUID
    name: str
    display_order: int = 0


class MenuCategoryCreate(BaseModel):
    name: str
    display_order: int = 0


class MenuCategoryUpdate(BaseModel):
    name: str | None = None
    display_order: int | None = None


class MenuItem(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    price: Money
    category_id: UUID
    station_id: UUID
    prep_time_min: int | None = None
    is_available: bool = True
    customization_schema: dict[str, Any] = Field(default_factory=dict)


class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: Money
    category_id: UUID
    station_id: UUID
    prep_time_min: int | None = None
    is_available: bool = True
    customization_schema: dict[str, Any] = Field(default_factory=dict)


class MenuItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Money | None = None
    category_id: UUID | None = None
    station_id: UUID | None = None
    prep_time_min: int | None = None
    customization_schema: dict[str, Any] | None = None


class Table(BaseModel):
    id: UUID
    number: int
    seats: int
    is_occupied: bool = False


class OrderItem(BaseModel):
    id: UUID
    order_id: UUID
    menu_item_id: UUID
    quantity: int
    unit_price: Money
    status: ItemStatus
    station_id: UUID
    customizations: Customizations = Field(default_factory=dict)
    allergy_notes: str | None = None
    started_at: datetime | None = None
    ready_at: datetime | None = None


class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: int
    customizations: Customizations = Field(default_factory=dict)
    allergy_notes: str | None = None


class OrderItemUpdate(BaseModel):
    quantity: int | None = None
    customizations: Customizations | None = None
    allergy_notes: str | None = None


class Order(BaseModel):
    id: UUID
    table_id: UUID
    customer_id: UUID | None = None
    type: OrderType
    status: OrderStatus
    subtotal: Money = Decimal("0.00")
    items: list[OrderItem] = Field(default_factory=list)
    created_at: datetime
    placed_at: datetime | None = None
    ready_at: datetime | None = None
    served_at: datetime | None = None


class OrderCreate(BaseModel):
    table_id: UUID
    customer_id: UUID | None = None
    type: OrderType


class Station(BaseModel):
    id: UUID
    name: str
    is_active: bool = True


class StationCreate(BaseModel):
    name: str
    is_active: bool = True


class KitchenTicket(BaseModel):
    order_id: UUID
    station_id: UUID
    table_number: int
    placed_at: datetime
    items: list[OrderItem]


class OrderEvent(BaseModel):
    id: UUID
    order_id: UUID
    order_item_id: UUID | None = None
    event_type: EventType
    actor_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class OrderCancelRequest(BaseModel):
    reason: str | None = None


class ItemAvailabilityUpdate(BaseModel):
    is_available: bool


class ItemStatusUpdate(BaseModel):
    new_status: ItemStatus
    reason: str | None = None


class RecallOrderRequest(BaseModel):
    reason: str | None = None


class WsEnvelope(BaseModel):
    type: str
    data: dict[str, Any] = Field(default_factory=dict)
    ts: datetime = Field(default_factory=utc_now)
