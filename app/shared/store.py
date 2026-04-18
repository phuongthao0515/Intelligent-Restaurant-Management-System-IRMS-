from __future__ import annotations

from decimal import Decimal

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
        self.category_seq = 2
        self.menu_item_seq = 2
        self.order_seq = 1
        self.order_item_seq = 1
        self.station_seq = 2
        self.event_seq = 1

        self.categories: dict[int, MenuCategory] = {
            1: MenuCategory(id=1, name="Main", display_order=1),
        }
        self.menu_items: dict[int, MenuItem] = {
            1: MenuItem(
                id=1,
                name="Grilled Salmon",
                description="Sample item",
                price=Decimal("18.50"),
                category_id=1,
                station_id=1,
                prep_time_min=12,
                is_available=True,
            ),
        }
        self.tables: dict[int, Table] = {
            1: Table(id=1, number=1, seats=4, is_occupied=False),
            2: Table(id=2, number=5, seats=6, is_occupied=True),
        }
        self.orders: dict[int, Order] = {}
        self.stations: dict[int, Station] = {
            1: Station(id=1, name="Grill", is_active=True),
        }
        self.events: dict[int, OrderEvent] = {}

        self.bus = EventBus()
        self.connections = ConnectionManager()
        self.broadcaster = WebSocketBroadcaster(self.connections)

    def next_category_id(self) -> int:
        value = self.category_seq
        self.category_seq += 1
        return value

    def next_menu_item_id(self) -> int:
        value = self.menu_item_seq
        self.menu_item_seq += 1
        return value

    def next_order_id(self) -> int:
        value = self.order_seq
        self.order_seq += 1
        return value

    def next_order_item_id(self) -> int:
        value = self.order_item_seq
        self.order_item_seq += 1
        return value

    def next_station_id(self) -> int:
        value = self.station_seq
        self.station_seq += 1
        return value

    def add_event(
        self,
        order_id: int,
        event_type: EventType,
        order_item_id: int | None = None,
        payload: dict | None = None,
    ) -> OrderEvent:
        event = OrderEvent(
            id=self.event_seq,
            order_id=order_id,
            order_item_id=order_item_id,
            event_type=event_type,
            payload=payload or {},
            created_at=utc_now(),
        )
        self.events[event.id] = event
        self.event_seq += 1
        return event


store = InMemoryStore()
