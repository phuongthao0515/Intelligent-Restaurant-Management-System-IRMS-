from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import HTTPException, status

from app.shared.models import (
    ItemAvailabilityUpdate,
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
)

from app.shared.store import store


class MenuService:
    """Actor: menu manager — restaurant manager who configures
    menu items, prices, and availability.
    """

    def list_categories(self) -> list[MenuCategory]:
        return list(store.categories.values())

    def create_category(self, payload: MenuCategoryCreate) -> MenuCategory:
        category = MenuCategory(
            id=uuid.uuid4(),
            name=payload.name,
            display_order=payload.display_order,
        )
        store.categories[category.id] = category
        return category

    def update_category(
        self, category_id: UUID, payload: MenuCategoryUpdate
    ) -> MenuCategory:
        category = store.categories.get(category_id)
        if category is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
        updated = category.model_copy(update=payload.model_dump(exclude_none=True))
        store.categories[category_id] = updated

        return updated

    def list_menu_items(
        self, category_id: UUID | None = None, is_available: bool | None = None
    ) -> list[MenuItem]:
        items = list(store.menu_items.values())
        if category_id is not None:
            items = [item for item in items if item.category_id == category_id]
        if is_available is not None:
            items = [item for item in items if item.is_available == is_available]

        return items

    def create_menu_item(self, payload: MenuItemCreate) -> MenuItem:
        item = MenuItem(id=uuid.uuid4(), **payload.model_dump())
        store.menu_items[item.id] = item

        return item

    def get_menu_item(self, item_id: UUID) -> MenuItem:
        item = store.menu_items.get(item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Menu item not found")
        return item

    def update_menu_item(self, item_id: UUID, payload: MenuItemUpdate) -> MenuItem:
        item = self.get_menu_item(item_id)
        updated = item.model_copy(update=payload.model_dump(exclude_none=True))
        store.menu_items[item_id] = updated
        return updated

    def update_item_availability(
        self, item_id: UUID, payload: ItemAvailabilityUpdate
    ) -> MenuItem:
        item = self.get_menu_item(item_id)
        updated = item.model_copy(update={"is_available": payload.is_available})
        store.menu_items[item_id] = updated
        return updated


menu_service = MenuService()
