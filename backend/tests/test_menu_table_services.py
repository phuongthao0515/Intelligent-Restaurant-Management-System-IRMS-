from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.shared.models import (
    ItemAvailabilityUpdate,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItem,
    Order,
    OrderStatus,
    Table,
    now_ict,
)


async def test_create_category_persists_with_uuid_and_returns_it(
    menu_service, menu_repo
):
    payload = MenuCategoryCreate(name="Drinks", display_order=2)
    created = await menu_service.create_category(payload)

    assert created.id in menu_repo.categories
    assert created.name == "Drinks"
    assert created.display_order == 2


async def test_update_category_partial_payload_merges_existing_fields(
    menu_service, seeded_category, menu_repo
):
    payload = MenuCategoryUpdate(display_order=5)
    updated = await menu_service.update_category(seeded_category.id, payload)

    assert updated.name == seeded_category.name
    assert updated.display_order == 5
    assert menu_repo.categories[seeded_category.id].display_order == 5


async def test_update_category_raises_404_for_unknown_id(menu_service):
    with pytest.raises(HTTPException) as exc:
        await menu_service.update_category(
            uuid.uuid4(), MenuCategoryUpdate(name="X")
        )
    assert exc.value.status_code == 404


async def test_list_menu_items_filters_by_category_and_availability(
    menu_service, menu_repo, seeded_category, seeded_station
):
    other_category = uuid.uuid4()
    items = [
        MenuItem(
            id=uuid.uuid4(),
            name="Burger",
            price=Decimal("10.00"),
            category_id=seeded_category.id,
            station_id=seeded_station.id,
            is_available=True,
        ),
        MenuItem(
            id=uuid.uuid4(),
            name="Salad",
            price=Decimal("8.00"),
            category_id=seeded_category.id,
            station_id=seeded_station.id,
            is_available=False,
        ),
        MenuItem(
            id=uuid.uuid4(),
            name="Cola",
            price=Decimal("3.00"),
            category_id=other_category,
            station_id=seeded_station.id,
            is_available=True,
        ),
    ]
    for item in items:
        menu_repo.items[item.id] = item

    by_category = await menu_service.list_menu_items(
        category_id=seeded_category.id
    )
    assert {i.name for i in by_category} == {"Burger", "Salad"}

    by_avail = await menu_service.list_menu_items(
        category_id=seeded_category.id, is_available=True
    )
    assert {i.name for i in by_avail} == {"Burger"}


async def test_update_item_availability_flips_flag(
    menu_service, seeded_menu_item, menu_repo
):
    updated = await menu_service.update_item_availability(
        seeded_menu_item.id, ItemAvailabilityUpdate(is_available=False)
    )
    assert updated.is_available is False
    assert menu_repo.items[seeded_menu_item.id].is_available is False


async def test_get_table_returns_seeded_table(table_service, seeded_table):
    table = await table_service.get_table(seeded_table.id)
    assert table.id == seeded_table.id
    assert table.number == seeded_table.number


async def test_get_table_raises_404_for_unknown_id(table_service):
    with pytest.raises(HTTPException) as exc:
        await table_service.get_table(uuid.uuid4())
    assert exc.value.status_code == 404


def _seed_table(table_repo, number: int = 1) -> Table:
    table = Table(id=uuid.uuid4(), number=number, seats=4, is_occupied=False)
    table_repo.tables[table.id] = table
    return table


def _seed_order(order_repo, table_id, status: OrderStatus) -> Order:
    order = Order(
        id=uuid.uuid4(),
        table_id=table_id,
        status=status,
        created_at=now_ict(),
    )
    order_repo.orders[order.id] = order
    return order


async def test_table_is_available_when_no_orders_exist(
    table_service, table_repo
):
    table = _seed_table(table_repo)

    listed = await table_service.list_tables()
    fetched = await table_service.get_table(table.id)

    assert listed[0].is_occupied is False
    assert fetched.is_occupied is False


@pytest.mark.parametrize(
    "active_status",
    [
        OrderStatus.DRAFT,
        OrderStatus.PLACED,
        OrderStatus.IN_KITCHEN,
        OrderStatus.READY,
        OrderStatus.SERVED,
    ],
)
async def test_table_is_occupied_for_any_active_order_status(
    table_service, table_repo, order_repo, active_status
):
    table = _seed_table(table_repo)
    _seed_order(order_repo, table.id, active_status)

    listed = await table_service.list_tables()
    fetched = await table_service.get_table(table.id)

    assert listed[0].is_occupied is True, f"expected occupied for {active_status}"
    assert fetched.is_occupied is True


@pytest.mark.parametrize(
    "terminal_status", [OrderStatus.CLOSED, OrderStatus.CANCELLED]
)
async def test_table_is_available_when_only_terminal_orders_exist(
    table_service, table_repo, order_repo, terminal_status
):
    table = _seed_table(table_repo)
    _seed_order(order_repo, table.id, terminal_status)

    listed = await table_service.list_tables()
    fetched = await table_service.get_table(table.id)

    assert listed[0].is_occupied is False, f"expected available for {terminal_status}"
    assert fetched.is_occupied is False


async def test_table_returns_to_available_after_all_orders_close(
    table_service, table_repo, order_repo
):
    table = _seed_table(table_repo)
    order = _seed_order(order_repo, table.id, OrderStatus.PLACED)

    fetched = await table_service.get_table(table.id)
    assert fetched.is_occupied is True

    order_repo.orders[order.id] = order.model_copy(
        update={"status": OrderStatus.CLOSED}
    )

    fetched_after = await table_service.get_table(table.id)
    assert fetched_after.is_occupied is False


async def test_list_tables_marks_only_tables_with_active_orders(
    table_service, table_repo, order_repo
):
    occupied_table = _seed_table(table_repo, number=1)
    free_table = _seed_table(table_repo, number=2)
    _seed_order(order_repo, occupied_table.id, OrderStatus.IN_KITCHEN)

    by_id = {t.id: t for t in await table_service.list_tables()}

    assert by_id[occupied_table.id].is_occupied is True
    assert by_id[free_table.id].is_occupied is False


async def test_table_stays_occupied_when_one_active_order_remains(
    table_service, table_repo, order_repo
):
    table = _seed_table(table_repo)
    closed = _seed_order(order_repo, table.id, OrderStatus.PLACED)
    _seed_order(order_repo, table.id, OrderStatus.IN_KITCHEN)

    order_repo.orders[closed.id] = closed.model_copy(
        update={"status": OrderStatus.CLOSED}
    )

    fetched = await table_service.get_table(table.id)
    assert fetched.is_occupied is True
