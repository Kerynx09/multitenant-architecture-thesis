#!/usr/bin/env python3
"""
Issue 4 (After): Credential rotation.
Creates a tenant user, then rotates the password, invalidating the old one.
"""
import psycopg2
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== UPDATE THESE WITH YOUR POSTGRESQL CREDENTIALS =====
SUPERUSER = "postgres"
SUPERUSER_PASSWORD = "1234567"   # <-- put your actual password here
# ========================================================

TENANTS = ["db_oakwood", "db_lincoln", "db_washington"]

def get_superuser_conn():
    conn = psycopg2.connect(
        dbname="postgres",
        user=SUPERUSER,
        password=SUPERUSER_PASSWORD,
        host="localhost"
    )
    conn.autocommit = True
    return conn

def ensure_tenant_user(tenant):
    """Create user if not exists, return username and initial password."""
    username = f"user_{tenant}"
    initial_password = f"pass_{tenant}_initial"
    with get_superuser_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE USER {username} WITH PASSWORD %s", (initial_password,))
                logger.info(f"Created user {username} with initial password")
            else:
                logger.info(f"User {username} already exists, will rotate password")
    return username, initial_password

def rotate_tenant_password(username, tenant):
    """Change the user's password to a new value."""
    new_password = f"pass_{tenant}_rotated_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    with get_superuser_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"ALTER USER {username} WITH PASSWORD %s", (new_password,))
            logger.info(f"Rotated password for {username}")
    return new_password

def test_access(tenant, username, password):
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
    except Exception:
        return False

def main():
    logger.info("=== Issue 4 After: Credential Rotation ===")
    for tenant in TENANTS:
        logger.info(f"--- Tenant: {tenant} ---")
        username, old_password = ensure_tenant_user(tenant)
        
        # Test old password works
        if test_access(tenant, username, old_password):
            logger.info("Old password works before rotation.")
        else:
            logger.error("Old password failed – user not created?")
            continue
        
        # Rotate password
        new_password = rotate_tenant_password(username, tenant)
        
        # Test old password should fail
        if test_access(tenant, username, old_password):
            logger.warning("Old password still works after rotation – rotation failed!")
        else:
            logger.info("Old password correctly rejected after rotation.")
        
        # Test new password works
        if test_access(tenant, username, new_password):
            logger.info("New password works after rotation. SUCCESS.")
        else:
            logger.error("New password does not work – rotation failed.")
    
    print("\nAfter script complete: Credentials are rotated; old passwords are invalidated.\n")

if __name__ == "__main__":
    main()