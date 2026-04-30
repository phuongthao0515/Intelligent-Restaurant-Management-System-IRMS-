from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.shared.models import Table


class TableRepository(Protocol):
    async def list_tables(self) -> list[Table]: ...
    async def get_table(self, table_id: UUID) -> Table | None: ...
