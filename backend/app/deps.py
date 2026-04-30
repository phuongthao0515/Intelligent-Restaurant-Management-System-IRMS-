from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.modules.kds.repositories import (
    SqlAlchemyStationRepository,
    StationRepository,
)
from app.modules.kds.service import KdsService
from app.modules.menu.repositories import (
    MenuRepository,
    SqlAlchemyMenuRepository,
)
from app.modules.menu.services.menu_service import MenuService
from app.modules.ordering.repositories import (
    OrderRepository,
    SqlAlchemyOrderRepository,
)
from app.modules.ordering.services.order_service import OrderService
from app.modules.table.repositories import (
    SqlAlchemyTableRepository,
    TableRepository,
)
from app.modules.table.services.table_service import TableService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_menu_repository(
    session: AsyncSession = Depends(get_session),
) -> MenuRepository:
    return SqlAlchemyMenuRepository(session)


def get_table_repository(
    session: AsyncSession = Depends(get_session),
) -> TableRepository:
    return SqlAlchemyTableRepository(session)


def get_order_repository(
    session: AsyncSession = Depends(get_session),
) -> OrderRepository:
    return SqlAlchemyOrderRepository(session)


def get_station_repository(
    session: AsyncSession = Depends(get_session),
) -> StationRepository:
    return SqlAlchemyStationRepository(session)


def get_menu_service(
    menus: MenuRepository = Depends(get_menu_repository),
) -> MenuService:
    return MenuService(menus)


def get_table_service(
    tables: TableRepository = Depends(get_table_repository),
    orders: OrderRepository = Depends(get_order_repository),
) -> TableService:
    return TableService(tables, orders)


def get_order_service(
    orders: OrderRepository = Depends(get_order_repository),
    menus: MenuService = Depends(get_menu_service),
    tables: TableService = Depends(get_table_service),
) -> OrderService:
    return OrderService(orders=orders, menus=menus, tables=tables)


def get_kds_service(
    stations: StationRepository = Depends(get_station_repository),
    orders: OrderService = Depends(get_order_service),
    tables: TableService = Depends(get_table_service),
) -> KdsService:
    return KdsService(stations=stations, orders=orders, tables=tables)
