from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import config

engine = create_async_engine(
    url=config.database_url.get_secret_value(),
    echo=True, future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получает сессию для работы с базой данных."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
