"""Check that an uploaded file really is what its name says it is.

The browser (or an attacker) chooses the file name and the declared content
type, so neither can be trusted. Almost every binary format starts with a
fixed "signature", and the first bytes of the file are compared with the
signature expected for its extension.

Text files have no signature, so they are only checked for the signs of a
binary file: NUL bytes, or the start of a known executable or archive.
"""

# Extensions that must start with one of these byte strings.
SIGNATURES: dict[str, tuple[bytes, ...]] = {
    ".pdf": (b"%PDF-",),
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    # Word and Excel files made since 2007 are zip archives.
    ".zip": (b"PK\x03\x04", b"PK\x05\x06"),
    ".docx": (b"PK\x03\x04",),
    ".xlsx": (b"PK\x03\x04",),
    # Older Word and Excel files use the OLE2 container.
    ".doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", b"{\\rtf"),
    ".xls": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
}

TEXT_EXTENSIONS = frozenset({".txt", ".csv"})

# Seen at the start of files that are not text.
BINARY_STARTS = (
    b"MZ",  # Windows executable
    b"\x7fELF",  # Linux executable
    b"PK\x03\x04",  # zip
    b"%PDF-",
    b"\x89PNG",
    b"\xff\xd8\xff",
    b"\xd0\xcf\x11\xe0",
    b"Rar!",
    b"7z\xbc\xaf",
    b"\x1f\x8b",  # gzip
)

# How many bytes from the start are inspected.
HEAD_BYTES = 8192


def check_file_signature(extension: str, head: bytes) -> str | None:
    """
    Return a message describing the problem, or None if the file looks right.

    ``head`` is the first bytes of the file.
    """

    extension = extension.lower()

    if not head:
        return "The uploaded file is empty."

    head = head[:HEAD_BYTES]

    if extension in TEXT_EXTENSIONS:
        if b"\x00" in head or head.startswith(BINARY_STARTS):
            return "The file content is not plain text."

        return None

    expected = SIGNATURES.get(extension)

    if expected is None:
        return "File type is not allowed."

    if not head.startswith(expected):
        return "The file content does not match its file type."

    return None