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
    """Actor: chef"""
    
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
    
    
    
        