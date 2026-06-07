import sys
import os

# Add parent dir to sys path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from bot.config import DB_URL
from bot.database.models import Base

# Create async engine
engine = create_async_engine(DB_URL, echo=False)

# Create session maker
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

from sqlalchemy import text

async def init_db():
    """Initialize database and create tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Gracefully add the new 'status' column if it doesn't exist
        try:
            await conn.execute(text("ALTER TABLE clients ADD COLUMN status VARCHAR NOT NULL DEFAULT '🆕 Новый'"))
        except Exception as e:
            # Column already exists or another DB error
            pass

async def get_session() -> AsyncSession:
    """Get async session"""
    async with async_session() as session:
        yield session
