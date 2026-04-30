from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.deps import get_table_service
from app.modules.table.services.table_service import TableService
from app.shared.models import Table


router = APIRouter()


@router.get("/tables", tags=["tables"], response_model=list[Table])
async def list_tables(
    service: TableService = Depends(get_table_service),
) -> list[Table]:
    return await service.list_tables()


@router.get("/tables/{table_id}", tags=["tables"], response_model=Table)
async def get_table(
    table_id: UUID,
    service: TableService = Depends(get_table_service),
) -> Table:
    return await service.get_table(table_id)
