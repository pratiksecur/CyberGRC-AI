from pathlib import Path

import pytest

from fastapi import HTTPException

from app.api.v1.routes import evidence as evidence_route
from app.core.config import (
    MAX_REQUEST_BODY_BYTES,
    MAX_UPLOAD_SIZE_BYTES,
    ALLOWED_UPLOAD_EXTENSIONS,
    ALLOWED_UPLOAD_MIME_TYPES,
)
from app.database.database import engine

from fastapi import UploadFile
from io import BytesIO

# ==========================================================
# HEALTH / SECURITY HEADERS
# ==========================================================

def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert body["application"] == "CyberGRC AI"
    assert body["version"] == "1.0.0"


def test_security_headers_are_present(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"

    assert (
        response.headers["permissions-policy"]
        == "camera=(), microphone=(), geolocation=()"
    )

    csp = response.headers["content-security-policy"]

    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp


# ==========================================================
# PUBLIC UPLOAD EXPOSURE
# ==========================================================

def test_public_upload_directory_is_not_exposed(client):
    response = client.get("/uploads/test.txt")

    assert response.status_code == 404


# ==========================================================
# PROTECTED EVIDENCE FILE ACCESS
# ==========================================================

def test_evidence_file_requires_authentication(
    client,
    resource_data,
):
    evidence = resource_data["evidence"]["admin"]

    response = client.get(
        f"/api/v1/evidence/{evidence.id}/file"
    )

    assert response.status_code == 401


def test_evidence_file_respects_visibility_scope(
    client,
    auth_headers,
    users,
    resource_data,
):
    evidence = resource_data["evidence"]["admin"]

    response = client.get(
        f"/api/v1/evidence/{evidence.id}/file",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


def test_evidence_file_can_be_accessed_when_in_scope(
    client,
    auth_headers,
    users,
    resource_data,
    db,
    tmp_path,
    monkeypatch,
):
    evidence = resource_data["evidence"]["admin"]

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    stored_file = upload_dir / "protected-test.pdf"

    stored_file.write_bytes(
        b"%PDF-1.4\nCyberGRC-AI security test\n"
    )

    monkeypatch.setattr(
        evidence_route,
        "UPLOAD_DIR",
        upload_dir,
    )

    evidence.file_path = str(stored_file)
    evidence.file_name = "original-evidence.pdf"

    db.commit()
    db.refresh(evidence)

    response = client.get(
        f"/api/v1/evidence/{evidence.id}/file",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    assert response.content == (
        b"%PDF-1.4\nCyberGRC-AI security test\n"
    )

    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="original-evidence.pdf"'
    )

    assert (
        response.headers["x-content-type-options"]
        == "nosniff"
    )


# ==========================================================
# UPLOAD VALIDATION
# ==========================================================

def test_executable_extension_is_rejected(
    client,
    auth_headers,
    users,
    resource_data,
):
    control = resource_data["controls"]["admin"]

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["admin"]),
        data={
            "control_id": str(control.id),
            "title": "Malicious Upload",
            "description": "Executable upload test",
        },
        files={
            "file": (
                "malware.exe",
                b"MZ fake executable",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400


def test_script_extension_is_rejected(
    client,
    auth_headers,
    users,
    resource_data,
):
    control = resource_data["controls"]["admin"]

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["admin"]),
        data={
            "control_id": str(control.id),
            "title": "Script Upload",
            "description": "Script upload test",
        },
        files={
            "file": (
                "payload.php",
                b"<?php echo 'test'; ?>",
                "application/x-httpd-php",
            )
        },
    )

    assert response.status_code == 400


def test_invalid_mime_type_is_rejected(
    client,
    auth_headers,
    users,
    resource_data,
):
    control = resource_data["controls"]["admin"]

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["admin"]),
        data={
            "control_id": str(control.id),
            "title": "Invalid MIME",
            "description": "MIME validation test",
        },
        files={
            "file": (
                "evidence.pdf",
                b"not actually a PDF",
                "application/x-malicious",
            )
        },
    )

    assert response.status_code == 400


# ==========================================================
# PATH TRAVERSAL / FILENAME SANITIZATION
# ==========================================================

def test_path_traversal_filename_is_rejected_directly():
    file = UploadFile(
        filename="../../malicious.pdf",
        file=BytesIO(b"test evidence"),
    )

    with pytest.raises(HTTPException) as exc_info:
        evidence_route._validate_upload_metadata(file)

    assert exc_info.value.status_code == 400


