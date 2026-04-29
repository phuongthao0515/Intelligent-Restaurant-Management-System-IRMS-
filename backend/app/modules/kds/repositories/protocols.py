from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.shared.models import Station


class StationRepository(Protocol):
    async def list_stations(self) -> list[Station]: ...
    async def get_station(self, station_id: UUID) -> Station | None: ...
    async def save_station(self, station: Station) -> None: ...
