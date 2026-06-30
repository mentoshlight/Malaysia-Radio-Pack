#!/usr/bin/env python3
"""
Malaysia Radio Pack (MRP) v2.0 — Database Initialisation

Creates all tables, enables PostGIS, and builds spatial indexes.

Usage:
    python -m scripts.init_db
    DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mrp python -m scripts.init_db
"""

import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# ── Ensure the project root is on sys.path ───────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.models import Base


# ── Config ───────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/mrp",
)


# ── Main ─────────────────────────────────────────────────────────────────────

async def init_database(url: str = DATABASE_URL) -> None:
    """Create all tables, enable PostGIS, create spatial indexes."""

    engine = create_async_engine(url, echo=False)

    async with engine.begin() as conn:
        # 1. Enable PostGIS extension
        print("[1/4] Enabling PostGIS extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

        # 2. Create all tables from ORM metadata
        print("[2/4] Creating tables...")
        await conn.run_sync(Base.metadata.create_all)

        # 3. Add PostGIS geography column for coverage radius
        print("[3/4] Adding PostGIS geography column & spatial indexes...")

        # Add geography point column (skip if already exists)
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'repeaters'
                      AND column_name = 'geog_point'
                ) THEN
                    ALTER TABLE repeaters ADD COLUMN geog_point geography(Point, 4326);
                END IF;
            END$$;
        """))

        # Populate geography from lat/lng
        await conn.execute(text("""
            UPDATE repeaters
            SET geog_point = ST_SetSRID(ST_MakePoint(longitude::double precision, latitude::double precision), 4326)::geography
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
              AND geog_point IS NULL;
        """))

        # GIST index on geography column
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_repeaters_geog
            ON repeaters USING GIST (geog_point);
        """))

        # B-tree indexes for common queries
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_repeaters_callsign
            ON repeaters (callsign);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_repeaters_state
            ON repeaters (state_id);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_repeaters_mode
            ON repeaters (mode);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_repeaters_status
            ON repeaters (status);
        """))

        # 4. Verify
        print("[4/4] Verifying tables...")
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = [row[0] for row in result.fetchall()]

    await engine.dispose()

    print(f"\n✅ Database initialised — {len(tables)} tables:")
    for t in tables:
        print(f"   • {t}")


def main():
    """CLI entry point."""
    print("=" * 60)
    print("  Malaysia Radio Pack (MRP) v2.0 — Database Init")
    print("=" * 60)
    print(f"  Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print()

    asyncio.run(init_database())


if __name__ == "__main__":
    main()
