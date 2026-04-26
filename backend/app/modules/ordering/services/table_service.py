from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.modules.ordering.repositories import TableRepository
from app.shared.models import Table


class TableService:
    def __init__(self, tables: TableRepository):
        self._tables = tables

    async def list_tables(self) -> list[Table]:
        return await self._tables.list_tables()

    async def get_table(self, table_id: UUID) -> Table:
        table = await self._tables.get_table(table_id)
        if table is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Table not found")
        return table
