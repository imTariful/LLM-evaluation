import logging
import asyncio
from sqlalchemy import text
from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        db = SessionLocal()
        # Test connection
        db.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
        
        # Here we would typically run alembic upgrade head
        # In a real startup script, we might call:
        # import alembic.config
        # alembic.config.main(argv=["upgrade", "head"])
        
        logger.info("Initialization complete.")
    except Exception as e:
        logger.error(f"Database Initialization Failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    print("Run `alembic upgrade head` to apply migrations.")
    init_db()
