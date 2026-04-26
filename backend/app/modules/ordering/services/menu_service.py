from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.modules.ordering.repositories import (
    InMemoryMenuRepository,
    MenuRepository,
)
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
    """Actor: menu manager — restaurant manager who configures
    menu items, prices, and availability.
    """

    def __init__(self, menus: MenuRepository):
        self._menus = menus

    def list_categories(self) -> list[MenuCategory]:
        return self._menus.list_categories()

    def create_category(self, payload: MenuCategoryCreate) -> MenuCategory:
        category = MenuCategory(
            id=uuid.uuid4(),
            name=payload.name,
            display_order=payload.display_order,
        )
        self._menus.save_category(category)
        return category

    def update_category(
        self, category_id: UUID, payload: MenuCategoryUpdate
    ) -> MenuCategory:
        category = self._menus.get_category(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        updated = category.model_copy(update=payload.model_dump(exclude_none=True))
        self._menus.save_category(updated)
        return updated

    def list_menu_items(
        self, category_id: UUID | None = None, is_available: bool | None = None
    ) -> list[MenuItem]:
        items = self._menus.list_items()
        if category_id is not None:
            items = [item for item in items if item.category_id == category_id]
        if is_available is not None:
            items = [item for item in items if item.is_available == is_available]
        return items

    def create_menu_item(self, payload: MenuItemCreate) -> MenuItem:
        item = MenuItem(id=uuid.uuid4(), **payload.model_dump())
        self._menus.save_item(item)
        return item

    def get_menu_item(self, item_id: UUID) -> MenuItem:
        item = self._menus.get_item(item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Menu item not found")
        return item

    def update_menu_item(self, item_id: UUID, payload: MenuItemUpdate) -> MenuItem:
        item = self.get_menu_item(item_id)
        updated = item.model_copy(update=payload.model_dump(exclude_none=True))
        self._menus.save_item(updated)
        return updated

    def update_item_availability(
        self, item_id: UUID, payload: ItemAvailabilityUpdate
    ) -> MenuItem:
        item = self.get_menu_item(item_id)
        updated = item.model_copy(update={"is_available": payload.is_available})
        self._menus.save_item(updated)
        return updated


menu_service = MenuService(InMemoryMenuRepository())
