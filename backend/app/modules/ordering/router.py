from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.deps import get_menu_service, get_order_service, get_table_service
from app.modules.ordering.services.menu_service import MenuService
from app.modules.ordering.services.order_service import OrderService
from app.modules.ordering.services.table_service import TableService
from app.shared.models import (
    ItemAvailabilityUpdate,
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
    Order,
    OrderCancelRequest,
    OrderCreate,
    OrderItem,
    OrderItemCreate,
    OrderItemUpdate,
    OrderStatus,
    Table,
)


router = APIRouter()


@router.get("/menu/categories", tags=["menu"], response_model=list[MenuCategory])
async def list_menu_categories(
    service: MenuService = Depends(get_menu_service),
) -> list[MenuCategory]:
    return await service.list_categories()


@router.post(
    "/menu/categories",
    tags=["menu"],
    status_code=status.HTTP_201_CREATED,
    response_model=MenuCategory,
)
async def create_menu_category(
    payload: MenuCategoryCreate,
    service: MenuService = Depends(get_menu_service),
) -> MenuCategory:
    return await service.create_category(payload)


@router.patch(
    "/menu/categories/{category_id}", tags=["menu"], response_model=MenuCategory
)
async def update_menu_category(
    category_id: UUID,
    payload: MenuCategoryUpdate,
    service: MenuService = Depends(get_menu_service),
) -> MenuCategory:
    return await service.update_category(category_id, payload)


@router.get("/menu/items", tags=["menu"], response_model=list[MenuItem])
async def list_menu_items(
    category_id: UUID | None = None,
    is_available: bool | None = None,
    service: MenuService = Depends(get_menu_service),
) -> list[MenuItem]:
    return await service.list_menu_items(category_id, is_available)


@router.post(
    "/menu/items",
    tags=["menu"],
    status_code=status.HTTP_201_CREATED,
    response_model=MenuItem,
)
async def create_menu_item(
    payload: MenuItemCreate,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.create_menu_item(payload)


@router.get("/menu/items/{item_id}", tags=["menu"], response_model=MenuItem)
async def get_menu_item(
    item_id: UUID,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.get_menu_item(item_id)


@router.patch("/menu/items/{item_id}", tags=["menu"], response_model=MenuItem)
async def update_menu_item(
    item_id: UUID,
    payload: MenuItemUpdate,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.update_menu_item(item_id, payload)


@router.patch(
    "/menu/items/{item_id}/availability", tags=["menu"], response_model=MenuItem
)
async def update_item_availability(
    item_id: UUID,
    payload: ItemAvailabilityUpdate,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.update_item_availability(item_id, payload)


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
