from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import TableStatus
from app.models.menu_category import MenuCategory as MenuCategoryORM
from app.models.menu_item import MenuItem as MenuItemORM
from app.models.order import Order as OrderORM
from app.models.order import OrderItem as OrderItemORM
from app.models.order_event import OrderEvent as OrderEventORM
from app.models.restaurant_table import RestaurantTable as RestaurantTableORM
from app.shared.models import (
    EventType,
    MenuCategory,
    MenuItem,
    Order,
    OrderEvent,
    OrderItem,
    Table,
)


# ---------------------------------------------------------------------------
# Private DTO converters: ORM -> Pydantic
# Repositories return Pydantic at the boundary so services never touch ORM.
# ---------------------------------------------------------------------------
def _table_to_dto(orm: RestaurantTableORM) -> Table:
    return Table(
        id=orm.id,
        number=orm.number,
        seats=orm.seats,
        is_occupied=(orm.status == TableStatus.OCCUPIED),
    )


def _menu_category_to_dto(orm: MenuCategoryORM) -> MenuCategory:
    return MenuCategory(
        id=orm.id,
        name=orm.name,
        display_order=orm.display_order,
    )


def _menu_item_to_dto(orm: MenuItemORM) -> MenuItem:
    return MenuItem(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        price=orm.price,
        category_id=orm.category_id,
        station_id=orm.station_id,
        prep_time_min=orm.prep_time_min,
        is_available=orm.is_available,
        is_combo=orm.is_combo,
        customization_schema=orm.customization_schema or {},
    )


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


# ---------------------------------------------------------------------------
# Concrete adapters
# ---------------------------------------------------------------------------
class SqlAlchemyTableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_tables(self) -> list[Table]:
        result = await self._session.execute(select(RestaurantTableORM))
        return [_table_to_dto(t) for t in result.scalars().all()]

    async def get_table(self, table_id: UUID) -> Table | None:
        result = await self._session.execute(
            select(RestaurantTableORM).where(RestaurantTableORM.id == table_id)
        )
        orm = result.scalar_one_or_none()
        return _table_to_dto(orm) if orm else None


class SqlAlchemyMenuRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_categories(self) -> list[MenuCategory]:
        result = await self._session.execute(select(MenuCategoryORM))
        return [_menu_category_to_dto(c) for c in result.scalars().all()]

    async def get_category(self, category_id: UUID) -> MenuCategory | None:
        result = await self._session.execute(
            select(MenuCategoryORM).where(MenuCategoryORM.id == category_id)
        )
        orm = result.scalar_one_or_none()
        return _menu_category_to_dto(orm) if orm else None

    async def save_category(self, category: MenuCategory) -> None:
        result = await self._session.execute(
            select(MenuCategoryORM).where(MenuCategoryORM.id == category.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            orm = MenuCategoryORM(
                id=category.id,
                name=category.name,
                display_order=category.display_order,
            )
            self._session.add(orm)
        else:
            orm.name = category.name
            orm.display_order = category.display_order
        await self._session.flush()

    async def list_items(self) -> list[MenuItem]:
        result = await self._session.execute(select(MenuItemORM))
        return [_menu_item_to_dto(i) for i in result.scalars().all()]

    async def get_item(self, item_id: UUID) -> MenuItem | None:
        result = await self._session.execute(
            select(MenuItemORM).where(MenuItemORM.id == item_id)
        )
        orm = result.scalar_one_or_none()
        return _menu_item_to_dto(orm) if orm else None

    async def save_item(self, item: MenuItem) -> None:
        result = await self._session.execute(
            select(MenuItemORM).where(MenuItemORM.id == item.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            orm = MenuItemORM(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                category_id=item.category_id,
                station_id=item.station_id,
                prep_time_min=item.prep_time_min if item.prep_time_min is not None else 10,
                is_available=item.is_available,
                is_combo=item.is_combo,
                customization_schema=item.customization_schema or {},
            )
            self._session.add(orm)
        else:
            orm.name = item.name
            orm.description = item.description
            orm.price = item.price
            orm.category_id = item.category_id
            orm.station_id = item.station_id
            if item.prep_time_min is not None:
                orm.prep_time_min = item.prep_time_min
            orm.is_available = item.is_available
            orm.is_combo = item.is_combo
            orm.customization_schema = item.customization_schema or {}
        await self._session.flush()


class SqlAlchemyOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_orders(self) -> list[Order]:
        result = await self._session.execute(
            select(OrderORM).options(selectinload(OrderORM.items))
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

    async def save_order(self, order: Order) -> None:
        # Upsert: fetch (with items eagerly loaded), then add or update.
        result = await self._session.execute(
            select(OrderORM)
            .where(OrderORM.id == order.id)
            .options(selectinload(OrderORM.items))
        )
        orm = result.scalar_one_or_none()

        if orm is None:
            # CREATE
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
            # UPDATE: do not touch created_at (immutable after creation)
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
        result = await self._session.execute(stmt)
        events = [_order_event_to_dto(e) for e in result.scalars()]
        if since is not None:
            events = [e for e in events if e.created_at.isoformat() >= since]
        return events
