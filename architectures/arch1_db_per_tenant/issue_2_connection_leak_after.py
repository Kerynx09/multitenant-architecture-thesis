import os
import sys
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
    Create the tenant table and add sample rows.
    This setup is shared between before and after demos.
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


def safe_request(request_id, engine, results):
    """
    Simulate a request that acquires a connection and closes it cleanly.
    This shows the pool can reuse the connection for subsequent requests.
    """
    try:
        conn = engine.connect()
        print(f'  request {request_id}: acquired connection')
        time.sleep(1)
        conn.close()
        print(f'  request {request_id}: closed connection cleanly')
        results.append((request_id, 'success', None))
    except Exception as exc:
        results.append((request_id, 'error', str(exc)))
        print(f'  request {request_id}: failed to acquire connection: {exc}')


def simulate_connection_leak_fix(tenant_name):
    engine = create_tenant_engine(
        tenant_name,
        pool_size=2,
        max_overflow=0,
        pool_timeout=5,
    )
    create_sample_data(engine, tenant_name)

    print(f'Running connection leak fix for tenant `{tenant_name}`')
    results = []

    # The after demo uses sequential requests with the same pool config.
    # This proves that once connections are closed cleanly, the pool can
    # reuse its limited connection capacity instead of being drained by leaks.
    for request_id in range(1, 5):
        safe_request(request_id, engine, results)

    success_count = sum(1 for _, status, _ in results if status == 'success')
    error_count = sum(1 for _, status, _ in results if status == 'error')

    print('\nSummary:')
    print('  total requests =', len(results))
    print('  successes =', success_count)
    print('  errors =', error_count)
    if error_count:
        sample_error = next(err for _, status, err in results if status == 'error')
        print('  sample error =', sample_error)


if __name__ == '__main__':
    simulate_connection_leak_fix('school_oakwood')
