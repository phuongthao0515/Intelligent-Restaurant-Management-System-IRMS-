from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import TableStatus
from app.models.restaurant_table import RestaurantTable as RestaurantTableORM
from app.shared.models import Table


def _table_to_dto(orm: RestaurantTableORM) -> Table:
    return Table(
        id=orm.id,
        number=orm.number,
        seats=orm.seats,
        is_occupied=(orm.status == TableStatus.OCCUPIED),
    )


class SqlAlchemyTableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_tables(self) -> list[Table]:
        result = await self._session.execute(select(RestaurantTableORM))
        return [_table_to_dto(t) for t in result.scalars().all()]

    async def get_table(self, table_id: UUID) -> Table | None:
        result = await self._session.execute(
            select(RestaurantTableORM).where(RestaurantTableORM.id == table_id)
        )
        orm = result.scalar_one_or_none()
        return _table_to_dto(orm) if orm else None
