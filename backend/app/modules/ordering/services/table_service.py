from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.modules.ordering.repositories import (
    InMemoryTableRepository,
    TableRepository,
)
from app.shared.models import Table


class TableService:
    """Actor: host — front-of-house staff who manages table
    seating and availability.
    """

    def __init__(self, tables: TableRepository):
        self._tables = tables

    def list_tables(self) -> list[Table]:
        return self._tables.list_tables()

    def get_table(self, table_id: UUID) -> Table:
        table = self._tables.get_table(table_id)
        if table is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Table not found")
        return table


table_service = TableService(InMemoryTableRepository())
