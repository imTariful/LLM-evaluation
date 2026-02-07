"""Initialize database tables on app startup."""
import logging
from sqlalchemy import inspect
from app.db.session import engine, async_engine
from app.db.base import Base

# Import ALL models to register them with Base.metadata
# IMPORTANT: Must import all models before calling create_all()
import app.models.prompt
import app.models.trace
import app.models.knowledge_base

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create all tables if they don't exist (synchronous)."""
    try:
        print(f"DEBUG: Initializing database tables. URL: {engine.url}")
        logger.info(f"📊 Creating tables. Database URL: {engine.url}")
        logger.info(f"📊 Registered tables in Base.metadata: {list(Base.metadata.tables.keys())}")
        
        # Create all tables defined in Base.metadata
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables initialized successfully (sync engine)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        raise


async def init_db_async() -> None:
    """Create all tables if they don't exist (async)."""
    try:
        logger.info(f"📊 Creating tables (async). Database URL: {async_engine.url}")
        logger.info(f"📊 Registered tables in Base.metadata: {list(Base.metadata.tables.keys())}")
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables initialized successfully (async engine)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database (async): {e}", exc_info=True)
        raise
