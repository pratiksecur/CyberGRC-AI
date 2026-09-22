from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_operations_runbook_exists():
    runbook = (
        PROJECT_ROOT
        / "docs"
        / "OPERATIONS.md"
    )

    assert runbook.exists()
    assert runbook.is_file()


def test_operations_runbook_documents_database_backup():
    runbook = (
        PROJECT_ROOT
        / "docs"
        / "OPERATIONS.md"
    )

    content = runbook.read_text(
        encoding="utf-8"
    )

    assert "pg_dump" in content
    assert "pg_restore" in content
    assert "postgres_data" in content


def test_operations_runbook_documents_evidence_backup():
    runbook = (
        PROJECT_ROOT
        / "docs"
        / "OPERATIONS.md"
    )

    content = runbook.read_text(
        encoding="utf-8"
    )

    assert "uploads_data" in content
    assert "Evidence Files" in content


def test_operations_runbook_documents_health_and_readiness():
    runbook = (
        PROJECT_ROOT
        / "docs"
        / "OPERATIONS.md"
    )

    content = runbook.read_text(
        encoding="utf-8"
    )

    assert "/api/v1/health" in content
    assert "/api/v1/ready" in content


def test_operations_runbook_documents_secret_handling():
    runbook = (
        PROJECT_ROOT
        / "docs"
        / "OPERATIONS.md"
    )

    content = runbook.read_text(
        encoding="utf-8"
    )

    assert ".env" in content
    assert ".env.example" in content
    assert "secrets" in content.lower()