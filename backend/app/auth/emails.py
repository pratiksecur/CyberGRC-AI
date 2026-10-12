"""One place that decides what an email address looks like inside the app."""


def normalize_email(value: str) -> str:
    """
    Emails are compared case-insensitively, so they are stored and looked
    up in lowercase with surrounding whitespace removed.
    """

    return value.strip().lower()