from functools import wraps
from contextlib import contextmanager
from .base import SessionLocal
from sqlalchemy.orm import session


@contextmanager
def session_scope() -> session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback
        raise
    finally:
        session.close()


def with_session(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with session_scope() as session:
            try:
                result = f(session, *args, **kwargs)
                session.commit()
                return result
            except:
                session.rollback()
                raise

    return wrapper


def get_db() -> SessionLocal:
    db = SessionLocal()
    return db
