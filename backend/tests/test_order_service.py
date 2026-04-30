from __future__ import annotations

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.shared.models import (
    EventType,
    ItemStatus,
    Order,
    OrderCreate,
    OrderItemCreate,
    OrderStatus,
    now_ict,
)


def test_now_ict_returns_vietnam_offset():
    ts = now_ict()
    assert ts.utcoffset() == timedelta(hours=7)
    assert ts.tzinfo is not None


async def _make_placed_order(order_service, table, menu_item, quantity: int = 1):
    order = await order_service.create_order(
        OrderCreate(table_id=table.id, customer_id=None)
    )
    await order_service.add_order_item(
        order.id,
        OrderItemCreate(
            menu_item_id=menu_item.id,
            quantity=quantity,
            customizations={},
            allergy_notes=None,
        ),
    )
    return await order_service.submit_order(order.id)


async def test_create_order_persists_with_draft_status(
    order_service, order_repo, seeded_table
):
    order = await order_service.create_order(
        OrderCreate(table_id=seeded_table.id, customer_id=None)
    )

    assert order.status == OrderStatus.DRAFT
    assert order.id in order_repo.orders
    assert order_repo.orders[order.id].table_id == seeded_table.id


async def test_create_order_rejects_unknown_table(order_service):
    with pytest.raises(HTTPException) as exc:
        await order_service.create_order(
            OrderCreate(table_id=uuid.uuid4(), customer_id=None)
        )
    assert exc.value.status_code == 404


async def test_add_order_item_updates_subtotal(
    order_service, seeded_table, seeded_menu_item
):
    order = await order_service.create_order(
        OrderCreate(table_id=seeded_table.id, customer_id=None)
    )
    await order_service.add_order_item(
        order.id,
        OrderItemCreate(
            menu_item_id=seeded_menu_item.id,
            quantity=2,
            customizations={},
            allergy_notes=None,
        ),
    )
    refreshed = await order_service.get_order(order.id)
    assert refreshed.subtotal == seeded_menu_item.price * 2
    assert len(refreshed.items) == 1


async def test_add_order_item_rejects_unavailable_menu_item(
    order_service, menu_repo, seeded_table, seeded_menu_item
):
    seeded_menu_item.is_available = False
    menu_repo.items[seeded_menu_item.id] = seeded_menu_item

    order = await order_service.create_order(
        OrderCreate(table_id=seeded_table.id, customer_id=None)
    )
    with pytest.raises(HTTPException) as exc:
        await order_service.add_order_item(
            order.id,
            OrderItemCreate(
                menu_item_id=seeded_menu_item.id,
                quantity=1,
                customizations={},
                allergy_notes=None,
            ),
        )
    assert exc.value.status_code == 409


