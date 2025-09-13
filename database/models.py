from datetime import datetime
from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typing import Optional


class M_Account(SQLModel, table=True):
    name: str
    id: str = Field(primary_key=True)
    password: str
    expiration_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    account_group: Optional[str] = None
    is_master: bool = Field(default=False)
    is_use: bool = Field(default=True)


class T_LotteryEntryRecord(SQLModel, table=True):
    value: str
    date: datetime
    start: int
    end: int
    result: str = Field(default="未定")
    amount: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    account_group: str
    id: Optional[int] = Field(default=None, primary_key=True)  # 主キー制約


class SessionFactory:
    engine: Engine

    @classmethod
    def sqlite(cls, name, echo=True):
        this = SessionFactory()
        this.engine = create_engine(
            f"sqlite:///{name}.sqlite",
            echo=echo,
            connect_args={
                "check_same_thread": False,
            },
        )
        return this

    @classmethod
    def sqlite_memory(cls, echo=True):
        this = SessionFactory()
        this.engine = create_engine(
            "sqlite://",
            echo=echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # in-memoryの使用
        )
        return this

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def drop_tables(self):
        SQLModel.metadata.drop_all(self.engine)

    def drop_table(self, model_class):
        model_class.__table__.drop(self.engine)

    def get(self) -> Session:
        return Session(self.engine)
