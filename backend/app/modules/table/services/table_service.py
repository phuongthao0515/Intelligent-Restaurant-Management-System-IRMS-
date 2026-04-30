from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.modules.ordering.repositories import OrderRepository
from app.modules.table.repositories import TableRepository
from app.shared.models import OrderStatus, Table


_ACTIVE_ORDER_STATUSES: frozenset[OrderStatus] = frozenset(
    {
        OrderStatus.DRAFT,
        OrderStatus.PLACED,
        OrderStatus.IN_KITCHEN,
        OrderStatus.READY,
        OrderStatus.SERVED,
    }
)


class TableService:
    def __init__(self, tables: TableRepository, orders: OrderRepository):
        self._tables = tables
        self._orders = orders

    async def list_tables(self) -> list[Table]:
        tables = await self._tables.list_tables()
        active = await self._orders.list_active_table_ids(_ACTIVE_ORDER_STATUSES)
        return [
            table.model_copy(update={"is_occupied": table.id in active})
            for table in tables
        ]

    async def get_table(self, table_id: UUID) -> Table:
        table = await self._tables.get_table(table_id)
        if table is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Table not found")
        active = await self._orders.list_active_table_ids(_ACTIVE_ORDER_STATUSES)
        return table.model_copy(update={"is_occupied": table.id in active})
