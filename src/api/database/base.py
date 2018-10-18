from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import GOB_MANAGEMENT_DB

# Create database engine
db_uri = URL(**GOB_MANAGEMENT_DB)
engine = create_engine(db_uri)

# Declarative base model to create database tables and classes
Base = declarative_base()
Base.metadata.bind = engine  # Bind engine to metadata of the base class

# Create database session object
db_session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
Base.query = db_session.query_property()  # Used by graphql to execute queries
