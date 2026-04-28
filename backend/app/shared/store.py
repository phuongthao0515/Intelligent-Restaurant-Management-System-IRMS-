from __future__ import annotations
from app.shared.models import OrderItem, ItemStatus

import uuid
from datetime import timedelta
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
        # Categories
        category_main_id = uuid.uuid4()
        category_appetizer_id = uuid.uuid4()
        category_beverage_id = uuid.uuid4()
        category_dessert_id = uuid.uuid4()
        
        # Stations
        station_grill_id = uuid.uuid4()
        station_kitchen_id = uuid.uuid4()
        station_fryer_id = uuid.uuid4()
        station_bar_id = uuid.uuid4()
        station_cold_id = uuid.uuid4()

        # Menu Items
        menu_salmon_id = uuid.uuid4()
        menu_steak_id = uuid.uuid4()
        menu_fish_id = uuid.uuid4()
        menu_fries_id = uuid.uuid4()
        menu_wings_id = uuid.uuid4()
        menu_salad_id = uuid.uuid4()
        menu_soup_id = uuid.uuid4()
        menu_pasta_id = uuid.uuid4()
        menu_burger_id = uuid.uuid4()
        menu_coke_id = uuid.uuid4()
        menu_coffee_id = uuid.uuid4()
        menu_dessert_id = uuid.uuid4()

        # Tables
        table_one_id = uuid.uuid4()
        table_two_id = uuid.uuid4()
        table_three_id = uuid.uuid4()
        table_four_id = uuid.uuid4()
        table_five_id = uuid.uuid4()

        self.categories: dict[UUID, MenuCategory] = {
            category_main_id: MenuCategory(id=category_main_id, name="Main", display_order=1),
            category_appetizer_id: MenuCategory(id=category_appetizer_id, name="Appetizer", display_order=2),
            category_beverage_id: MenuCategory(id=category_beverage_id, name="Beverage", display_order=3),
            category_dessert_id: MenuCategory(id=category_dessert_id, name="Dessert", display_order=4),
        }
        
        self.menu_items: dict[UUID, MenuItem] = {
            menu_salmon_id: MenuItem(
                id=menu_salmon_id,
                name="Grilled Salmon",
                description="Fresh grilled salmon fillet",
                price=Decimal("18.50"),
                category_id=category_main_id,
                station_id=station_grill_id,
                prep_time_min=12,
                is_available=True,
            ),
            menu_steak_id: MenuItem(
                id=menu_steak_id,
                name="Ribeye Steak",
                description="Prime ribeye cooked to order",
                price=Decimal("24.99"),
                category_id=category_main_id,
                station_id=station_grill_id,
                prep_time_min=15,
                is_available=True,
            ),
            menu_fish_id: MenuItem(
                id=menu_fish_id,
                name="Fish & Chips",
                description="Crispy battered fish",
                price=Decimal("14.99"),
                category_id=category_main_id,
                station_id=station_fryer_id,
                prep_time_min=10,
                is_available=True,
            ),
            menu_fries_id: MenuItem(
                id=menu_fries_id,
                name="French Fries",
                description="Golden crispy fries",
                price=Decimal("5.99"),
                category_id=category_appetizer_id,
                station_id=station_fryer_id,
                prep_time_min=8,
                is_available=True,
            ),
            menu_wings_id: MenuItem(
                id=menu_wings_id,
                name="Buffalo Wings",
                description="Spicy buffalo wings",
                price=Decimal("12.99"),
                category_id=category_appetizer_id,
                station_id=station_fryer_id,
                prep_time_min=12,
                is_available=True,
            ),
            menu_salad_id: MenuItem(
                id=menu_salad_id,
                name="Caesar Salad",
                description="Fresh greens with parmesan",
                price=Decimal("9.99"),
                category_id=category_appetizer_id,
                station_id=station_cold_id,
                prep_time_min=5,
                is_available=True,
            ),
            menu_soup_id: MenuItem(
                id=menu_soup_id,
                name="Tomato Soup",
                description="Creamy tomato soup",
                price=Decimal("7.99"),
                category_id=category_appetizer_id,
                station_id=station_kitchen_id,
                prep_time_min=8,
                is_available=True,
            ),
            menu_pasta_id: MenuItem(
                id=menu_pasta_id,
                name="Pasta Carbonara",
                description="Classic Italian pasta",
                price=Decimal("16.99"),
                category_id=category_main_id,
                station_id=station_kitchen_id,
                prep_time_min=12,
                is_available=True,
            ),
            menu_burger_id: MenuItem(
                id=menu_burger_id,
                name="Gourmet Burger",
                description="Premium beef burger",
                price=Decimal("15.99"),
                category_id=category_main_id,
                station_id=station_grill_id,
                prep_time_min=10,
                is_available=True,
            ),
            menu_coke_id: MenuItem(
                id=menu_coke_id,
                name="Soft Drink",
                description="Assorted soft drinks",
                price=Decimal("3.99"),
                category_id=category_beverage_id,
                station_id=station_bar_id,
                prep_time_min=1,
                is_available=True,
            ),
            menu_coffee_id: MenuItem(
                id=menu_coffee_id,
                name="Espresso Coffee",
                description="Double shot espresso",
                price=Decimal("4.99"),
                category_id=category_beverage_id,
                station_id=station_bar_id,
                prep_time_min=3,
                is_available=True,
            ),
            menu_dessert_id: MenuItem(
                id=menu_dessert_id,
                name="Chocolate Cake",
                description="Decadent chocolate cake",
                price=Decimal("8.99"),
                category_id=category_dessert_id,
                station_id=station_cold_id,
                prep_time_min=2,
                is_available=True,
            ),
        }
        
        self.tables: dict[UUID, Table] = {
            table_one_id: Table(id=table_one_id, number=1, seats=2, is_occupied=True),
            table_two_id: Table(id=table_two_id, number=2, seats=2, is_occupied=True),
            table_three_id: Table(id=table_three_id, number=3, seats=4, is_occupied=True),
            table_four_id: Table(id=table_four_id, number=4, seats=4, is_occupied=True),
            table_five_id: Table(id=table_five_id, number=5, seats=6, is_occupied=True),
        }
        
        self.stations: dict[UUID, Station] = {
            station_grill_id: Station(id=station_grill_id, name="Grill", is_active=True),
            station_kitchen_id: Station(id=station_kitchen_id, name="Kitchen", is_active=True),
            station_fryer_id: Station(id=station_fryer_id, name="Fryer", is_active=True),
            station_bar_id: Station(id=station_bar_id, name="Bar", is_active=True),
            station_cold_id: Station(id=station_cold_id, name="Cold Prep", is_active=True),
        }
        
        # Create test orders with items in various states
        order1_id = uuid.uuid4()
        order2_id = uuid.uuid4()
        order3_id = uuid.uuid4()
        order4_id = uuid.uuid4()
        
        now = utc_now()
        
        # Order 1: Table 1 - Mix of queued and preparing items
        order1 = Order(
            id=order1_id,
            table_id=table_one_id,
            customer_id=None,
            type="DINE_IN",
            status=OrderStatus.IN_KITCHEN,
            subtotal=Decimal("32.48"),
            items=[
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order1_id,
                    menu_item_id=menu_steak_id,
                    qty=1,
                    unit_price=Decimal("24.99"),
                    status=ItemStatus.QUEUED,
                    station_id=station_grill_id,
                ),
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order1_id,
                    menu_item_id=menu_fries_id,
                    qty=2,
                    unit_price=Decimal("5.99"),
                    status=ItemStatus.PREPARING,
                    station_id=station_fryer_id,
                    started_at=now,
                ),
            ],
            created_at=now - timedelta(minutes=5),
            placed_at=now - timedelta(minutes=5),
        )
        
        # Order 2: Table 3 - Some items ready
        order2 = Order(
            id=order2_id,
            table_id=table_three_id,
            customer_id=None,
            type="DINE_IN",
            status=OrderStatus.READY,
            subtotal=Decimal("34.97"),
            items=[
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order2_id,
                    menu_item_id=menu_fish_id,
                    qty=1,
                    unit_price=Decimal("14.99"),
                    status=ItemStatus.READY,
                    station_id=station_fryer_id,
                    started_at=now - timedelta(minutes=8),
                    ready_at=now - timedelta(minutes=2),
                ),
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order2_id,
                    menu_item_id=menu_salad_id,
                    qty=1,
                    unit_price=Decimal("9.99"),
                    status=ItemStatus.READY,
                    station_id=station_cold_id,
                    started_at=now - timedelta(minutes=3),
                    ready_at=now - timedelta(minutes=1),
                ),
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order2_id,
                    menu_item_id=menu_coke_id,
                    qty=2,
                    unit_price=Decimal("3.99"),
                    status=ItemStatus.SERVED,
                    station_id=station_bar_id,
                ),
            ],
            created_at=now - timedelta(minutes=10),
            placed_at=now - timedelta(minutes=10),
            ready_at=now - timedelta(minutes=1),
        )
        
        # Order 3: Table 2 - Mostly preparing
        order3 = Order(
            id=order3_id,
            table_id=table_two_id,
            customer_id=None,
            type="DINE_IN",
            status=OrderStatus.IN_KITCHEN,
            subtotal=Decimal("41.97"),
            items=[
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order3_id,
                    menu_item_id=menu_burger_id,
                    qty=1,
                    unit_price=Decimal("15.99"),
                    status=ItemStatus.PREPARING,
                    station_id=station_grill_id,
                    started_at=now - timedelta(minutes=4),
                ),
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order3_id,
                    menu_item_id=menu_wings_id,
                    qty=1,
                    unit_price=Decimal("12.99"),
                    status=ItemStatus.QUEUED,
                    station_id=station_fryer_id,
                ),
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order3_id,
                    menu_item_id=menu_soup_id,
                    qty=1,
                    unit_price=Decimal("7.99"),
                    status=ItemStatus.QUEUED,
                    station_id=station_kitchen_id,
                ),
            ],
            created_at=now - timedelta(minutes=8),
            placed_at=now - timedelta(minutes=8),
        )
        
        # Order 4: Table 4 - Just placed
        order4 = Order(
            id=order4_id,
            table_id=table_four_id,
            customer_id=None,
            type="DINE_IN",
            status=OrderStatus.PLACED,
            subtotal=Decimal("21.98"),
            items=[
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order4_id,
                    menu_item_id=menu_salmon_id,
                    qty=1,
                    unit_price=Decimal("18.50"),
                    status=ItemStatus.QUEUED,
                    station_id=station_grill_id,
                ),
                OrderItem(
                    id=uuid.uuid4(),
                    order_id=order4_id,
                    menu_item_id=menu_dessert_id,
                    qty=1,
                    unit_price=Decimal("8.99"),
                    status=ItemStatus.QUEUED,
                    station_id=station_cold_id,
                ),
            ],
            created_at=now - timedelta(minutes=1),
            placed_at=now - timedelta(minutes=1),
        )
        
        self.orders: dict[UUID, Order] = {
            order1_id: order1,
            order2_id: order2,
            order3_id: order3,
            order4_id: order4,
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
