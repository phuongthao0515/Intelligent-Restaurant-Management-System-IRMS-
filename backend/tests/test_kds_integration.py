from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException

from app.shared.models import (
    EventType,
    ItemStatus,
    ItemStatusUpdate,
    OrderCreate,
    OrderItemCreate,
    OrderStatus,
    RecallOrderRequest,
)


async def _place_order_with_items(
    order_service, table, menu_item, item_count: int = 1
):
    order = await order_service.create_order(
        OrderCreate(table_id=table.id, customer_id=None)
    )
    for _ in range(item_count):
        await order_service.add_order_item(
            order.id,
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                customizations={},
                allergy_notes=None,
            ),
        )
    return await order_service.submit_order(order.id)


async def test_kds_list_tickets_returns_only_placed_orders_with_station_items(
    kds_service, order_service, seeded_table, seeded_menu_item, seeded_station
):
    draft = await order_service.create_order(
        OrderCreate(table_id=seeded_table.id, customer_id=None)
    )
    await order_service.add_order_item(
        draft.id,
        OrderItemCreate(
            menu_item_id=seeded_menu_item.id,
            quantity=1,
            customizations={},
            allergy_notes=None,
        ),
    )

    placed = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=1
    )

    tickets = await kds_service.list_tickets(seeded_station.id)

    assert len(tickets) == 1
    assert tickets[0].order_id == placed.id
    assert tickets[0].table_number == seeded_table.number


async def test_kds_list_tickets_filters_active_status(
    kds_service, order_service, seeded_table, seeded_menu_item, seeded_station
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=2
    )
    await kds_service.bump_order_item(order.items[0].id)

    active = await kds_service.list_tickets(seeded_station.id, status_filter="ACTIVE")

    assert len(active) == 1
    assert all(
        item.status in {ItemStatus.QUEUED, ItemStatus.PREPARING}
        for item in active[0].items
    )


async def test_kds_list_tickets_raises_for_unknown_station(kds_service):
    with pytest.raises(HTTPException) as exc:
        await kds_service.list_tickets(uuid.uuid4())
    assert exc.value.status_code == 404


async def test_kds_bump_item_marks_ready_and_sets_timestamp(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=1
    )
    bumped = await kds_service.bump_order_item(order.items[0].id)

    assert bumped.status == ItemStatus.READY
    assert bumped.ready_at is not None


async def test_kds_bump_all_items_auto_promotes_order_to_ready(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=2
    )
    for item in order.items:
        await kds_service.bump_order_item(item.id)

    refreshed = await order_service.get_order(order.id)
    assert refreshed.status == OrderStatus.READY
    assert all(item.status == ItemStatus.READY for item in refreshed.items)


async def test_kds_bump_one_item_keeps_order_in_kitchen_when_others_pending(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=2
    )
    await kds_service.bump_order_item(order.items[0].id)

    refreshed = await order_service.get_order(order.id)
    assert refreshed.status == OrderStatus.IN_KITCHEN
    assert refreshed.items[0].status == ItemStatus.READY
    assert refreshed.items[1].status == ItemStatus.QUEUED


async def test_kds_update_status_to_preparing_transitions_order_to_in_kitchen(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=1
    )
    await kds_service.update_order_item_status(
        order.items[0].id, ItemStatusUpdate(new_status=ItemStatus.PREPARING)
    )

    refreshed = await order_service.get_order(order.id)
    assert refreshed.status == OrderStatus.IN_KITCHEN
    assert refreshed.items[0].status == ItemStatus.PREPARING
    assert refreshed.items[0].started_at is not None


async def test_kds_recall_resets_items_and_transitions_to_in_kitchen(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=2
    )
    for item in order.items:
        await kds_service.bump_order_item(item.id)

    recalled = await kds_service.recall_order(
        order.id, RecallOrderRequest(reason="missing_garnish")
    )

    assert recalled.status == OrderStatus.IN_KITCHEN
    assert all(item.status == ItemStatus.QUEUED for item in recalled.items)
    assert all(item.ready_at is None for item in recalled.items)
    assert all(item.started_at is None for item in recalled.items)


async def test_kds_recall_rejects_draft_order(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    draft = await order_service.create_order(
        OrderCreate(table_id=seeded_table.id, customer_id=None)
    )
    await order_service.add_order_item(
        draft.id,
        OrderItemCreate(
            menu_item_id=seeded_menu_item.id,
            quantity=1,
            customizations={},
            allergy_notes=None,
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await kds_service.recall_order(draft.id)
    assert exc.value.status_code == 409


async def test_kds_list_events_returns_placed_event(
    kds_service, order_service, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=1
    )
    events = await kds_service.list_events(order_id=order.id)

    assert any(e.event_type == EventType.PLACED for e in events)
    assert all(e.order_id == order.id for e in events)


async def test_kds_writes_only_via_order_service(
    kds_service, order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _place_order_with_items(
        order_service, seeded_table, seeded_menu_item, item_count=2
    )
    for item in order.items:
        await kds_service.bump_order_item(item.id)
    await kds_service.recall_order(order.id, RecallOrderRequest(reason="quality"))

    final = order_repo.orders[order.id]
    assert final.status == OrderStatus.IN_KITCHEN
    assert all(item.status == ItemStatus.QUEUED for item in final.items)
    assert any(e.event_type == EventType.RECALLED for e in order_repo.events)
    assert any(
        e.payload.get("auto_promoted") is True for e in order_repo.events
    )
