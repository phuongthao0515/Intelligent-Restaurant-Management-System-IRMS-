from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.modules.ordering.service import ordering_service
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
def list_menu_categories() -> list[MenuCategory]:
    return ordering_service.list_categories()


@router.post(
    "/menu/categories",
    tags=["menu"],
    status_code=status.HTTP_201_CREATED,
    response_model=MenuCategory,
)
def create_menu_category(payload: MenuCategoryCreate) -> MenuCategory:
    return ordering_service.create_category(payload)


@router.patch("/menu/categories/{category_id}", tags=["menu"], response_model=MenuCategory)
def update_menu_category(category_id: int, payload: MenuCategoryUpdate) -> MenuCategory:
    return ordering_service.update_category(category_id, payload)


@router.get("/menu/items", tags=["menu"], response_model=list[MenuItem])
def list_menu_items(
    category_id: int | None = None,
    is_available: bool | None = None,
) -> list[MenuItem]:
    return ordering_service.list_menu_items(category_id, is_available)


@router.post("/menu/items", tags=["menu"], status_code=status.HTTP_201_CREATED, response_model=MenuItem)
def create_menu_item(payload: MenuItemCreate) -> MenuItem:
    return ordering_service.create_menu_item(payload)


@router.get("/menu/items/{item_id}", tags=["menu"], response_model=MenuItem)
def get_menu_item(item_id: int) -> MenuItem:
    return ordering_service.get_menu_item(item_id)


@router.patch("/menu/items/{item_id}", tags=["menu"], response_model=MenuItem)
def update_menu_item(item_id: int, payload: MenuItemUpdate) -> MenuItem:
    return ordering_service.update_menu_item(item_id, payload)


@router.patch("/menu/items/{item_id}/availability", tags=["menu"], response_model=MenuItem)
def update_item_availability(item_id: int, payload: ItemAvailabilityUpdate) -> MenuItem:
    return ordering_service.update_item_availability(item_id, payload)


@router.get("/tables", tags=["tables"], response_model=list[Table])
def list_tables() -> list[Table]:
    return ordering_service.list_tables()


@router.get("/tables/{table_id}", tags=["tables"], response_model=Table)
def get_table(table_id: int) -> Table:
    return ordering_service.get_table(table_id)


@router.get("/orders", tags=["orders"], response_model=list[Order])
def list_orders(table_id: int | None = None, status: OrderStatus | None = None) -> list[Order]:
    return ordering_service.list_orders(table_id, status)


@router.post("/orders", tags=["orders"], status_code=status.HTTP_201_CREATED, response_model=Order)
def create_order(payload: OrderCreate) -> Order:
    return ordering_service.create_order(payload)


@router.get("/orders/{order_id}", tags=["orders"], response_model=Order)
def get_order(order_id: int) -> Order:
    return ordering_service.get_order(order_id)


@router.post(
    "/orders/{order_id}/items",
    tags=["orders"],
    status_code=status.HTTP_201_CREATED,
    response_model=OrderItem,
)
def add_order_item(order_id: int, payload: OrderItemCreate) -> OrderItem:
    return ordering_service.add_order_item(order_id, payload)


@router.patch("/orders/{order_id}/items/{item_id}", tags=["orders"], response_model=OrderItem)
def update_order_item(order_id: int, item_id: int, payload: OrderItemUpdate) -> OrderItem:
    return ordering_service.update_order_item(order_id, item_id, payload)


@router.delete("/orders/{order_id}/items/{item_id}", tags=["orders"], status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_id: int, item_id: int) -> Response:
    ordering_service.remove_order_item(order_id, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/orders/{order_id}/submit", tags=["orders"], response_model=Order)
def submit_order(order_id: int) -> Order:
    return ordering_service.submit_order(order_id)


@router.post("/orders/{order_id}/cancel", tags=["orders"], response_model=Order)
def cancel_order(order_id: int, payload: OrderCancelRequest | None = None) -> Order:
    reason = payload.reason if payload else None
    return ordering_service.cancel_order(order_id, reason)


@router.post("/orders/{order_id}/close", tags=["orders"], response_model=Order)
def close_order(order_id: int) -> Order:
    return ordering_service.close_order(order_id)