def test_normal_filename_is_accepted():
    file = UploadFile(
        filename="security-evidence.pdf",
        file=BytesIO(b"test evidence"),
        headers={"content-type": "application/pdf"},
    )

    result = evidence_route._validate_upload_metadata(file)

    assert result == "security-evidence.pdf"

# ==========================================================
# UPLOAD SIZE LIMIT
# ==========================================================

def test_upload_larger_than_configured_limit_is_rejected(
    client,
    auth_headers,
    users,
    resource_data,
):
    control = resource_data["controls"]["admin"]

    oversized_content = b"A" * (
        MAX_UPLOAD_SIZE_BYTES + 1
    )

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["admin"]),
        data={
            "control_id": str(control.id),
            "title": "Oversized Evidence",
            "description": "Oversized upload test",
        },
        files={
            "file": (
                "large.txt",
                oversized_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 413


# ==========================================================
# SERVER-GENERATED STORAGE NAMES
# ==========================================================

def test_uploaded_file_uses_server_generated_storage_name(
    client,
    auth_headers,
    users,
    resource_data,
    tmp_path,
    monkeypatch,
):
    control = resource_data["controls"]["admin"]

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    monkeypatch.setattr(
        evidence_route,
        "UPLOAD_DIR",
        upload_dir,
    )

    original_filename = "important-evidence.pdf"

    response = client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["admin"]),
        data={
            "control_id": str(control.id),
            "title": "Generated Name Test",
            "description": "Storage filename security test",
        },
        files={
            "file": (
                original_filename,
                b"%PDF-1.4\ntest",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["file_name"] == original_filename

    stored_path = Path(body["file_path"])

    assert stored_path.exists()

    assert stored_path.name != original_filename
    assert stored_path.suffix.lower() == ".pdf"


# ==========================================================
# FILE PATH INTEGRITY
# ==========================================================

def test_file_path_cannot_be_changed_through_update_endpoint(
    client,
    auth_headers,
    users,
    resource_data,
):
    evidence = resource_data["evidence"]["admin"]

    response = client.patch(
        f"/api/v1/evidence/{evidence.id}",
        headers=auth_headers(users["admin"]),
        json={
            "file_path": "../../outside/uploads/secret.txt"
        },
    )

    assert response.status_code == 400


# ==========================================================
# PATH ESCAPE PROTECTION
# ==========================================================

def test_file_path_escape_is_rejected(
    client,
    auth_headers,
    users,
    resource_data,
    db,
    tmp_path,
    monkeypatch,
):
    evidence = resource_data["evidence"]["admin"]

    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    outside_file = tmp_path / "outside.txt"

    outside_file.write_text(
        "This file must never be served."
    )

    monkeypatch.setattr(
        evidence_route,
        "UPLOAD_DIR",
        upload_dir,
    )

    evidence.file_path = str(outside_file)

    db.commit()
    db.refresh(evidence)

    response = client.get(
        f"/api/v1/evidence/{evidence.id}/file",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404


# ==========================================================
# CONFIGURATION SANITY
# ==========================================================

def test_upload_limit_is_within_request_limit():
    assert MAX_UPLOAD_SIZE_BYTES <= MAX_REQUEST_BODY_BYTES


def test_allowed_upload_extensions_are_restricted():
    forbidden_extensions = {
        ".exe",
        ".dll",
        ".bat",
        ".cmd",
        ".ps1",
        ".sh",
        ".php",
        ".py",
        ".js",
        ".msi",
    }

    assert (
        ALLOWED_UPLOAD_EXTENSIONS.isdisjoint(
            forbidden_extensions
        )
    )


def test_allowed_upload_mime_types_are_restricted():
    forbidden_mime_types = {
        "application/x-msdownload",
        "application/x-dosexec",
        "application/x-httpd-php",
        "application/javascript",
    }

    assert (
        ALLOWED_UPLOAD_MIME_TYPES.isdisjoint(
            forbidden_mime_types
        )
    )


# ==========================================================
# DATABASE CONNECTION HARDENING
# ==========================================================

def test_database_engine_uses_connection_pre_ping():
    assert getattr(
        engine.pool,
        "_pre_ping",
        False,
    ) is True