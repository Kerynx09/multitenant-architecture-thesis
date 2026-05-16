import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))
from core import create_tenant_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    grade = Column(String, nullable=False)
    school = Column(String, nullable=False)


def create_sample_data(engine, school_name):
    """
    Ensure the tenant table exists and add a small set of sample records.
    This step is about data setup, not pool behavior.
    """
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all([
        Student(name='Alice Johnson', email='alice@school.com', grade='A', school=school_name),
        Student(name='Brian Lee', email='brian@school.com', grade='B', school=school_name),
    ])
    session.commit()
    session.close()


def request_connection(thread_id, engine, results):
    """
    Each thread tries to acquire a connection at the same time.
    If the pool has no free connection and overflow is disabled,
    SQLAlchemy raises a timeout error.
    """
    try:
        with engine.connect() as conn:
            print(f'  thread {thread_id}: acquired connection')
            time.sleep(4)
            print(f'  thread {thread_id}: released connection')
            results.append((thread_id, 'success', None))
    except Exception as exc:
        results.append((thread_id, 'error', str(exc)))
        print(f'  thread {thread_id}: failed to acquire connection: {exc}')


def simulate_connection_exhaustion(tenant_name):
    engine = create_tenant_engine(
        tenant_name,
        pool_size=1,
        max_overflow=0,
        pool_timeout=5,
    )
    create_sample_data(engine, tenant_name)

    print(f'Running concurrent exhaustion simulation for tenant `{tenant_name}`')
    results = []
    threads = []

    for i in range(4):
        thread = threading.Thread(target=request_connection, args=(i + 1, engine, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    success_count = sum(1 for _, status, _ in results if status == 'success')
    error_count = sum(1 for _, status, _ in results if status == 'error')

    print('\nSummary:')
    print('  total thread attempts =', len(results))
    print('  successes =', success_count)
    print('  errors =', error_count)
    if error_count:
        sample_error = next(err for _, status, err in results if status == 'error')
        print('  sample error =', sample_error)


if __name__ == '__main__':
    simulate_connection_exhaustion('school_oakwood')
