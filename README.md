# Multitenant Architecture Patterns

A practical, standalone demonstration project for multi-tenant SaaS architecture patterns.
This repository is designed to support empirical proof of real issues and before/after solutions using a school application scenario.

## Project Structure

- `architectures/`
  - `arch1_db_per_tenant/` — dedicated database per tenant with practical issue demonstrations
  - `arch2_shared_rls/` — shared database with PostgreSQL RLS
  - `arch3_schema_per_tenant/` — schema-per-tenant design
  - `arch4_hybrid/` — hybrid routing across architectures
- `shared/` — shared data models and utilities
- `docs/` — documentation for the project

## Getting Started

1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the first issue demonstration for Architecture 1:
   ```bash
   python architectures/arch1_db_per_tenant/issue_1_connection_pool_exhaustion_before.py
   python architectures/arch1_db_per_tenant/issue_1_connection_pool_exhaustion_after.py
   ```

> The first demo now uses concurrent threads to simulate real simultaneous request load, while the after demo shows the corrected pool configuration.

## Goals

- Build one main school application adapted to four architectures
- Simulate real operational failures with actual data
- Implement practical fixes and capture before/after proof
- Keep the project clean and standalone for defense presentation
