from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    school = Column(String, nullable=False)


def create_tenant_engine(
    tenant_name: str,
    pool_size: int = 1,
    max_overflow: int = 0,
    pool_timeout: int = 30,
):
    """
    Create a tenant-specific engine.

    For these demos, SQLite is used as a stand-in for PostgreSQL.
    The connection pool settings are the key part of the demonstration.
    """
    database_url = f'sqlite:///./{tenant_name}.sqlite'
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        connect_args={"check_same_thread": False},
        echo=False,
    )


def initialize_tenant_database(engine):
    """Create tables for a tenant if they do not already exist."""
    Base.metadata.create_all(engine)


def get_student_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
