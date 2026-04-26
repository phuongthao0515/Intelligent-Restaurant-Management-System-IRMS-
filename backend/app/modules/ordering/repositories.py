from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.shared.models import (
    EventType,
    MenuCategory, 
    MenuItem, 
    Order, 
    OrderEvent,
    Table,
)

from app.shared.store import store

class TableRepository(Protocol):
    def list_tables(self) -> list[Table]:
        return list(store.tables.values())
    def get_table(self, table_id: UUID) -> Table | None:
        return store.tables.get(table_id)
    
class OrderRepository(Protocol):
    """Persistence port for orders and order events."""

    def list_orders(self) -> list[Order]:
        return list(store.orders.values())

    def get_order(self, order_id: UUID) -> Order | None:
        return store.orders.get(order_id)

    def save_order(self, order: Order) -> None:
        store.orders[order.id] = order

    def add_event(
        self,
        order_id: UUID,
        event_type: EventType,
        order_item_id: UUID | None = None,
        payload: dict | None = None,
    ) -> OrderEvent:
        return store.add_event(order_id, event_type, order_item_id, payload)


class MenuRepository(Protocol):
    def list_categories(self)->list[MenuCategory]:
        return list(store.categories.values())
    
    def get_category(self, category_id: UUID) -> MenuCategory | None:
        return store.categories.get(category_id)
    
    def save_category(self, category: MenuCategory) -> None:
        store.categories[category.id] = category
        
    def list_items(self)->list[MenuItem]:
        return list(store.menu_items.values())
    
    def get_item(self, item_id: UUID)-> MenuItem|None:
        return store.menu_items.get(item_id)
    
    def save_item(self, item: MenuItem)->None:
        store.menu_items[item.id] = item

class InMemoryMenuRepository:
    def list_categories(self)->list[MenuCategory]:
        return list(store.categories.values())
    def get_category(self, category_id: UUID)->MenuCategory|None:
        return store.categories.get(category_id)
    
    def save_category(self, category: MenuCategory)->None:
        store.categories[category.id] = category
        
    def list_items(self) -> list[MenuItem]:
        return list(store.menu_items.values())
    
    def get_item(self, item_id: UUID)->MenuItem|None:
        return store.menu_items.get(item_id)
    
    def save_item(self, item: MenuItem) -> None:
        store.menu_items[item.id] = item

class InMemoryTableRepository:
    """Reads the in-process store"""
    def list_tables(self)-> list[Table]:
        return list(store.tables.values())
    
    def get_table(self, table_id: UUID) -> Table|None:
        return store.tables.get(table_id)
    
class InMemoryOrderRepository:
    def list_orders(self)-> list[Order]:
        return list(store.orders.values())
    
    def get_order(self, order_id:UUID)->Order|None:
        return store.orders.get(order_id)
    
    def save_order(self, order:Order)->None:
        store.orders[order.id] = order
        
    def add_event(self, order_id: UUID, event_type: EventType, order_item_id: UUID| None=None, payload: dict|None=None,)->OrderEvent:
        return store.add_event(order_id, event_type, order_item_id, payload)