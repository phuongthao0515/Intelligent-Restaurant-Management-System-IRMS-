from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.deps import get_menu_service
from app.modules.menu.services.menu_service import MenuService
from app.shared.models import (
    ItemAvailabilityUpdate,
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
)


router = APIRouter()


@router.get("/menu/categories", tags=["menu"], response_model=list[MenuCategory])
async def list_menu_categories(
    service: MenuService = Depends(get_menu_service),
) -> list[MenuCategory]:
    return await service.list_categories()


@router.post(
    "/menu/categories",
    tags=["menu"],
    status_code=status.HTTP_201_CREATED,
    response_model=MenuCategory,
)
async def create_menu_category(
    payload: MenuCategoryCreate,
    service: MenuService = Depends(get_menu_service),
) -> MenuCategory:
    return await service.create_category(payload)


@router.patch(
    "/menu/categories/{category_id}", tags=["menu"], response_model=MenuCategory
)
async def update_menu_category(
    category_id: UUID,
    payload: MenuCategoryUpdate,
    service: MenuService = Depends(get_menu_service),
) -> MenuCategory:
    return await service.update_category(category_id, payload)


@router.get("/menu/items", tags=["menu"], response_model=list[MenuItem])
async def list_menu_items(
    category_id: UUID | None = None,
    is_available: bool | None = None,
    service: MenuService = Depends(get_menu_service),
) -> list[MenuItem]:
    return await service.list_menu_items(category_id, is_available)


@router.post(
    "/menu/items",
    tags=["menu"],
    status_code=status.HTTP_201_CREATED,
    response_model=MenuItem,
)
async def create_menu_item(
    payload: MenuItemCreate,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.create_menu_item(payload)


@router.get("/menu/items/{item_id}", tags=["menu"], response_model=MenuItem)
async def get_menu_item(
    item_id: UUID,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.get_menu_item(item_id)


@router.patch("/menu/items/{item_id}", tags=["menu"], response_model=MenuItem)
async def update_menu_item(
    item_id: UUID,
    payload: MenuItemUpdate,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.update_menu_item(item_id, payload)


@router.patch(
    "/menu/items/{item_id}/availability", tags=["menu"], response_model=MenuItem
)
async def update_item_availability(
    item_id: UUID,
    payload: ItemAvailabilityUpdate,
    service: MenuService = Depends(get_menu_service),
) -> MenuItem:
    return await service.update_item_availability(item_id, payload)
