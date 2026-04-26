from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.shared.models import (
    EventType,
    MenuCategory,
    MenuItem,
    Order,
    OrderEvent,
    Table,
)


class TableRepository(Protocol):
    async def list_tables(self) -> list[Table]: ...
    async def get_table(self, table_id: UUID) -> Table | None: ...


class MenuRepository(Protocol):
    async def list_categories(self) -> list[MenuCategory]: ...
    async def get_category(self, category_id: UUID) -> MenuCategory | None: ...
    async def save_category(self, category: MenuCategory) -> None: ...

    async def list_items(self) -> list[MenuItem]: ...
    async def get_item(self, item_id: UUID) -> MenuItem | None: ...
    async def save_item(self, item: MenuItem) -> None: ...


class OrderRepository(Protocol):
    async def list_orders(self) -> list[Order]: ...
    async def get_order(self, order_id: UUID) -> Order | None: ...
    async def save_order(self, order: Order) -> None: ...
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
