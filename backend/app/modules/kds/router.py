from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.deps import get_kds_service
from app.modules.kds.service import KdsService
from app.shared.models import (
    ItemStatusUpdate,
    KitchenTicket,
    Order,
    OrderEvent,
    OrderItem,
    RecallOrderRequest,
    Station,
    StationCreate,
)


router = APIRouter()


@router.get("/kds/stations", tags=["kds"], response_model=list[Station])
async def list_stations(
    service: KdsService = Depends(get_kds_service),
) -> list[Station]:
    return await service.list_stations()


@router.post(
    "/kds/stations",
    tags=["kds"],
    status_code=status.HTTP_201_CREATED,
    response_model=Station,
)
async def create_station(
    payload: StationCreate,
    service: KdsService = Depends(get_kds_service),
) -> Station:
    return await service.create_station(payload)


@router.get(
    "/kds/stations/{station_id}/tickets",
    tags=["kds"],
    response_model=list[KitchenTicket],
)
async def list_station_tickets(
    station_id: UUID,
    status: str | None = "ACTIVE",
    service: KdsService = Depends(get_kds_service),
) -> list[KitchenTicket]:
    return await service.list_tickets(station_id, status)


@router.patch(
    "/kds/order-items/{order_item_id}/status",
    tags=["kds"],
    response_model=OrderItem,
)
async def update_order_item_status(
    order_item_id: UUID,
    payload: ItemStatusUpdate,
    service: KdsService = Depends(get_kds_service),
) -> OrderItem:
    return await service.update_order_item_status(order_item_id, payload)


@router.post(
    "/kds/order-items/{order_item_id}/bump",
    tags=["kds"],
    response_model=OrderItem,
)
async def bump_order_item(
    order_item_id: UUID,
    service: KdsService = Depends(get_kds_service),
) -> OrderItem:
    return await service.bump_order_item(order_item_id)


@router.post("/kds/orders/{order_id}/recall", tags=["kds"], response_model=Order)
async def recall_order(
    order_id: UUID,
    payload: RecallOrderRequest | None = None,
    service: KdsService = Depends(get_kds_service),
) -> Order:
    return await service.recall_order(order_id, payload)


@router.get("/kds/events", tags=["kds"], response_model=list[OrderEvent])
async def list_events(
    order_id: UUID | None = None,
    since: str | None = None,
    service: KdsService = Depends(get_kds_service),
) -> list[OrderEvent]:
    return await service.list_events(order_id, since)
