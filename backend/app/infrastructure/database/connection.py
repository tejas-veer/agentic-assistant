from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os

database_url = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./agentic_assist.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

is_sqlite = database_url.startswith("sqlite")
is_debug = os.environ.get("DEBUG", "true").lower() == "true"

engine_kwargs = {
    "echo": is_debug,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 10
    })

engine = create_async_engine(database_url, **engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

