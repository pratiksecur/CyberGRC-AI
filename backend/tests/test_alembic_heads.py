"""The migration history must have exactly one head.

Two heads mean two branches of migrations were created in parallel, and
`alembic upgrade head` would then fail. This test needs no database.
"""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_a_single_head():
    backend_dir = Path(__file__).resolve().parents[1]

    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "alembic"))

    heads = ScriptDirectory.from_config(config).get_heads()

    assert len(heads) == 1, f"Expected one Alembic head, found: {heads}"