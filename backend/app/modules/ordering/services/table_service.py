from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.shared.models import Table
from app.shared.store import store


class TableService:
    """Actor: host — front-of-house staff who manages table
    seating and availability.
    """

    def list_tables(self) -> list[Table]:
        return list(store.tables.values())

    def get_table(self, table_id: UUID) -> Table:
        table = store.tables.get(table_id)
        if table is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Table not found")
        return table


table_service = TableService()