async def test_add_order_item_rejects_non_draft_order(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    with pytest.raises(HTTPException) as exc:
        await order_service.add_order_item(
            order.id,
            OrderItemCreate(
                menu_item_id=seeded_menu_item.id,
                quantity=1,
                customizations={},
                allergy_notes=None,
            ),
        )
    assert exc.value.status_code == 409


async def test_submit_order_transitions_to_placed_and_writes_event(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)

    assert order.status == OrderStatus.PLACED
    assert order.placed_at is not None
    placed_events = [
        e for e in order_repo.events if e.event_type == EventType.PLACED
    ]
    assert len(placed_events) == 1
    assert placed_events[0].order_id == order.id


async def test_cancel_order_writes_cancelled_event_with_reason(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    cancelled = await order_service.cancel_order(order.id, reason="customer_left")

    assert cancelled.status == OrderStatus.CANCELLED
    cancelled_events = [
        e for e in order_repo.events if e.event_type == EventType.CANCELLED
    ]
    assert len(cancelled_events) == 1
    assert cancelled_events[0].payload.get("reason") == "customer_left"


async def test_update_item_status_to_preparing_sets_started_at(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    item = order.items[0]
    updated = await order_service.update_item_status(item.id, ItemStatus.PREPARING)

    assert updated.status == ItemStatus.PREPARING
    assert updated.started_at is not None
    assert updated.ready_at is None


async def test_update_item_status_to_ready_sets_ready_at(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    item = order.items[0]
    updated = await order_service.update_item_status(item.id, ItemStatus.READY)

    assert updated.status == ItemStatus.READY
    assert updated.ready_at is not None


async def test_update_item_status_rejects_terminal_orders(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    cancelled = order.model_copy(update={"status": OrderStatus.CANCELLED})
    order_repo.orders[order.id] = cancelled

    with pytest.raises(HTTPException) as exc:
        await order_service.update_item_status(order.items[0].id, ItemStatus.READY)
    assert exc.value.status_code == 409


async def test_transition_order_to_ready_promotes_status_and_emits_event(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    promoted = await order_service.transition_order_to_ready(order.id)

    assert promoted.status == OrderStatus.READY
    assert promoted.ready_at is not None
    auto_events = [
        e for e in order_repo.events if e.payload.get("auto_promoted") is True
    ]
    assert len(auto_events) == 1


async def test_transition_order_to_ready_is_idempotent_when_already_ready(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    first = await order_service.transition_order_to_ready(order.id)
    second = await order_service.transition_order_to_ready(order.id)

    assert first.status == OrderStatus.READY
    assert second.status == OrderStatus.READY
    assert second.id == first.id


async def test_recall_order_resets_items_and_transitions_to_in_kitchen(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    await order_service.update_item_status(order.items[0].id, ItemStatus.READY)
    await order_service.transition_order_to_ready(order.id)

    recalled = await order_service.recall_order(order.id, reason="missing_garnish")

    assert recalled.status == OrderStatus.IN_KITCHEN
    assert recalled.ready_at is None
    assert all(it.status == ItemStatus.QUEUED for it in recalled.items)
    assert all(it.started_at is None and it.ready_at is None for it in recalled.items)
    recall_events = [
        e for e in order_repo.events if e.event_type == EventType.RECALLED
    ]
    assert len(recall_events) == 1
    assert recall_events[0].payload.get("reason") == "missing_garnish"


async def test_recall_order_rejects_terminal_states(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    cancelled = order.model_copy(update={"status": OrderStatus.CANCELLED})
    order_repo.orders[order.id] = cancelled

    with pytest.raises(HTTPException) as exc:
        await order_service.recall_order(order.id)
    assert exc.value.status_code == 409


async def test_list_events_returns_events_for_order(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    events = await order_service.list_events(order_id=order.id)

    assert any(e.event_type == EventType.PLACED for e in events)
    assert all(e.order_id == order.id for e in events)


async def test_serve_order_transitions_to_served_with_timestamp_and_event(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    await order_service.update_item_status(order.items[0].id, ItemStatus.READY)
    await order_service.transition_order_to_ready(order.id)

    served = await order_service.serve_order(order.id)

    assert served.status == OrderStatus.SERVED
    assert served.served_at is not None
    assert all(it.status == ItemStatus.SERVED for it in served.items)
    served_events = [
        e for e in order_repo.events
        if e.event_type == EventType.STATUS_CHANGED
        and e.payload.get("status") == OrderStatus.SERVED.value
    ]
    assert len(served_events) == 1


async def test_serve_order_rejects_non_ready_orders(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    with pytest.raises(HTTPException) as exc:
        await order_service.serve_order(order.id)
    assert exc.value.status_code == 409


async def test_close_order_transitions_to_closed_from_served(
    order_service, seeded_table, seeded_menu_item
):
    order = await _make_placed_order(order_service, seeded_table, seeded_menu_item)
    await order_service.update_item_status(order.items[0].id, ItemStatus.READY)
    await order_service.transition_order_to_ready(order.id)
    await order_service.serve_order(order.id)

    closed = await order_service.close_order(order.id)
    assert closed.status == OrderStatus.CLOSED


async def test_close_order_rejects_draft_or_cancelled(
    order_service, order_repo, seeded_table, seeded_menu_item
):
    draft = await order_service.create_order(
        OrderCreate(table_id=seeded_table.id, customer_id=None)
    )
    with pytest.raises(HTTPException) as exc:
        await order_service.close_order(draft.id)
    assert exc.value.status_code == 409
