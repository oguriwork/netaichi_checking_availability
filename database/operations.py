from __future__ import annotations

from sqlmodel import SQLModel

from config import settings

from .models import SessionFactory


class NetaichiDatabase:
    def __init__(self, echo=True):
        self.ECHO = echo
        self.sqlite = SessionFactory.sqlite(settings.DB_PATH, self.ECHO)

    def memory_sqlite(self):
        self.sqlite = SessionFactory.sqlite_memory(self.ECHO)
        return self

    def session(self):
        return self.sqlite.get()

    def create_tables(self):
        self.sqlite.create_tables()

    def drop_tables(self):
        self.sqlite.drop_tables()

    def drop_table(self, table: SQLModel):
        self.sqlite.drop_table(table)
