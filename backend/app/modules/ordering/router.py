from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import get_order_service
from app.modules.ordering.services.order_service import OrderService
from app.shared.models import (
    Order,
    OrderCancelRequest,
    OrderCreate,
    OrderItem,
    OrderItemCreate,
    OrderItemUpdate,
    OrderStatus,
)


router = APIRouter()


@router.get("/orders", tags=["orders"], response_model=list[Order])
async def list_orders(
    table_id: UUID | None = None,
    status: OrderStatus | None = None,
    service: OrderService = Depends(get_order_service),
) -> list[Order]:
    return await service.list_orders(table_id, status)


@router.post(
    "/orders",
    tags=["orders"],
    status_code=status.HTTP_201_CREATED,
    response_model=Order,
)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> Order:
    return await service.create_order(payload)


@router.get("/orders/{order_id}", tags=["orders"], response_model=Order)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> Order:
    return await service.get_order(order_id)


@router.post(
    "/orders/{order_id}/items",
    tags=["orders"],
    status_code=status.HTTP_201_CREATED,
    response_model=OrderItem,
)
async def add_order_item(
    order_id: UUID,
    payload: OrderItemCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderItem:
    return await service.add_order_item(order_id, payload)


@router.patch(
    "/orders/{order_id}/items/{item_id}", tags=["orders"], response_model=OrderItem
)
async def update_order_item(
    order_id: UUID,
    item_id: UUID,
    payload: OrderItemUpdate,
    service: OrderService = Depends(get_order_service),
) -> OrderItem:
    return await service.update_order_item(order_id, item_id, payload)


@router.delete(
    "/orders/{order_id}/items/{item_id}",
    tags=["orders"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order_item(
    order_id: UUID,
    item_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> Response:
    await service.remove_order_item(order_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/orders/{order_id}/submit", tags=["orders"], response_model=Order)
async def submit_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> Order:
    return await service.submit_order(order_id)


@router.post("/orders/{order_id}/cancel", tags=["orders"], response_model=Order)
async def cancel_order(
    order_id: UUID,
    payload: OrderCancelRequest | None = None,
    service: OrderService = Depends(get_order_service),
) -> Order:
    reason = payload.reason if payload else None
    return await service.cancel_order(order_id, reason)


@router.post("/orders/{order_id}/serve", tags=["orders"], response_model=Order)
async def serve_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> Order:
    return await service.serve_order(order_id)


@router.post("/orders/{order_id}/close", tags=["orders"], response_model=Order)
async def close_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> Order:
    return await service.close_order(order_id)
