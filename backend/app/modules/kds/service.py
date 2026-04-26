from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.kds.repositories import StationRepository
from app.modules.ordering.repositories import OrderRepository, TableRepository
from app.shared.models import (
    EventType,
    ItemStatus,
    ItemStatusUpdate,
    KitchenTicket,
    Order,
    OrderEvent,
    OrderItem,
    OrderStatus,
    RecallOrderRequest,
    Station,
    StationCreate,
    utc_now,
)


class KdsService:
    def __init__(
        self,
        stations: StationRepository,
        orders: OrderRepository,
        tables: TableRepository,
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
            table = await self._tables.get_table(order.table_id)
            tickets.append(
                KitchenTicket(
                    order_id=order.id,
                    station_id=station_id,
                    table_number=table.number if table else 0,
                    placed_at=order.placed_at,
                    items=items,
                )
            )
        return tickets

    async def update_order_item_status(
        self, order_item_id: UUID, payload: ItemStatusUpdate
    ) -> OrderItem:
        orders = await self._orders.list_orders()
        for order in orders:
            for index, item in enumerate(order.items):
                if item.id != order_item_id:
                    continue
                changed_at = utc_now()
                updated_item = item.model_copy(update={"status": payload.new_status})
                if payload.new_status == ItemStatus.PREPARING:
                    updated_item = updated_item.model_copy(
                        update={"started_at": changed_at}
                    )
                if payload.new_status == ItemStatus.READY:
                    updated_item = updated_item.model_copy(
                        update={"ready_at": changed_at}
                    )
                items = list(order.items)
                items[index] = updated_item
                updated_order = order.model_copy(update={"items": items})

                auto_promoted = False
                if all(current.status == ItemStatus.READY for current in items):
                    updated_order = updated_order.model_copy(
                        update={"status": OrderStatus.READY, "ready_at": changed_at}
                    )
                    auto_promoted = True
                elif (
                    order.status in {OrderStatus.PLACED, OrderStatus.IN_KITCHEN}
                    and any(
                        current.status in {ItemStatus.QUEUED, ItemStatus.PREPARING}
                        for current in items
                    )
                ):
                    updated_order = updated_order.model_copy(
                        update={"status": OrderStatus.IN_KITCHEN}
                    )

                await self._orders.save_order(updated_order)
                await self._orders.add_event(
                    updated_order.id,
                    EventType.STATUS_CHANGED,
                    order_item_id=order_item_id,
                    payload={
                        "new_status": payload.new_status.value,
                        "reason": payload.reason,
                    },
                )
                if auto_promoted:
                    await self._orders.add_event(
                        updated_order.id,
                        EventType.STATUS_CHANGED,
                        payload={
                            "new_status": OrderStatus.READY.value,
                            "auto_promoted": True,
                        },
                    )
                return updated_item

        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order item not found")

    async def bump_order_item(self, order_item_id: UUID) -> OrderItem:
        return await self.update_order_item_status(
            order_item_id, ItemStatusUpdate(new_status=ItemStatus.READY)
        )

    async def recall_order(
        self, order_id: UUID, payload: RecallOrderRequest | None = None
    ) -> Order:
        order = await self._orders.get_order(order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")

        reset_items = [
            item.model_copy(
                update={
                    "status": ItemStatus.QUEUED,
                    "started_at": None,
                    "ready_at": None,
                }
            )
            for item in order.items
        ]
        updated = order.model_copy(
            update={
                "status": OrderStatus.IN_KITCHEN,
                "ready_at": None,
                "items": reset_items,
            }
        )
        await self._orders.save_order(updated)
        await self._orders.add_event(
            order_id,
            EventType.RECALLED,
            payload={"reason": payload.reason if payload else None},
        )
        return updated

    async def list_events(
        self, order_id: UUID | None = None, since: str | None = None
    ) -> list[OrderEvent]:
        return await self._orders.list_events(order_id=order_id, since=since)
