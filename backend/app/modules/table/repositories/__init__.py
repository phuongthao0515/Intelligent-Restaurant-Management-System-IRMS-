from app.modules.table.repositories.protocols import TableRepository
from app.modules.table.repositories.sqlalchemy import SqlAlchemyTableRepository

__all__ = [
    "TableRepository",
    "SqlAlchemyTableRepository",
]
