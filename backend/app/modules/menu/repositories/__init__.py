from app.modules.menu.repositories.protocols import MenuRepository
from app.modules.menu.repositories.sqlalchemy import SqlAlchemyMenuRepository

__all__ = [
    "MenuRepository",
    "SqlAlchemyMenuRepository",
]
