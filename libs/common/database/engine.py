from common.database.config import db_config
from common.database.logger import setup_alchemy_logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


setup_alchemy_logging()


engine = create_async_engine(db_config.url, pool_size=5, max_overflow=10)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
