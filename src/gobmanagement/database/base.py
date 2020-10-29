from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import scoped_session, sessionmaker

from gobcore.model.sa.management import Base

from .config import GOB_MANAGEMENT_DB

# Create database engine
db_uri = URL(**GOB_MANAGEMENT_DB)
engine = create_engine(db_uri)

# Declarative base model to create database tables and classes
Base.metadata.bind = engine  # Bind engine to metadata of the base class

# Create database session object
maker = sessionmaker(bind=engine, expire_on_commit=False, autocommit=True)
Session = scoped_session(maker)
db_session = Session  # should not be used
Base.query = db_session.query_property()  # Used by graphql to execute queries


@contextmanager
def session_scope(readonly=False, backend=Session):
    session = backend()
    if readonly:
        session.flush = lambda: None
    try:
        yield session
        if not readonly:
            session.commit()
    except Exception:
        session.rollback()
        raise
    session.close()
