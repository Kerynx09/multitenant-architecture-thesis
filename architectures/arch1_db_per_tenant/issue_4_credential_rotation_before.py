#!/usr/bin/env python3
"""
Issue 4 (Before): No credential rotation.
Simulates a tenant database user whose password is never changed.
"""
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== UPDATE THESE WITH YOUR POSTGRESQL CREDENTIALS =====
SUPERUSER = "postgres"
SUPERUSER_PASSWORD = "1234567"   # <-- put your actual password here
# ========================================================

TENANTS = ["db_oakwood", "db_lincoln", "db_washington"]

def get_superuser_conn():
    """Return a connection as superuser."""
    conn = psycopg2.connect(
        dbname="postgres",
        user=SUPERUSER,
        password=SUPERUSER_PASSWORD,
        host="localhost"
    )
    conn.autocommit = True
    return conn

def ensure_tenant_user(tenant):
    """Create a database user for the tenant if not exists, return (username, password)."""
    username = f"user_{tenant}"
    password = f"pass_{tenant}_initial"
    with get_superuser_conn() as conn:
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE USER {username} WITH PASSWORD %s", (password,))
                logger.info(f"Created user {username} for tenant {tenant}")
            else:
                logger.info(f"User {username} already exists (password unchanged)")
    return username, password

def test_tenant_access(tenant, username, password):
    """Attempt to connect to tenant database using given credentials."""
    try:
        conn = psycopg2.connect(
            dbname=tenant,
            user=username,
            password=password,
            host="localhost",
            connect_timeout=5
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Access failed for {tenant} with user {username}: {e}")
        return False

def main():
    logger.info("=== Issue 4 Before: No Credential Rotation ===")
    for tenant in TENANTS:
        logger.info(f"--- Tenant: {tenant} ---")
        username, password = ensure_tenant_user(tenant)
        if test_tenant_access(tenant, username, password):
            logger.info(f"Access granted with initial password.")
        else:
            logger.error(f"Could not access tenant database with created user.")
    print("\nBefore script complete: Credentials are never rotated. Old passwords remain valid forever.\n")

if __name__ == "__main__":
    main()