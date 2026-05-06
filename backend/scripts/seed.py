from __future__ import annotations

import asyncio
from decimal import Decimal

import structlog
from sqlalchemy import select

from app.database import async_session_maker
from app.models import (
    Customer,
    MenuCategory,
    MenuItem,
    RestaurantTable,
    Staff,
    Station,
)
from app.models.enums import StaffRole, TableStatus

logger = structlog.get_logger(__name__)


CATEGORY_DATA: list[tuple[str, int]] = [
    ("APPETIZER", 1),
    ("MAIN", 2),
    ("DESSERT", 3),
    ("BEVERAGE", 4),
]

STATION_DATA: list[tuple[str, bool]] = [
    ("GRILL", True),
    ("COLD", True),
    ("BAR", True),
    ("FRYER", True),
]

STAFF_DATA: list[tuple[str, str, StaffRole]] = [
    ("Alice Nguyen", "+84900000001", StaffRole.MANAGER),
    ("Bob Tran", "+84900000002", StaffRole.SERVER),
    ("Carol Le", "+84900000003", StaffRole.SERVER),
    ("David Pham", "+84900000004", StaffRole.CHEF),
    ("Eve Vu", "+84900000005", StaffRole.CHEF),
    ("Frank Hoang", "+84900000006", StaffRole.CASHIER),
    ("Grace Ly", "+84900000007", StaffRole.HOST),
]

TABLE_DATA: list[tuple[int, int]] = [
    (1, 2),
    (2, 2),
    (3, 4),
    (4, 4),
    (5, 6),
]

CUSTOMER_DATA: list[tuple[str, str]] = [
    ("Hannah Kim", "+84910000001"),
    ("Ian Bui", "+84910000002"),
    ("Jenny Do", "+84910000003"),
]

# (name, category_name, description, price, station_name, is_combo, prep_time_min)
MENU_DATA: list[tuple[str, str, str, Decimal, str, bool, int]] = [
    ("Caesar Salad", "APPETIZER", "Romaine, parmesan, croutons", Decimal("8.00"), "COLD", False, 2),
    ("Bruschetta", "APPETIZER", "Toasted bread, tomato, basil", Decimal("7.00"), "COLD", False, 2),
    ("Chicken Wings", "APPETIZER", "Smoked, buffalo glaze", Decimal("10.00"), "GRILL", False, 3),
    ("French Fries", "APPETIZER", "Crispy skin-on fries", Decimal("5.00"), "FRYER", False, 2),
    ("Ribeye Steak", "MAIN", "12oz prime ribeye, garlic butter", Decimal("32.00"), "GRILL", False, 10),
    ("Grilled Salmon", "MAIN", "Atlantic salmon, lemon herb", Decimal("26.00"), "GRILL", False, 10),
    ("Margherita Pizza", "MAIN", "San Marzano, mozzarella, basil", Decimal("18.00"), "GRILL", False, 5),
    ("Beef Burger", "MAIN", "Angus patty, cheddar, brioche", Decimal("16.00"), "GRILL", False, 2),
    ("Steak & Wine Combo", "MAIN", "Ribeye + house red pairing", Decimal("42.00"), "GRILL", True, 5),
    ("Tiramisu", "DESSERT", "Classic Italian, mascarpone", Decimal("9.00"), "COLD", False, 3),
    ("Mojito", "BEVERAGE", "White rum, lime, mint", Decimal("11.00"), "BAR", False, 4),
    ("House Red", "BEVERAGE", "Glass of house red wine", Decimal("12.00"), "BAR", False, 2),
]


async def seed() -> None:
    async with async_session_maker() as db:
        existing = await db.scalar(select(MenuCategory).limit(1))
        if existing is not None:
            logger.info("seed.skip", reason="data already seeded")
            return

        categories = [
            MenuCategory(name=name, display_order=order)
            for (name, order) in CATEGORY_DATA
        ]
        stations = [
            Station(name=name, is_active=is_active)
            for (name, is_active) in STATION_DATA
        ]
        staff = [
            Staff(
                name=name,
                phone_number=phone,
                role=role,
                password_hash=f"$stub${name}",
                is_active=True,
            )
            for (name, phone, role) in STAFF_DATA
        ]
        tables = [
            RestaurantTable(
                number=number,
                seats=seats,
                status=TableStatus.AVAILABLE,
            )
            for (number, seats) in TABLE_DATA
        ]
        customers = [
            Customer(name=name, phone_number=phone)
            for (name, phone) in CUSTOMER_DATA
        ]

        db.add_all(categories)
        db.add_all(stations)
        db.add_all(staff)
        db.add_all(tables)
        db.add_all(customers)
        await db.flush()

        categories_by_name = {c.name: c for c in categories}
        stations_by_name = {s.name: s for s in stations}

        menu_items = [
            MenuItem(
                name=name,
                category_id=categories_by_name[category_name].id,
                station_id=stations_by_name[station_name].id,
                description=description,
                price=price,
                is_combo=is_combo,
                prep_time_min=prep_time_min,
                is_available=True,
                customization_schema={},
            )
            for (
                name,
                category_name,
                description,
                price,
                station_name,
                is_combo,
                prep_time_min,
            ) in MENU_DATA
        ]

        db.add_all(menu_items)
        await db.commit()

        logger.info(
            "seed.complete",
            categories=len(categories),
            stations=len(stations),
            staff=len(staff),
            tables=len(tables),
            customers=len(customers),
            menu_items=len(menu_items),
        )


if __name__ == "__main__":
    asyncio.run(seed())
