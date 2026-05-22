"""Alembic migration environment for the Weigh to Go! backend.

The database URL is sourced from application settings so that migrations
and the running application share a single configuration source.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from weighttogo.config import get_settings

# The Alembic Config object provides access to the values in alembic.ini.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# No models are defined yet; autogenerate support is wired up when the
# domain layer introduces SQLAlchemy models in a later phase.
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emitting SQL without a DBAPI)."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database connection.

    The URL is passed directly rather than through alembic.ini so that
    credentials containing characters such as '%' are not subject to
    ConfigParser interpolation.
    """
    connectable = engine_from_config(
        {"sqlalchemy.url": get_settings().database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
