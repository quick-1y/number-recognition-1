import asyncio
import os
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import async_engine_from_config

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    raise RuntimeError(
        "python-dotenv is required to run alembic commands. Please install dependencies from backend/requirements.txt."
    ) from exc

BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent

sys.path.append(str(BASE_DIR))

from app.db.base import Base  # noqa: E402
from app.db import models  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

dotenv_paths = [
    BASE_DIR / ".env",
    PROJECT_ROOT / ".env",
]
for env_path in dotenv_paths:
    load_dotenv(env_path, override=False)

def resolve_database_url() -> str:
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required for alembic migrations.")

    url = make_url(database_url)

    if url.get_backend_name() == "sqlite" and url.database:
        db_path = Path(url.database)
        if not db_path.is_absolute():
            db_path = (PROJECT_ROOT / db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = url.set(database=str(db_path))

    return str(url)


config.set_main_option("sqlalchemy.url", resolve_database_url())

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)


def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section)
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def process_migrations():
        async with connectable.begin() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(process_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
