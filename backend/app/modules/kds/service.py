from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.kds.repositories import StationRepository
from app.modules.ordering.services.order_service import OrderService
from app.modules.table.services.table_service import TableService
from app.shared.models import (
    ItemStatus,
    ItemStatusUpdate,
    KitchenTicket,
    Order,
    OrderEvent,
    OrderItem,
    RecallOrderRequest,
    Station,
    StationCreate,
)


class KdsService:
    def __init__(
        self,
        stations: StationRepository,
        orders: OrderService,
        tables: TableService,
    ):
        self._stations = stations
        self._orders = orders
        self._tables = tables

    async def list_stations(self) -> list[Station]:
        return await self._stations.list_stations()

    async def create_station(self, payload: StationCreate) -> Station:
        station = Station(id=uuid.uuid4(), **payload.model_dump())
        await self._stations.save_station(station)
        return station

    async def list_tickets(
        self, station_id: UUID, status_filter: str | None = None
    ) -> list[KitchenTicket]:
        if await self._stations.get_station(station_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Station not found")

        orders = await self._orders.list_orders()
        tickets: list[KitchenTicket] = []
        for order in orders:
            if order.placed_at is None:
                continue
            items = [item for item in order.items if item.station_id == station_id]
            if status_filter == "ACTIVE":
                items = [
                    item for item in items
                    if item.status in {ItemStatus.QUEUED, ItemStatus.PREPARING}
                ]
            elif status_filter:
                items = [item for item in items if item.status.value == status_filter]
            if not items:
                continue
            try:
                table = await self._tables.get_table(order.table_id)
                table_number = table.number
            except HTTPException:
                table_number = 0
            tickets.append(
                KitchenTicket(
                    order_id=order.id,
                    station_id=station_id,
                    table_number=table_number,
                    placed_at=order.placed_at,
                    items=items,
                )
            )
        return tickets

    async def update_order_item_status(
        self, order_item_id: UUID, payload: ItemStatusUpdate
    ) -> OrderItem:
        updated_item = await self._orders.update_item_status(
            order_item_id, payload.new_status, payload.reason
        )

        if payload.new_status == ItemStatus.READY:
            order = await self._orders.get_order(updated_item.order_id)
            if order.items and all(
                item.status == ItemStatus.READY for item in order.items
            ):
                await self._orders.transition_order_to_ready(order.id)

        return updated_item

    async def bump_order_item(self, order_item_id: UUID) -> OrderItem:
        return await self.update_order_item_status(
            order_item_id, ItemStatusUpdate(new_status=ItemStatus.READY)
        )

    async def recall_order(
        self, order_id: UUID, payload: RecallOrderRequest | None = None
    ) -> Order:
        return await self._orders.recall_order(
            order_id, payload.reason if payload else None
        )

    async def list_events(
        self, order_id: UUID | None = None, since: str | None = None
    ) -> list[OrderEvent]:
        return await self._orders.list_events(order_id=order_id, since=since)
