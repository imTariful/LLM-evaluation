from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

# Synchronous engine for compatibility (used by Alembic, etc.)
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine for async operations
# Convert sqlite:// to sqlite+aiosqlite:// for async support
database_url = settings.SQLALCHEMY_DATABASE_URI
if database_url.startswith("sqlite://"):
    # For async SQLite, use sqlite+aiosqlite
    # If it starts with sqlite:///, replace with sqlite+aiosqlite:///
    if database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    else:
        database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif database_url.startswith("postgresql://"):
    # For async PostgreSQL, use postgresql+asyncpg
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    database_url,
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Get async database session for dependency injection"""
    async with async_session_maker() as session:
        yield session
