from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.ordering.repositories import (
    MenuRepository,
    OrderRepository,
    TableRepository,
)
from app.shared.domain_events import ORDER_CANCELLED, ORDER_PLACED, ORDER_SERVED
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


class OrderService:
    def __init__(
        self,
        orders: OrderRepository,
        menus: MenuRepository,
        tables: TableRepository,
    ):
        self._orders = orders
        self._menus = menus
        self._tables = tables

    async def list_orders(
        self,
        table_id: UUID | None = None,
        status_filter: OrderStatus | None = None,
    ) -> list[Order]:
        orders = await self._orders.list_orders()
        if table_id is not None:
            orders = [order for order in orders if order.table_id == table_id]
        if status_filter is not None:
            orders = [order for order in orders if order.status == status_filter]
        return orders

    async def create_order(self, payload: OrderCreate) -> Order:
        if await self._tables.get_table(payload.table_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Table not found")
        order = Order(
            id=uuid.uuid4(),
            table_id=payload.table_id,
            customer_id=payload.customer_id,
            status=OrderStatus.DRAFT,
            created_at=utc_now(),
        )
        await self._orders.save_order(order)
        return order

    async def get_order(self, order_id: UUID) -> Order:
        order = await self._orders.get_order(order_id)
        if order is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
        return order

    async def add_order_item(self, order_id: UUID, payload: OrderItemCreate) -> OrderItem:
        order = await self.get_order(order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only draft orders are editable"
            )

        menu_item = await self._menus.get_item(payload.menu_item_id)
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
        await self._orders.save_order(updated_order)
        return item

    async def update_order_item(
        self, order_id: UUID, item_id: UUID, payload: OrderItemUpdate
    ) -> OrderItem:
        order = await self.get_order(order_id)
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
                await self._orders.save_order(
                    order.model_copy(update={"items": items, "subtotal": subtotal})
                )
                return updated_item
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order item not found")

    async def remove_order_item(self, order_id: UUID, item_id: UUID) -> None:
        order = await self.get_order(order_id)
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
        await self._orders.save_order(
            order.model_copy(update={"items": items, "subtotal": subtotal})
        )

    async def submit_order(self, order_id: UUID) -> Order:
        order = await self.get_order(order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only draft orders can be submitted"
            )
        updated = order.model_copy(
            update={"status": OrderStatus.PLACED, "placed_at": utc_now()}
        )
        await self._orders.save_order(updated)
        await self._orders.add_event(
            order_id,
            EventType.PLACED,
            payload={
                "event": ORDER_PLACED,
                "status": updated.status.value,
                "table_id": str(updated.table_id),
                "placed_at": updated.placed_at.isoformat() if updated.placed_at else None,
                "items": [
                    {
                        "item_id": str(it.id),
                        "menu_item_id": str(it.menu_item_id),
                        "station_id": str(it.station_id),
                        "quantity": it.quantity,
                        "customizations": it.customizations,
                        "allergy_notes": it.allergy_notes,
                    }
                    for it in updated.items
                ],
            },
        )
        return updated

    async def cancel_order(self, order_id: UUID, reason: str | None = None) -> Order:
        order = await self.get_order(order_id)
        if order.status in {OrderStatus.CLOSED, OrderStatus.CANCELLED}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Order already finished")
        updated = order.model_copy(update={"status": OrderStatus.CANCELLED})
        await self._orders.save_order(updated)
        await self._orders.add_event(
            order_id,
            EventType.CANCELLED,
            payload={
                "event": ORDER_CANCELLED,
                "reason": reason,
                "table_id": str(updated.table_id),
            },
        )
        return updated

    async def serve_order(self, order_id: UUID) -> Order:
        order = await self.get_order(order_id)
        if order.status != OrderStatus.READY:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Only ready orders can be served"
            )
        served_items = [
            item.model_copy(update={"status": ItemStatus.SERVED})
            if item.status == ItemStatus.READY
            else item
            for item in order.items
        ]
        updated = order.model_copy(
            update={
                "status": OrderStatus.SERVED,
                "served_at": utc_now(),
                "items": served_items,
            }
        )
        await self._orders.save_order(updated)
        await self._orders.add_event(
            order_id,
            EventType.STATUS_CHANGED,
            payload={
                "event": ORDER_SERVED,
                "status": updated.status.value,
                "table_id": str(updated.table_id),
                "served_at": updated.served_at.isoformat() if updated.served_at else None,
            },
        )
        return updated

    async def close_order(self, order_id: UUID) -> Order:
        order = await self.get_order(order_id)
        if order.status not in {OrderStatus.SERVED, OrderStatus.READY}:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Only ready or served orders can be closed",
            )
        updated = order.model_copy(update={"status": OrderStatus.CLOSED})
        await self._orders.save_order(updated)
        return updated
