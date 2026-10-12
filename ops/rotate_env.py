"""
Write a new .env with fresh secrets, keeping every other setting.

    python ops/rotate_env.py          writes .env.new (never overwrites .env)
    python ops/rotate_env.py --sql    prints the SQL that gives the database
                                      user the new password (pipe it to psql)

Rotated: POSTGRES_PASSWORD, SECRET_KEY, METRICS_AUTH_TOKEN.
The values are never printed.
"""

import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRENT = ROOT / ".env"
EXAMPLE = ROOT / ".env.example"
NEW = ROOT / ".env.new"

ROTATED = ("POSTGRES_PASSWORD", "SECRET_KEY", "METRICS_AUTH_TOKEN")


def read_value(path: Path, key: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"{key} not found in {path.name}")


def build() -> None:
    if NEW.exists():
        raise SystemExit(
            ".env.new already exists. Delete or rename it first, "
            "so a rotation is never silently repeated."
        )

    source = CURRENT if CURRENT.exists() else EXAMPLE

    values = {
        "POSTGRES_PASSWORD": secrets.token_urlsafe(24),
        "SECRET_KEY": secrets.token_urlsafe(48),
        "METRICS_AUTH_TOKEN": secrets.token_urlsafe(32),
    }

    lines = source.read_text(encoding="utf-8").splitlines()
    seen = set()
    output = []

    for line in lines:
        key = line.split("=", 1)[0] if "=" in line else None

        if key in values and not line.lstrip().startswith("#"):
            output.append(f"{key}={values[key]}")
            seen.add(key)
        elif key == "DATABASE_URL" and not line.lstrip().startswith("#"):
            output.append(
                re.sub(
                    r"(://[^:/@]+:)[^@]*(@)",
                    lambda m: m.group(1) + values["POSTGRES_PASSWORD"] + m.group(2),
                    line,
                    count=1,
                )
            )
        else:
            output.append(line)

    for key in ROTATED:
        if key not in seen:
            output.append(f"{key}={values[key]}")

    NEW.write_text("\n".join(output) + "\n", encoding="utf-8")

    print(f"Wrote {NEW.name} from {source.name}.")
    print("Rotated:", ", ".join(ROTATED))


def sql() -> None:
    if not NEW.exists():
        raise SystemExit("Run without --sql first to create .env.new.")

    password = read_value(NEW, "POSTGRES_PASSWORD").replace("'", "''")
    print(f"ALTER USER postgres PASSWORD '{password}';")


if __name__ == "__main__":
    sql() if "--sql" in sys.argv else build()