"""Alembic migrations must build the real schema on an empty PostgreSQL.

Each test run creates a brand-new database (<name>_migration), runs
`alembic upgrade head` in a subprocess exactly like the Docker `migrate`
service does, then compares the result with the SQLAlchemy models.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

from app.database.database import Base

pytestmark = pytest.mark.postgres

BACKEND_DIR = Path(__file__).resolve().parents[2]

_STRUCTURAL_DIFFS = {
    "add_table",
    "remove_table",
    "add_column",
    "remove_column",
    "modify_nullable",
}


@pytest.fixture(scope="module")
def migrated_database(pg_url):
    base_url = make_url(pg_url)
    database_name = f"{base_url.database}_migration"
    admin_url = base_url.set(database="postgres")
    migration_url = base_url.set(database=database_name)

    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as connection:
        connection.execute(
            text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
        )
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))

    rendered_url = migration_url.render_as_string(hide_password=False)

    environment = dict(os.environ)
    environment["DATABASE_URL"] = rendered_url

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(BACKEND_DIR),
        env=environment,
        capture_output=True,
        text=True,
        timeout=600,
    )

    engine = create_engine(rendered_url)

    try:
        yield {"result": result, "engine": engine}
    finally:
        engine.dispose()
        with admin_engine.connect() as connection:
            connection.execute(
                text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
            )
        admin_engine.dispose()


def test_upgrade_head_succeeds_on_empty_database(migrated_database):
    result = migrated_database["result"]

    assert result.returncode == 0, (
        "alembic upgrade head failed.\n"
        f"STDOUT:\n{result.stdout[-2000:]}\nSTDERR:\n{result.stderr[-4000:]}"
    )

    tables = set(inspect(migrated_database["engine"]).get_table_names())

    assert {"organizations", "users", "risks"} <= tables


def test_migrated_schema_matches_models(migrated_database):
    assert migrated_database["result"].returncode == 0, (
        "Migration failed; see test_upgrade_head_succeeds_on_empty_database."
    )

    with migrated_database["engine"].connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={"compare_type": False, "compare_server_default": False},
        )
        raw_differences = compare_metadata(context, Base.metadata)

    flat = []
    for difference in raw_differences:
        if isinstance(difference, list):
            flat.extend(difference)
        else:
            flat.append(difference)

    problems = []
    for difference in flat:
        kind = difference[0]
        if kind not in _STRUCTURAL_DIFFS:
            continue
        if kind in {"add_table", "remove_table"}:
            problems.append(f"{kind}: {difference[1].name}")
        elif kind in {"add_column", "remove_column"}:
            problems.append(f"{kind}: {difference[2]}.{difference[3].name}")
        else:
            problems.append(f"{kind}: {difference[2]}.{difference[3]}")

    assert not problems, (
        "Migrations and models disagree (a migration is missing or wrong):\n"
        + "\n".join(sorted(problems))
    )