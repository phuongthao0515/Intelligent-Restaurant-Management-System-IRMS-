from __future__ import annotations

from fastapi import APIRouter, status

from app.modules.kds.service import kds_service
from app.shared.models import (
    ItemStatusUpdate,
    Order,
    OrderEvent,
    OrderItem,
    RecallOrderRequest,
    Station,
    StationCreate,
    KitchenTicket,
)


router = APIRouter()


@router.get("/kds/stations", tags=["kds"], response_model=list[Station])
def list_stations() -> list[Station]:
    return kds_service.list_stations()


@router.post("/kds/stations", tags=["kds"], status_code=status.HTTP_201_CREATED, response_model=Station)
def create_station(payload: StationCreate) -> Station:
    return kds_service.create_station(payload)


@router.get("/kds/stations/{station_id}/tickets", tags=["kds"], response_model=list[KitchenTicket])
def list_station_tickets(station_id: int, status: str | None = "ACTIVE") -> list[KitchenTicket]:
    return kds_service.list_tickets(station_id, status)


@router.patch("/kds/order-items/{order_item_id}/status", tags=["kds"], response_model=OrderItem)
def update_order_item_status(order_item_id: int, payload: ItemStatusUpdate) -> OrderItem:
    return kds_service.update_order_item_status(order_item_id, payload)


@router.post("/kds/order-items/{order_item_id}/bump", tags=["kds"], response_model=OrderItem)
def bump_order_item(order_item_id: int) -> OrderItem:
    return kds_service.bump_order_item(order_item_id)


@router.post("/kds/orders/{order_id}/recall", tags=["kds"], response_model=Order)
def recall_order(order_id: int, payload: RecallOrderRequest | None = None) -> Order:
    return kds_service.recall_order(order_id, payload)


@router.get("/kds/events", tags=["kds"], response_model=list[OrderEvent])
def list_events(order_id: int | None = None, since: str | None = None) -> list[OrderEvent]:
    return kds_service.list_events(order_id, since)
