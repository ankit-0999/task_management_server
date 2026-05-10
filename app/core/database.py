from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Use lazy engine initialization — Vercel serverless functions import modules
# at cold-start. If DATABASE_URL is missing, the error will be surfaced per-request
# rather than crashing the whole function on import.
def _get_engine():
    if not settings.SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        # Vercel serverless: use NullPool to avoid connection reuse across invocations
        poolclass=__import__('sqlalchemy.pool', fromlist=['NullPool']).NullPool,
    )

engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
