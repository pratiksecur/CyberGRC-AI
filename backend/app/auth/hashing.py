import os

from passlib.context import CryptContext


# ==========================================================
# BCRYPT COST FACTOR
# ==========================================================
#
# The work factor is configurable so automated tests can use the
# cheapest setting (BCRYPT_ROUNDS=4, set in backend/conftest.py) instead
# of spending roughly a quarter of a second per hashed password.
#
# Staging and production refuse to start with a weak setting. Hashes
# created with a different cost still verify correctly: bcrypt stores
# the cost inside every hash.

_DEFAULT_ROUNDS = 12
_MIN_ROUNDS = 4
_MAX_ROUNDS = 16
_MIN_NON_DEVELOPMENT_ROUNDS = 12


def _bcrypt_rounds() -> int:
    raw_value = os.getenv("BCRYPT_ROUNDS", str(_DEFAULT_ROUNDS)).strip()

    try:
        rounds = int(raw_value)
    except ValueError as exc:
        raise RuntimeError("BCRYPT_ROUNDS must be a valid integer.") from exc

    if not _MIN_ROUNDS <= rounds <= _MAX_ROUNDS:
        raise RuntimeError(
            f"BCRYPT_ROUNDS must be between {_MIN_ROUNDS} and {_MAX_ROUNDS}."
        )

    environment = os.getenv("ENVIRONMENT", "development").strip().lower()

    if (
        environment in {"staging", "production"}
        and rounds < _MIN_NON_DEVELOPMENT_ROUNDS
    ):
        raise RuntimeError(
            "BCRYPT_ROUNDS must be at least "
            f"{_MIN_NON_DEVELOPMENT_ROUNDS} in staging and production."
        )

    return rounds


# Configure bcrypt as the hashing algorithm
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=_bcrypt_rounds(),
)


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure hash.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)