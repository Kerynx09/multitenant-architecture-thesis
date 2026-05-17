"""
Issue 5 (Before): Vulnerable to tenant ID tampering.
Trusts user‑supplied tenant ID – attacker can change it to access another tenant's data.
"""
import os
import sys
import logging
from datetime import datetime
from core import create_tenant_engine
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simulated authenticated user (belongs to db_oakwood)
AUTHENTICATED_TENANT = "db_oakwood"

def get_data(tenant_id):
    """Vulnerable: directly uses user‑provided tenant ID to connect."""
    try:
        engine = create_tenant_engine(tenant_id, pool_size=1)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM students"))
            count = result.scalar()
            logger.info(f"Query on {tenant_id} returned {count} rows")
            return count
    except Exception as e:
        logger.error(f"Failed: {e}")
        return None

def main():
    logger.info("=== Issue 5 Before: Vulnerable to Tenant Tampering ===")
    logger.info(f"Authenticated user belongs to: {AUTHENTICATED_TENANT}")
    
    # Legitimate request
    logger.info("--- Legitimate request ---")
    get_data(AUTHENTICATED_TENANT)
    
    # Attack: tamper with tenant ID
    logger.info("--- Attacker changes tenant ID to db_lincoln ---")
    get_data("db_lincoln")
    
    print("\nVulnerable: Attacker accessed another tenant's data.\n")

if __name__ == "__main__":
    main()