from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.menu.repositories import MenuRepository
from app.shared.models import (
    ItemAvailabilityUpdate,
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
)


class MenuService:
    def __init__(self, menus: MenuRepository):
        self._menus = menus

    async def list_categories(self) -> list[MenuCategory]:
        return await self._menus.list_categories()

    async def create_category(self, payload: MenuCategoryCreate) -> MenuCategory:
        category = MenuCategory(
            id=uuid.uuid4(),
            name=payload.name,
            display_order=payload.display_order,
        )
        await self._menus.save_category(category)
        return category

    async def update_category(
        self, category_id: UUID, payload: MenuCategoryUpdate
    ) -> MenuCategory:
        category = await self._menus.get_category(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        updated = category.model_copy(update=payload.model_dump(exclude_none=True))
        await self._menus.save_category(updated)
        return updated

    async def list_menu_items(
        self, category_id: UUID | None = None, is_available: bool | None = None
    ) -> list[MenuItem]:
        items = await self._menus.list_items()
        if category_id is not None:
            items = [item for item in items if item.category_id == category_id]
        if is_available is not None:
            items = [item for item in items if item.is_available == is_available]
        return items

    async def create_menu_item(self, payload: MenuItemCreate) -> MenuItem:
        item = MenuItem(id=uuid.uuid4(), **payload.model_dump())
        await self._menus.save_item(item)
        return item

    async def get_menu_item(self, item_id: UUID) -> MenuItem:
        item = await self._menus.get_item(item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Menu item not found")
        return item

    async def update_menu_item(self, item_id: UUID, payload: MenuItemUpdate) -> MenuItem:
        item = await self.get_menu_item(item_id)
        updated = item.model_copy(update=payload.model_dump(exclude_none=True))
        await self._menus.save_item(updated)
        return updated

    async def update_item_availability(
        self, item_id: UUID, payload: ItemAvailabilityUpdate
    ) -> MenuItem:
        item = await self.get_menu_item(item_id)
        updated = item.model_copy(update={"is_available": payload.is_available})
        await self._menus.save_item(updated)
        return updated
