from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.shared.models import (
    EventType,
    ItemStatus,
    Order,
    OrderCreate,
    OrderItem,
    OrderItemCreate,
    OrderItemUpdate,
    OrderStatus,
    utc_now,
)
from app.shared.store import store


class OrderService:
    """Actor: server — front-of-house staff (waiter) who takes
    and manages customer orders.
    """

    def list_orders(
        self,
        table_id: UUID | None = None,
        status_filter: OrderStatus | None = None,
    ) -> list[Order]:
        orders = list(store.orders.values())
        if table_id is not None:
            orders = [order for order in orders if order.table_id == table_id]
        if status_filter is not None:
            orders = [order for order in orders if order.status == status_filter]
        return orders

    def create_order(self, payload: OrderCreate) -> Order:
        if payload.table_id not in store.tables:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Table not found")
        order = Order(
            id=uuid.uuid4(),
            table_id=payload.table_id,
            customer_id=payload.customer_id,
            type=payload.type,
            status=OrderStatus.DRAFT,
            created_at=utc_now(),
        )
        store.orders[order.id] = order
        return order

    def get_order(self, order_id: UUID) -> Order:
        order = store.orders.get(order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
        return order

    def add_order_item(self, order_id: UUID, payload: OrderItemCreate) -> OrderItem:
        order = self.get_order(order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only draft orders are editable"
            )

        menu_item = store.menu_items.get(payload.menu_item_id)
        if menu_item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Menu item not found")
        if not menu_item.is_available:
            raise HTTPException(status.HTTP_409_CONFLICT, "Menu item is unavailable")

        item = OrderItem(
            id=uuid.uuid4(),
            order_id=order_id,
            menu_item_id=menu_item.id,
            quantity=payload.quantity,
            unit_price=menu_item.price,
            status=ItemStatus.QUEUED,
            station_id=menu_item.station_id,
            customizations=payload.customizations,
            allergy_notes=payload.allergy_notes,
        )
        updated_order = order.model_copy(
            update={
                "items": [*order.items, item],
                "subtotal": order.subtotal + (menu_item.price * payload.quantity),
            }
        )
        store.orders[order_id] = updated_order
        return item

    def update_order_item(
        self, order_id: UUID, item_id: UUID, payload: OrderItemUpdate
    ) -> OrderItem:
        order = self.get_order(order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only draft orders are editable"
            )

        for index, item in enumerate(order.items):
            if item.id == item_id:
                updated_item = item.model_copy(
                    update=payload.model_dump(exclude_none=True)
                )
                items = list(order.items)
                items[index] = updated_item
                subtotal = sum(
                    (current.unit_price * current.quantity for current in items),
                    start=Decimal("0.00"),
                )
                store.orders[order_id] = order.model_copy(
                    update={"items": items, "subtotal": subtotal}
                )
                return updated_item
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order item not found")

    def remove_order_item(self, order_id: UUID, item_id: UUID) -> None:
        order = self.get_order(order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only draft orders are editable"
            )

        items = [item for item in order.items if item.id != item_id]
        if len(items) == len(order.items):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order item not found")

        subtotal = sum(
            (item.unit_price * item.quantity for item in items),
            start=Decimal("0.00"),
        )
        store.orders[order_id] = order.model_copy(
            update={"items": items, "subtotal": subtotal}
        )

    def submit_order(self, order_id: UUID) -> Order:
        order = self.get_order(order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only draft orders can be submitted"
            )
        updated = order.model_copy(
            update={"status": OrderStatus.PLACED, "placed_at": utc_now()}
        )
        store.orders[order_id] = updated
        store.add_event(
            order_id, EventType.PLACED, payload={"status": updated.status.value}
        )
        return updated

    def cancel_order(self, order_id: UUID, reason: str | None = None) -> Order:
        order = self.get_order(order_id)
        if order.status in {OrderStatus.CLOSED, OrderStatus.CANCELLED}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Order already finished")
        updated = order.model_copy(update={"status": OrderStatus.CANCELLED})
        store.orders[order_id] = updated
        store.add_event(order_id, EventType.CANCELLED, payload={"reason": reason})
        return updated

    def close_order(self, order_id: UUID) -> Order:
        order = self.get_order(order_id)
        if order.status not in {OrderStatus.SERVED, OrderStatus.READY}:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Only ready or served orders can be closed in this skeleton",
            )
        updated = order.model_copy(update={"status": OrderStatus.CLOSED})
        store.orders[order_id] = updated
        return updated


order_service = OrderService()
