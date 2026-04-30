from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order as OrderORM
from app.models.order import OrderItem as OrderItemORM
from app.models.order_event import OrderEvent as OrderEventORM
from app.shared.models import EventType, Order, OrderEvent, OrderItem, OrderStatus


def _order_item_to_dto(orm: OrderItemORM) -> OrderItem:
    return OrderItem(
        id=orm.id,
        order_id=orm.order_id,
        menu_item_id=orm.menu_item_id,
        station_id=orm.station_id,
        quantity=orm.quantity,
        unit_price=orm.unit_price,
        status=orm.status,
        customizations=orm.customizations or {},
        allergy_notes=orm.allergy_notes,
        started_at=orm.started_at,
        ready_at=orm.ready_at,
    )


def _order_to_dto(orm: OrderORM) -> Order:
    return Order(
        id=orm.id,
        table_id=orm.table_id,
        customer_id=orm.customer_id,
        status=orm.status,
        subtotal=orm.subtotal,
        items=[_order_item_to_dto(it) for it in orm.items],
        created_at=orm.created_at,
        placed_at=orm.placed_at,
        ready_at=orm.ready_at,
        served_at=orm.served_at,
    )


def _order_event_to_dto(orm: OrderEventORM) -> OrderEvent:
    return OrderEvent(
        id=orm.id,
        order_id=orm.order_id,
        order_item_id=orm.order_item_id,
        actor_id=orm.actor_id,
        event_type=orm.event_type,
        payload=orm.payload or {},
        created_at=orm.created_at,
    )


class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(self) -> list[Order]:
        result = await self._session.execute(
            select(OrderORM)
            .options(selectinload(OrderORM.items))
            .order_by(OrderORM.created_at.desc())
        )
        return [_order_to_dto(o) for o in result.scalars().all()]

    async def get_order(self, order_id: UUID) -> Order | None:
        result = await self._session.execute(
            select(OrderORM)
            .where(OrderORM.id == order_id)
            .options(selectinload(OrderORM.items))
        )
        orm = result.scalar_one_or_none()
        return _order_to_dto(orm) if orm else None

    async def list_active_table_ids(
        self, active_statuses: Iterable[OrderStatus]
    ) -> set[UUID]:
        statuses = list(active_statuses)
        if not statuses:
            return set()
        result = await self._session.execute(
            select(OrderORM.table_id)
            .where(OrderORM.status.in_(statuses))
            .distinct()
        )
        return {row for row in result.scalars().all()}

    async def save_order(self, order: Order) -> None:
        result = await self._session.execute(
            select(OrderORM)
            .where(OrderORM.id == order.id)
            .options(selectinload(OrderORM.items))
        )
        orm = result.scalar_one_or_none()

        if orm is None:
            orm = OrderORM(
                id=order.id,
                table_id=order.table_id,
                customer_id=order.customer_id,
                status=order.status,
                subtotal=order.subtotal,
                placed_at=order.placed_at,
                ready_at=order.ready_at,
                served_at=order.served_at,
            )
            if order.created_at is not None:
                orm.created_at = order.created_at
            self._session.add(orm)
        else:
            orm.table_id = order.table_id
            orm.customer_id = order.customer_id
            orm.status = order.status
            orm.subtotal = order.subtotal
            orm.placed_at = order.placed_at
            orm.ready_at = order.ready_at
            orm.served_at = order.served_at

        existing_by_id = {it.id: it for it in orm.items}
        new_ids = {it.id for it in order.items}

        for old_id, old_orm in list(existing_by_id.items()):
            if old_id not in new_ids:
                orm.items.remove(old_orm)

        for item in order.items:
            if item.id in existing_by_id:
                ex = existing_by_id[item.id]
                ex.menu_item_id = item.menu_item_id
                ex.station_id = item.station_id
                ex.quantity = item.quantity
                ex.unit_price = item.unit_price
                ex.status = item.status
                ex.customizations = item.customizations or {}
                ex.allergy_notes = item.allergy_notes
                ex.started_at = item.started_at
                ex.ready_at = item.ready_at
            else:
                orm.items.append(
                    OrderItemORM(
                        id=item.id,
                        order_id=order.id,
                        menu_item_id=item.menu_item_id,
                        station_id=item.station_id,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        status=item.status,
                        customizations=item.customizations or {},
                        allergy_notes=item.allergy_notes,
                        started_at=item.started_at,
                        ready_at=item.ready_at,
                    )
                )

        await self._session.flush()

    async def add_event(
        self,
        order_id: UUID,
        event_type: EventType,
        order_item_id: UUID | None = None,
        payload: dict | None = None,
    ) -> OrderEvent:
        orm = OrderEventORM(
            id=uuid4(),
            order_id=order_id,
            order_item_id=order_item_id,
            event_type=event_type,
            payload=payload or {},
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return _order_event_to_dto(orm)

    async def list_events(
        self, order_id: UUID | None = None, since: str | None = None
    ) -> list[OrderEvent]:
        stmt = select(OrderEventORM).order_by(OrderEventORM.created_at)
        if order_id is not None:
            stmt = stmt.where(OrderEventORM.order_id == order_id)
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError as exc:
                raise ValueError(
                    f"`since` must be ISO-8601 datetime, got {since!r}"
                ) from exc
            stmt = stmt.where(OrderEventORM.created_at >= since_dt)
        result = await self._session.execute(stmt)
        return [_order_event_to_dto(e) for e in result.scalars()]
