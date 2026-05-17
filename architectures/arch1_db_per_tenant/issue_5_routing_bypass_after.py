"""
Issue 5 (After): Secure – tenant ID from session, ignores user input.
"""
import os
import sys
import logging
from core import create_tenant_engine
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simulated authenticated user (tenant stored in session)
AUTHENTICATED_TENANT = "db_oakwood"

def get_data(user_provided_tenant_id):
    """Secure: ignores user input, uses session tenant."""
    actual_tenant = AUTHENTICATED_TENANT
    logger.info(f"Using tenant from session: {actual_tenant} (ignored input: {user_provided_tenant_id})")
    try:
        engine = create_tenant_engine(actual_tenant, pool_size=1)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM students"))
            count = result.scalar()
            logger.info(f"Query on {actual_tenant} returned {count} rows")
            return count
    except Exception as e:
        logger.error(f"Failed: {e}")
        return None

def main():
    logger.info("=== Issue 5 After: Tenant ID from Session ===")
    logger.info(f"Authenticated user belongs to: {AUTHENTICATED_TENANT}")
    
    # Legitimate request
    logger.info("--- Legitimate request ---")
    get_data(AUTHENTICATED_TENANT)
    
    # Attacker tries to tamper
    logger.info("--- Attacker tries to change tenant ID to db_lincoln ---")
    get_data("db_lincoln")
    
    print("\nSecure: Attacker cannot access another tenant's data.\n")

if __name__ == "__main__":
    main()