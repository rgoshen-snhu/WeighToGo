"""Verify migration 0007 adds the (user_id, created_at) partial index (NFR-P-3)."""

from __future__ import annotations

import importlib.util
import pathlib
import types

from sqlalchemy.engine import Engine

_PATH = pathlib.Path("alembic/versions/0007_performance_indexes.py")


def _load_migration() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("migration_0007", _PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fresh_engine_with_weight_entries() -> Engine:
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE weight_entries ("
                "  entry_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "  user_id INTEGER NOT NULL,"
                "  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                "  is_deleted INTEGER NOT NULL DEFAULT 0"
                ")"
            )
        )
    return engine


def test_migration_0007_file_exists() -> None:
    assert _PATH.is_file(), f"Migration not found at {_PATH}"


def test_migration_0007_revision_identifiers() -> None:
    mod = _load_migration()
    assert mod.revision == "0007"
    assert mod.down_revision == "0006"


def test_migration_0007_has_upgrade_and_downgrade() -> None:
    mod = _load_migration()
    assert callable(mod.upgrade)
    assert callable(mod.downgrade)


def test_migration_0007_creates_created_at_index() -> None:
    from alembic.operations import Operations
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import inspect

    engine = _fresh_engine_with_weight_entries()
    mod = _load_migration()
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        with Operations.context(ctx):
            mod.upgrade()
    names = {ix["name"] for ix in inspect(engine).get_indexes("weight_entries")}
    assert "idx_weight_entries_user_created_at" in names
    idx_map = {ix["name"]: ix for ix in inspect(engine).get_indexes("weight_entries")}
    assert idx_map["idx_weight_entries_user_created_at"]["column_names"] == [
        "user_id",
        "created_at",
    ]


def test_migration_0007_downgrade_removes_created_at_index() -> None:
    from alembic.operations import Operations
    from alembic.runtime.migration import MigrationContext
    from sqlalchemy import inspect

    engine = _fresh_engine_with_weight_entries()
    mod = _load_migration()
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        with Operations.context(ctx):
            mod.upgrade()
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        with Operations.context(ctx):
            mod.downgrade()
    names = {ix["name"] for ix in inspect(engine).get_indexes("weight_entries")}
    assert "idx_weight_entries_user_created_at" not in names
