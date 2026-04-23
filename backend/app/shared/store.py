from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

from app.shared.events import EventBus
from app.shared.models import (
    EventType,
    MenuCategory,
    MenuItem,
    Order,
    OrderEvent,
    OrderStatus,
    Station,
    Table,
    utc_now,
)
from app.shared.websocket import ConnectionManager, WebSocketBroadcaster


class InMemoryStore:
    def __init__(self) -> None:
        category_main_id = uuid.uuid4()
        station_grill_id = uuid.uuid4()
        menu_salmon_id = uuid.uuid4()
        table_one_id = uuid.uuid4()
        table_five_id = uuid.uuid4()

        self.categories: dict[UUID, MenuCategory] = {
            category_main_id: MenuCategory(id=category_main_id, name="Main", display_order=1),
        }
        self.menu_items: dict[UUID, MenuItem] = {
            menu_salmon_id: MenuItem(
                id=menu_salmon_id,
                name="Grilled Salmon",
                description="Sample item",
                price=Decimal("18.50"),
                category_id=category_main_id,
                station_id=station_grill_id,
                prep_time_min=12,
                is_available=True,
            ),
        }
        self.tables: dict[UUID, Table] = {
            table_one_id: Table(id=table_one_id, number=1, seats=4, is_occupied=False),
            table_five_id: Table(id=table_five_id, number=5, seats=6, is_occupied=True),
        }
        self.orders: dict[UUID, Order] = {}
        self.stations: dict[UUID, Station] = {
            station_grill_id: Station(id=station_grill_id, name="Grill", is_active=True),
        }
        self.events: dict[UUID, OrderEvent] = {}

        self.bus = EventBus()
        self.connections = ConnectionManager()
        self.broadcaster = WebSocketBroadcaster(self.connections)

    def add_event(
        self,
        order_id: UUID,
        event_type: EventType,
        order_item_id: UUID | None = None,
        payload: dict | None = None,
    ) -> OrderEvent:
        event = OrderEvent(
            id=uuid.uuid4(),
            order_id=order_id,
            order_item_id=order_item_id,
            event_type=event_type,
            payload=payload or {},
            created_at=utc_now(),
        )
        self.events[event.id] = event
        return event


store = InMemoryStore()
