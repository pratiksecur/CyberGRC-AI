"""Uploads are checked against the file's real contents, not just its name."""

import pytest

from app.core.upload_validation import check_file_signature

PDF = b"%PDF-1.4\n1 0 obj\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16
ZIP = b"PK\x03\x04" + b"\x00" * 16
OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 16


# ----------------------------------------------------------
# The check itself
# ----------------------------------------------------------

@pytest.mark.parametrize(
    "extension,content",
    [
        (".pdf", PDF),
        (".png", PNG),
        (".jpg", JPEG),
        (".jpeg", JPEG),
        (".zip", ZIP),
        (".docx", ZIP),
        (".xlsx", ZIP),
        (".doc", OLE),
        (".xls", OLE),
        (".doc", b"{\\rtf1\\ansi"),
        (".txt", b"plain text evidence\n"),
        (".csv", b"a,b,c\n1,2,3\n"),
        (".csv", "naïve,café\n".encode("cp1252")),
    ],
)
def test_genuine_files_pass(extension, content):
    assert check_file_signature(extension, content) is None


@pytest.mark.parametrize(
    "extension,content",
    [
        (".pdf", b"this is not a pdf"),
        (".pdf", PNG),
        (".png", PDF),
        (".jpg", PNG),
        (".docx", PDF),
        (".xlsx", b"just text"),
        (".xls", ZIP),
        (".zip", b"MZ\x90\x00 executable"),
    ],
)
def test_files_that_do_not_match_their_extension_fail(extension, content):
    assert check_file_signature(extension, content)


@pytest.mark.parametrize(
    "content",
    [
        b"MZ\x90\x00\x03\x00",  # Windows executable
        b"\x7fELF\x02\x01",  # Linux executable
        PDF,
        ZIP,
        b"text with a NUL \x00 inside",
    ],
)
def test_text_files_cannot_be_binaries(content):
    assert check_file_signature(".txt", content)
    assert check_file_signature(".csv", content)


def test_empty_files_fail():
    assert check_file_signature(".pdf", b"")
    assert check_file_signature(".txt", b"")


def test_unknown_extensions_fail():
    assert check_file_signature(".exe", b"MZ")


# ----------------------------------------------------------
# Through the API
# ----------------------------------------------------------

def _upload(client, auth_headers, users, resource_data, name, content, mime):
    control = resource_data["controls"]["admin"]

    return client.post(
        "/api/v1/evidence/",
        headers=auth_headers(users["admin"]),
        data={
            "control_id": str(control.id),
            "title": "Signature test",
            "description": "Upload content check",
        },
        files={"file": (name, content, mime)},
    )


@pytest.mark.parametrize(
    "name,content,mime",
    [
        ("report.pdf", PDF, "application/pdf"),
        ("picture.png", PNG, "image/png"),
        ("photo.jpg", JPEG, "image/jpeg"),
        ("notes.txt", b"plain text", "text/plain"),
        ("archive.zip", ZIP, "application/zip"),
    ],
)
def test_genuine_uploads_are_accepted(
    client, auth_headers, users, resource_data, name, content, mime
):
    response = _upload(
        client, auth_headers, users, resource_data, name, content, mime
    )

    assert response.status_code in {200, 201}, response.text


@pytest.mark.parametrize(
    "name,content,mime",
    [
        ("report.pdf", b"<html>not a pdf</html>", "application/pdf"),
        ("picture.png", PDF, "image/png"),
        ("notes.txt", b"MZ\x90\x00binary", "text/plain"),
        ("data.csv", b"a,b\x00,c", "text/csv"),
        ("empty.pdf", b"", "application/pdf"),
    ],
)
def test_disguised_uploads_are_rejected(
    client, auth_headers, users, resource_data, name, content, mime
):
    response = _upload(
        client, auth_headers, users, resource_data, name, content, mime
    )

    assert response.status_code == 400