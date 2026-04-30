from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.menu_category import MenuCategory as MenuCategoryORM
from app.models.menu_item import MenuItem as MenuItemORM
from app.shared.models import MenuCategory, MenuItem


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
