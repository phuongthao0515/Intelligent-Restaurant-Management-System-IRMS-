from __future__ import annotations

import uuid
from decimal import Decimal
from uuid import UUID

import pytest

from app.modules.kds.service import KdsService
from app.modules.menu.services.menu_service import MenuService
from app.modules.ordering.services.order_service import OrderService
from app.modules.table.services.table_service import TableService
from app.shared.models import (
    EventType,
    MenuCategory,
    MenuItem,
    Order,
    OrderEvent,
    OrderStatus,
    Station,
    Table,
    now_ict,
)


class InMemoryMenuRepository:
    def __init__(self) -> None:
        self.categories: dict[UUID, MenuCategory] = {}
        self.items: dict[UUID, MenuItem] = {}

    async def list_categories(self) -> list[MenuCategory]:
        return list(self.categories.values())

    async def get_category(self, category_id: UUID) -> MenuCategory | None:
        return self.categories.get(category_id)

    async def save_category(self, category: MenuCategory) -> None:
        self.categories[category.id] = category

    async def list_items(self) -> list[MenuItem]:
        return list(self.items.values())

    async def get_item(self, item_id: UUID) -> MenuItem | None:
        return self.items.get(item_id)

    async def save_item(self, item: MenuItem) -> None:
        self.items[item.id] = item


class InMemoryTableRepository:
    def __init__(self) -> None:
        self.tables: dict[UUID, Table] = {}

    async def list_tables(self) -> list[Table]:
        return list(self.tables.values())

    async def get_table(self, table_id: UUID) -> Table | None:
        return self.tables.get(table_id)


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self.orders: dict[UUID, Order] = {}
        self.events: list[OrderEvent] = []

    async def list_orders(self) -> list[Order]:
        return list(self.orders.values())

    async def get_order(self, order_id: UUID) -> Order | None:
        return self.orders.get(order_id)

    async def save_order(self, order: Order) -> None:
        self.orders[order.id] = order

    async def list_active_table_ids(
        self, active_statuses
    ) -> set[UUID]:
        statuses = set(active_statuses)
        return {
            order.table_id
            for order in self.orders.values()
            if order.status in statuses
        }

    async def add_event(
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
            created_at=now_ict(),
        )
        self.events.append(event)
        return event

    async def list_events(
        self, order_id: UUID | None = None, since: str | None = None
    ) -> list[OrderEvent]:
        events = self.events
        if order_id is not None:
            events = [e for e in events if e.order_id == order_id]
        if since is not None:
            events = [e for e in events if e.created_at.isoformat() >= since]
        return events


class InMemoryStationRepository:
    def __init__(self) -> None:
        self.stations: dict[UUID, Station] = {}

    async def list_stations(self) -> list[Station]:
        return list(self.stations.values())

    async def get_station(self, station_id: UUID) -> Station | None:
        return self.stations.get(station_id)

    async def save_station(self, station: Station) -> None:
        self.stations[station.id] = station


@pytest.fixture
def menu_repo() -> InMemoryMenuRepository:
    return InMemoryMenuRepository()


@pytest.fixture
def table_repo() -> InMemoryTableRepository:
    return InMemoryTableRepository()


@pytest.fixture
def order_repo() -> InMemoryOrderRepository:
    return InMemoryOrderRepository()


@pytest.fixture
def station_repo() -> InMemoryStationRepository:
    return InMemoryStationRepository()


@pytest.fixture
def menu_service(menu_repo: InMemoryMenuRepository) -> MenuService:
    return MenuService(menu_repo)


@pytest.fixture
def table_service(
    table_repo: InMemoryTableRepository,
    order_repo: InMemoryOrderRepository,
) -> TableService:
    return TableService(table_repo, order_repo)


@pytest.fixture
def order_service(
    order_repo: InMemoryOrderRepository,
    menu_service: MenuService,
    table_service: TableService,
) -> OrderService:
    return OrderService(orders=order_repo, menus=menu_service, tables=table_service)


@pytest.fixture
def kds_service(
    station_repo: InMemoryStationRepository,
    order_service: OrderService,
    table_service: TableService,
) -> KdsService:
    return KdsService(
        stations=station_repo, orders=order_service, tables=table_service
    )


@pytest.fixture
def seeded_table(table_repo: InMemoryTableRepository) -> Table:
    table = Table(id=uuid.uuid4(), number=1, seats=4, is_occupied=False)
    table_repo.tables[table.id] = table
    return table


@pytest.fixture
def seeded_category(menu_repo: InMemoryMenuRepository) -> MenuCategory:
    category = MenuCategory(id=uuid.uuid4(), name="Mains", display_order=1)
    menu_repo.categories[category.id] = category
    return category


@pytest.fixture
def seeded_station(station_repo: InMemoryStationRepository) -> Station:
    station = Station(id=uuid.uuid4(), name="Grill", is_active=True)
    station_repo.stations[station.id] = station
    return station


@pytest.fixture
def seeded_menu_item(
    menu_repo: InMemoryMenuRepository,
    seeded_category: MenuCategory,
    seeded_station: Station,
) -> MenuItem:
    item = MenuItem(
        id=uuid.uuid4(),
        name="Burger",
        description="Classic beef burger",
        price=Decimal("12.50"),
        category_id=seeded_category.id,
        station_id=seeded_station.id,
        prep_time_min=10,
        is_available=True,
        is_combo=False,
        customization_schema={},
    )
    menu_repo.items[item.id] = item
    return item
