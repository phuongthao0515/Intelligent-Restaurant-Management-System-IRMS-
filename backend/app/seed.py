"""Seed the database with sample data to verify the schema."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import text

from app.database import async_session_maker, engine, init_db, BaseModel
from app.models.customer import Customer
from app.models.enums import (
    OrderEventType,
    OrderItemStatus,
    OrderPriority,
    OrderStatus,
    PaymentMethod,
    ReservationStatus,
    StaffRole,
    TableStatus,
)
from app.models.menu_item import MenuItem
from app.models.order import Order, OrderItem
from app.models.order_event import OrderEvent
from app.models.payment import Payment
from app.models.reservation import Reservation
from app.models.restaurant_table import RestaurantTable
from app.models.staff import Staff


async def seed() -> None:
    # Recreate all tables (drop + create) for a clean seed
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await init_db()

    async with async_session_maker() as session:
        # ── Staff ──────────────────────────────────────────────
        staff = [
            Staff(name="Alice Nguyen", phone_number="0901000001", role=StaffRole.MANAGER, password_hash="hashed_pw_1", is_active=True),
            Staff(name="Bob Tran", phone_number="0901000002", role=StaffRole.SERVER, password_hash="hashed_pw_2", is_active=True),
            Staff(name="Charlie Le", phone_number="0901000003", role=StaffRole.SERVER, password_hash="hashed_pw_3", is_active=True),
            Staff(name="Diana Pham", phone_number="0901000004", role=StaffRole.CHEF, password_hash="hashed_pw_4", is_active=True),
            Staff(name="Edward Vo", phone_number="0901000005", role=StaffRole.CHEF, password_hash="hashed_pw_5", is_active=True),
            Staff(name="Fiona Hoang", phone_number="0901000006", role=StaffRole.CASHIER, password_hash="hashed_pw_6", is_active=True),
            Staff(name="George Dao", phone_number="0901000007", role=StaffRole.HOST, password_hash="hashed_pw_7", is_active=True),
        ]
        session.add_all(staff)
        await session.flush()
        print(f"  + {len(staff)} staff members")

        # ── Tables ─────────────────────────────────────────────
        tables = [
            RestaurantTable(table_number=1, capacity=2, status=TableStatus.OCCUPIED),
            RestaurantTable(table_number=2, capacity=2, status=TableStatus.AVAILABLE),
            RestaurantTable(table_number=3, capacity=4, status=TableStatus.OCCUPIED),
            RestaurantTable(table_number=4, capacity=4, status=TableStatus.AVAILABLE),
            RestaurantTable(table_number=5, capacity=6, status=TableStatus.RESERVED),
            RestaurantTable(table_number=6, capacity=6, status=TableStatus.AVAILABLE),
            RestaurantTable(table_number=7, capacity=8, status=TableStatus.CLEANING),
            RestaurantTable(table_number=8, capacity=10, status=TableStatus.AVAILABLE),
        ]
        session.add_all(tables)
        await session.flush()
        print(f"  + {len(tables)} restaurant tables")

        # ── Customers ──────────────────────────────────────────
        customers = [
            Customer(name="Minh Anh", phone_number="0912000001"),
            Customer(name="Thu Ha", phone_number="0912000002"),
            Customer(name="Quoc Bao", phone_number="0912000003"),
            Customer(name="Lan Phuong", phone_number="0912000004"),
        ]
        session.add_all(customers)
        await session.flush()
        print(f"  + {len(customers)} customers")

        # ── Menu Items ─────────────────────────────────────────
        menu_items = [
            MenuItem(name="Pho Bo", category="Main", description="Traditional beef noodle soup", price=Decimal("55000"), station="kitchen", prep_time_min=12),
            MenuItem(name="Bun Cha", category="Main", description="Grilled pork with rice noodles", price=Decimal("50000"), station="grill", prep_time_min=15),
            MenuItem(name="Banh Mi Thit", category="Main", description="Vietnamese baguette with pork", price=Decimal("30000"), station="kitchen", prep_time_min=8),
            MenuItem(name="Com Tam", category="Main", description="Broken rice with grilled pork", price=Decimal("45000"), station="grill", prep_time_min=15),
            MenuItem(name="Goi Cuon", category="Appetizer", description="Fresh spring rolls", price=Decimal("35000"), station="cold", prep_time_min=10),
            MenuItem(name="Cha Gio", category="Appetizer", description="Fried spring rolls", price=Decimal("40000"), station="kitchen", prep_time_min=12),
            MenuItem(name="Ca Phe Sua Da", category="Beverage", description="Iced Vietnamese coffee", price=Decimal("25000"), station="bar", prep_time_min=3),
            MenuItem(name="Tra Da", category="Beverage", description="Iced tea", price=Decimal("5000"), station="bar", prep_time_min=1),
            MenuItem(name="Sinh To Bo", category="Beverage", description="Avocado smoothie", price=Decimal("30000"), station="bar", prep_time_min=5),
            MenuItem(name="Combo A", category="Combo", description="Pho + Iced coffee", price=Decimal("70000"), station="kitchen", prep_time_min=15, is_combo=True),
            MenuItem(name="Che Ba Mau", category="Dessert", description="Three-color dessert", price=Decimal("20000"), station="cold", prep_time_min=5),
            MenuItem(name="Banh Flan", category="Dessert", description="Caramel flan", price=Decimal("18000"), station="cold", prep_time_min=3, is_available=False),
        ]
        session.add_all(menu_items)
        await session.flush()
        print(f"  + {len(menu_items)} menu items")

        now = datetime.now(timezone.utc)

        # ── Order 1: served & paid (table 1, server Bob) ──────
        order1 = Order(
            server_id=staff[1].id,  # Bob
            table_id=tables[0].id,  # Table 1
            status=OrderStatus.CLOSED,
            priority=OrderPriority.NORMAL,
        )
        session.add(order1)
        await session.flush()

        oi1a = OrderItem(order_id=order1.id, menu_item_id=menu_items[0].id, assigned_chef_id=staff[3].id, quantity=1, unit_price=menu_items[0].price, status=OrderItemStatus.SERVED, station="kitchen")
        oi1b = OrderItem(order_id=order1.id, menu_item_id=menu_items[6].id, quantity=2, unit_price=menu_items[6].price, status=OrderItemStatus.SERVED, station="bar")
        session.add_all([oi1a, oi1b])
        await session.flush()

        session.add_all([
            OrderEvent(order_id=order1.id, actor_id=staff[1].id, event_type=OrderEventType.PLACED, payload=json.dumps({"items": 2})),
            OrderEvent(order_id=order1.id, actor_id=staff[3].id, event_type=OrderEventType.STATUS_CHANGED, payload=json.dumps({"from": "PLACED", "to": "IN_KITCHEN"})),
            OrderEvent(order_id=order1.id, actor_id=staff[1].id, event_type=OrderEventType.STATUS_CHANGED, payload=json.dumps({"from": "READY", "to": "SERVED"})),
        ])

        subtotal1 = menu_items[0].price + menu_items[6].price * 2  # 55000 + 50000
        session.add(Payment(
            order_id=order1.id, cashier_id=staff[5].id,  # Fiona
            subtotal=subtotal1, service_fee=Decimal("5000"), discount=Decimal("0"),
            total=subtotal1 + Decimal("5000"), tip=Decimal("10000"), method=PaymentMethod.CARD,
        ))
        print("  + order 1 (CLOSED) with 2 items, 3 events, 1 payment")

        # ── Order 2: in kitchen (table 3, server Charlie) ─────
        order2 = Order(
            server_id=staff[2].id,  # Charlie
            table_id=tables[2].id,  # Table 3
            status=OrderStatus.IN_KITCHEN,
            priority=OrderPriority.HIGH,
            special_instructions="No MSG please",
        )
        session.add(order2)
        await session.flush()

        oi2a = OrderItem(order_id=order2.id, menu_item_id=menu_items[1].id, assigned_chef_id=staff[4].id, quantity=2, unit_price=menu_items[1].price, status=OrderItemStatus.PREPARING, station="grill")
        oi2b = OrderItem(order_id=order2.id, menu_item_id=menu_items[4].id, assigned_chef_id=staff[3].id, quantity=1, unit_price=menu_items[4].price, status=OrderItemStatus.READY, station="cold")
        oi2c = OrderItem(order_id=order2.id, menu_item_id=menu_items[7].id, quantity=3, unit_price=menu_items[7].price, status=OrderItemStatus.SERVED, station="bar", notes_allergy="No sugar")
        session.add_all([oi2a, oi2b, oi2c])
        await session.flush()

        session.add_all([
            OrderEvent(order_id=order2.id, actor_id=staff[2].id, event_type=OrderEventType.PLACED),
            OrderEvent(order_id=order2.id, actor_id=staff[4].id, event_type=OrderEventType.STATUS_CHANGED, payload=json.dumps({"from": "PLACED", "to": "IN_KITCHEN"})),
            OrderEvent(order_id=order2.id, order_item_id=oi2b.id, actor_id=staff[3].id, event_type=OrderEventType.ITEM_STATUS_CHANGED, payload=json.dumps({"item": "Goi Cuon", "to": "READY"})),
        ])
        print("  + order 2 (IN_KITCHEN) with 3 items, 3 events")

        # ── Order 3: just placed / VIP (table 1, server Bob) ──
        order3 = Order(
            server_id=staff[1].id,
            table_id=tables[0].id,
            status=OrderStatus.PLACED,
            priority=OrderPriority.VIP,
            special_instructions="Birthday celebration – candle on dessert",
        )
        session.add(order3)
        await session.flush()

        oi3a = OrderItem(order_id=order3.id, menu_item_id=menu_items[9].id, quantity=2, unit_price=menu_items[9].price, status=OrderItemStatus.QUEUED, station="kitchen")
        oi3b = OrderItem(order_id=order3.id, menu_item_id=menu_items[10].id, quantity=2, unit_price=menu_items[10].price, status=OrderItemStatus.QUEUED, station="cold")
        session.add_all([oi3a, oi3b])
        await session.flush()

        session.add(OrderEvent(order_id=order3.id, actor_id=staff[1].id, event_type=OrderEventType.PLACED))
        print("  + order 3 (PLACED/VIP) with 2 items, 1 event")

        # ── Reservations ───────────────────────────────────────
        reservations = [
            Reservation(customer_id=customers[0].id, table_id=tables[4].id, status=ReservationStatus.CONFIRMED, party_size=5, reserved_at=now + timedelta(hours=2), notes="Anniversary dinner"),
            Reservation(customer_id=customers[1].id, table_id=tables[3].id, status=ReservationStatus.PENDING, party_size=3, reserved_at=now + timedelta(hours=4)),
            Reservation(customer_id=customers[2].id, table_id=tables[7].id, status=ReservationStatus.CANCELLED, party_size=8, reserved_at=now - timedelta(days=1), notes="Cancelled – rescheduling"),
            Reservation(customer_id=customers[3].id, table_id=tables[5].id, status=ReservationStatus.SEATED, party_size=4, reserved_at=now - timedelta(minutes=30)),
        ]
        session.add_all(reservations)
        print(f"  + {len(reservations)} reservations")

        await session.commit()

    # ── Verify ─────────────────────────────────────────────────
    print("\n== Verification ==")
    async with async_session_maker() as session:
        result = await session.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )
        table_names = [row[0] for row in result.all()]
        print(f"  Tables ({len(table_names)}): {', '.join(table_names)}")

        for tbl in table_names:
            count = (await session.execute(text(f'SELECT count(*) FROM "{tbl}"'))).scalar()
            print(f"    {tbl}: {count} rows")

    await engine.dispose()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
