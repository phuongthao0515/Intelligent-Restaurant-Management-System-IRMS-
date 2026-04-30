from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from app.shared.models import EventType, Order, OrderEvent, OrderStatus


class OrderRepository(Protocol):
    async def list_orders(self) -> list[Order]: ...
    async def get_order(self, order_id: UUID) -> Order | None: ...
    async def save_order(self, order: Order) -> None: ...
    async def list_active_table_ids(
        self, active_statuses: Iterable[OrderStatus]
    ) -> set[UUID]: ...
    async def add_event(
        self,
        order_id: UUID,
        event_type: EventType,
        order_item_id: UUID | None = None,
        payload: dict | None = None,
    ) -> OrderEvent: ...
    async def list_events(
        self, order_id: UUID | None = None, since: str | None = None
    ) -> list[OrderEvent]: ...
