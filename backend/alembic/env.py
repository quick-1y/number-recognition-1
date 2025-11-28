import asyncio
import os
from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:  # pragma: no cover - dependency guard
    raise RuntimeError(
        "python-dotenv is required to run alembic commands. Please install dependencies from backend/requirements.txt."
    ) from exc

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.base import Base  # noqa: E402
from app.db import models  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

dotenv_paths = [
    Path(__file__).resolve().parents[1] / ".env",
    Path(__file__).resolve().parents[2] / ".env",
]
for env_path in dotenv_paths:
    load_dotenv(env_path, override=False)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable is required for alembic migrations.")

config.set_main_option("sqlalchemy.url", database_url)

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
