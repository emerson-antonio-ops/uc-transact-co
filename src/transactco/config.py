"""Settings loaded from .env, with the same defaults as .env.example."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]


def _env(key: str, default: str) -> str:
    value = os.environ.get(key, "").strip()
    return value or default


def _env_int(key: str, default: int) -> int:
    return int(_env(key, str(default)))


@dataclass(frozen=True)
class Settings:
    pg_host: str
    pg_port: int
    pg_db: str
    pg_user: str
    pg_password: str
    ro_user: str
    ro_password: str
    duckdb_path: Path
    seed: int
    days: int
    customers: int
    products: int
    orders_per_day: int

    @property
    def admin_dsn(self) -> str:
        """Owner connection. Reads and writes everything, including _control."""
        return (
            f"host={self.pg_host} port={self.pg_port} dbname={self.pg_db} "
            f"user={self.pg_user} password={self.pg_password}"
        )

    @property
    def readonly_dsn(self) -> str:
        """The only connection `make land` is allowed to use. Cannot see _control."""
        return (
            f"host={self.pg_host} port={self.pg_port} dbname={self.pg_db} "
            f"user={self.ro_user} password={self.ro_password}"
        )


def load_settings() -> Settings:
    load_dotenv(REPO_ROOT / ".env")

    duckdb_path = Path(_env("DUCKDB_PATH", "warehouse.duckdb"))
    if not duckdb_path.is_absolute():
        duckdb_path = REPO_ROOT / duckdb_path

    return Settings(
        pg_host=_env("POSTGRES_HOST", "localhost"),
        pg_port=_env_int("POSTGRES_PORT", 5432),
        pg_db=_env("POSTGRES_DB", "transactco"),
        pg_user=_env("POSTGRES_USER", "transactco"),
        pg_password=_env("POSTGRES_PASSWORD", "transactco"),
        ro_user=_env("ANALYTICS_RO_USER", "analytics_ro"),
        ro_password=_env("ANALYTICS_RO_PASSWORD", "analytics_ro"),
        duckdb_path=duckdb_path,
        seed=_env_int("TRANSACTCO_SEED", 20260810),
        days=_env_int("SEED_DAYS", 90),
        customers=_env_int("SEED_CUSTOMERS", 5000),
        products=_env_int("SEED_PRODUCTS", 400),
        orders_per_day=_env_int("SEED_ORDERS_PER_DAY", 600),
    )
