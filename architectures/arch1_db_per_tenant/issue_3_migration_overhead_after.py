"""
Issue 3 (After): Concurrent schema migration on test table.
Uses threading to migrate all tenants in parallel.
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core import create_tenant_engine
from sqlalchemy import text, inspect

# Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_filename = f"{log_dir}/migration_after_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TENANTS = ["db_oakwood", "db_lincoln", "db_washington"]

def create_test_table_if_not_exists(engine, tenant_name):
    inspector = inspect(engine)
    if not inspector.has_table("migration_test"):
        logger.info(f"Tenant {tenant_name}: creating test table 'migration_test'")
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE migration_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        logger.info(f"Tenant {tenant_name}: test table created")
    else:
        logger.info(f"Tenant {tenant_name}: test table already exists")

def column_exists(engine, table_name, column_name):
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def add_column(engine, tenant_name):
    with engine.connect() as conn:
        if not column_exists(engine, "migration_test", "description"):
            conn.execute(text("ALTER TABLE migration_test ADD COLUMN description VARCHAR(255)"))
            conn.commit()
            logger.info(f"Tenant {tenant_name}: added column 'description'")
        else:
            logger.info(f"Tenant {tenant_name}: column already exists, skipping")

def migrate_tenant(tenant_name, results, index):
    start = time.time()
    engine = None
    try:
        engine = create_tenant_engine(tenant_name, pool_size=5, max_overflow=5, pool_timeout=10)
        create_test_table_if_not_exists(engine, tenant_name)
        add_column(engine, tenant_name)
        elapsed = time.time() - start
        logger.info(f"Tenant {tenant_name}: migration completed in {elapsed:.3f}s")
        results[index] = (tenant_name, elapsed, "success")
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"Tenant {tenant_name}: migration failed - {e}")
        results[index] = (tenant_name, elapsed, f"error: {e}")
    finally:
        if engine:
            engine.dispose()

def main():
    logger.info("=== Starting CONCURRENT migration (after) ===")
    results = [None] * len(TENANTS)
    threads = []
    total_start = time.time()

    for i, tenant in enumerate(TENANTS):
        t = threading.Thread(target=migrate_tenant, args=(tenant, results, i))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    total_elapsed = time.time() - total_start
    logger.info(f"All migrations completed in {total_elapsed:.3f} seconds")

    print("\n=== Summary (Concurrent) ===")
    print(f"Total tenants: {len(TENANTS)}")
    print(f"Total time: {total_elapsed:.3f} seconds")
    print(f"Average per tenant (parallel): {total_elapsed/len(TENANTS):.3f} seconds")
    for i, (tenant, elapsed, status) in enumerate(results):
        print(f"  {tenant}: {elapsed:.3f}s - {status}")
    print(f"Log saved to: {log_filename}")

if __name__ == "__main__":
    main()