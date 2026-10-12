"""Password rules applied whenever a password is chosen.

Existing passwords are never re-checked; the rules apply when someone
creates an account, changes their password, or an administrator resets it.

bcrypt only reads the first 72 bytes of a password, so longer passwords
are refused instead of being silently truncated.
"""

MIN_LENGTH = 10
MAX_BYTES = 72

# Exact matches only (case-insensitive). Long enough to pass the length rule,
# short enough to be guessed first by anyone attacking the login.
COMMON_PASSWORDS = frozenset(
    {
        "password1",
        "password12",
        "password123",
        "password1234",
        "password12345",
        "passw0rd123",
        "1234567890",
        "12345678910",
        "123456789012",
        "qwertyuiop",
        "qwerty12345",
        "qwerty123456",
        "letmein1234",
        "welcome1234",
        "welcome123",
        "admin12345",
        "administrator",
        "iloveyou123",
        "changeme123",
        "abcdefghij",
        "abc1234567",
        "0123456789",
        "1q2w3e4r5t",
    }
)


def password_problems(
    password: str,
    *,
    email: str | None = None,
    full_name: str | None = None,
) -> list[str]:
    """Return everything wrong with the password (empty list when fine)."""

    problems = []

    if len(password) < MIN_LENGTH:
        problems.append(
            f"Password must be at least {MIN_LENGTH} characters long."
        )

    if len(password.encode("utf-8")) > MAX_BYTES:
        problems.append(
            f"Password must be at most {MAX_BYTES} bytes long."
        )

    lowered = password.strip().lower()

    if lowered in COMMON_PASSWORDS:
        problems.append("Password is too common.")

    if password and len(set(password)) == 1:
        problems.append("Password cannot be a single repeated character.")

    if email:
        local_part = email.strip().lower().split("@", 1)[0]

        if len(local_part) >= 4 and local_part in lowered:
            problems.append("Password must not contain your email name.")

    if full_name and lowered == full_name.strip().lower():
        problems.append("Password must not be your name.")

    return problems


def validate_password(
    password: str,
    *,
    email: str | None = None,
    full_name: str | None = None,
) -> None:
    """Raise ValueError with a readable message if the password is refused."""

    problems = password_problems(
        password,
        email=email,
        full_name=full_name,
    )

    if problems:
        raise ValueError(" ".join(problems))