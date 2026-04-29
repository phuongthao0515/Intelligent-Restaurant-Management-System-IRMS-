from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.station import Station as StationORM
from app.shared.models import Station


def _station_to_dto(orm: StationORM) -> Station:
    return Station(
        id=orm.id,
        name=orm.name,
        is_active=orm.is_active,
    )


class SqlAlchemyStationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_stations(self) -> list[Station]:
        result = await self._session.execute(select(StationORM))
        return [_station_to_dto(s) for s in result.scalars().all()]

    async def get_station(self, station_id: UUID) -> Station | None:
        result = await self._session.execute(
            select(StationORM).where(StationORM.id == station_id)
        )
        orm = result.scalar_one_or_none()
        return _station_to_dto(orm) if orm else None

    async def save_station(self, station: Station) -> None:
        result = await self._session.execute(
            select(StationORM).where(StationORM.id == station.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            orm = StationORM(
                id=station.id,
                name=station.name,
                is_active=station.is_active,
            )
            self._session.add(orm)
        else:
            orm.name = station.name
            orm.is_active = station.is_active
        await self._session.flush()
