from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status

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
from app.shared.store import store


class KdsService:
    def list_stations(self) -> list[Station]:
        return list(store.stations.values())

    def create_station(self, payload: StationCreate) -> Station:
        station = Station(id=uuid.uuid4(), **payload.model_dump())
        store.stations[station.id] = station
        return station

    def list_tickets(self, station_id: UUID, status_filter: str | None = None) -> list[KitchenTicket]:
        if station_id not in store.stations:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Station not found")

        tickets: list[KitchenTicket] = []
        for order in store.orders.values():
            if order.placed_at is None:
                continue
            items = [item for item in order.items if item.station_id == station_id]
            if status_filter == "ACTIVE":
                items = [
                    item for item in items if item.status in {ItemStatus.QUEUED, ItemStatus.PREPARING}
                ]
            elif status_filter:
                items = [item for item in items if item.status.value == status_filter]
            if not items:
                continue
            table = store.tables.get(order.table_id)
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

    def update_order_item_status(
        self, order_item_id: UUID, payload: ItemStatusUpdate
    ) -> OrderItem:
        for order_id, order in store.orders.items():
            for index, item in enumerate(order.items):
                if item.id != order_item_id:
                    continue
                updated_item = item.model_copy(update={"status": payload.new_status})
                if payload.new_status == ItemStatus.PREPARING:
                    updated_item.started_at = utc_now()
                if payload.new_status == ItemStatus.READY:
                    updated_item.ready_at = utc_now()
                items = list(order.items)
                items[index] = updated_item
                updated_order = order.model_copy(update={"items": items})
                if all(current.status == ItemStatus.READY for current in items):
                    updated_order = updated_order.model_copy(
                        update={"status": OrderStatus.READY, "ready_at": utc_now()}
                    )
                elif any(current.status in {ItemStatus.QUEUED, ItemStatus.PREPARING} for current in items):
                    updated_order = updated_order.model_copy(update={"status": OrderStatus.IN_KITCHEN})
                store.orders[order_id] = updated_order
                store.add_event(
                    order_id,
                    EventType.STATUS_CHANGED,
                    order_item_id=order_item_id,
                    payload={"new_status": payload.new_status.value, "reason": payload.reason},
                )
                return updated_item
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order item not found")

    def bump_order_item(self, order_item_id: UUID) -> OrderItem:
        return self.update_order_item_status(
            order_item_id, ItemStatusUpdate(new_status=ItemStatus.READY)
        )

    def recall_order(self, order_id: UUID, payload: RecallOrderRequest | None = None) -> Order:
        order = store.orders.get(order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
        updated = order.model_copy(update={"status": OrderStatus.IN_KITCHEN, "ready_at": None})
        store.orders[order_id] = updated
        store.add_event(
            order_id,
            EventType.RECALLED,
            payload={"reason": payload.reason if payload else None},
        )
        return updated

    def list_events(self, order_id: UUID | None = None, since: str | None = None) -> list[OrderEvent]:
        events = list(store.events.values())
        if order_id is not None:
            events = [event for event in events if event.order_id == order_id]
        if since is not None:
            events = [event for event in events if event.created_at.isoformat() >= since]
        return events


kds_service = KdsService()
