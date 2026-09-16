import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


def get_database_url() -> str:
    """Збирає DSN зі змінних оточення (.env)."""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"


engine = create_engine(get_database_url(), echo=False)

DBSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

@contextmanager
def session_scope() -> Session:

    session = DBSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
