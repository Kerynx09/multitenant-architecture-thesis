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
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all([
        Student(name='Alice Johnson', email='alice@school.com', grade='A', school=school_name),
        Student(name='Brian Lee', email='brian@school.com', grade='B', school=school_name),
    ])
    session.commit()
    session.close()


def leaky_request(thread_id, engine, results):
    """
    Simulate a request that acquires a connection and never returns it.
    This behavior models a bug where the application fails to close a connection.
    """
    try:
        conn = engine.connect()
        print(f'  thread {thread_id}: acquired and leaked connection')
        results.append((thread_id, 'leaked', None))
        time.sleep(8)
        # Intentionally not closing the connection to simulate a leak.
    except Exception as exc:
        results.append((thread_id, 'error', str(exc)))
        print(f'  thread {thread_id}: failed to acquire connection: {exc}')


def normal_request(thread_id, engine, results):
    """
    Simulate a healthy request that tries to get a connection normally.
    In the presence of leaked connections, this request will fail.
    """
    try:
        with engine.connect() as conn:
            print(f'  thread {thread_id}: acquired connection successfully')
            time.sleep(1)
            results.append((thread_id, 'success', None))
    except Exception as exc:
        results.append((thread_id, 'error', str(exc)))
        print(f'  thread {thread_id}: failed to acquire connection: {exc}')


def simulate_connection_leak(tenant_name):
    engine = create_tenant_engine(
        tenant_name,
        pool_size=2,
        max_overflow=0,
        pool_timeout=5,
    )
    create_sample_data(engine, tenant_name)

    print(f'Running connection leak simulation for tenant `{tenant_name}`')
    results = []
    threads = []

    # Two threads acquire connections and never close them.
    for i in range(2):
        thread = threading.Thread(target=leaky_request, args=(i + 1, engine, results))
        threads.append(thread)
        thread.start()

    time.sleep(1)

    # Additional requests now contend for the exhausted pool.
    for i in range(2, 4):
        thread = threading.Thread(target=normal_request, args=(i + 1, engine, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    leaked_count = sum(1 for _, status, _ in results if status == 'leaked')
    success_count = sum(1 for _, status, _ in results if status == 'success')
    error_count = sum(1 for _, status, _ in results if status == 'error')

    print('\nSummary:')
    print('  leaked connections =', leaked_count)
    print('  successes =', success_count)
    print('  errors =', error_count)
    if error_count:
        sample_error = next(err for _, status, err in results if status == 'error')
        print('  sample error =', sample_error)


if __name__ == '__main__':
    simulate_connection_leak('school_oakwood')
