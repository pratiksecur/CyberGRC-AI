"""Load the built-in framework catalogs into an organization.

Run from the backend folder (or inside the backend container):

    python -m app.seed.frameworks --organization-id 1 --dry-run
    python -m app.seed.frameworks --organization-id 1
    python -m app.seed.frameworks --all-organizations
    python -m app.seed.frameworks --organization-id 1 --framework "DORA" --merge

Safe to run repeatedly: it never edits or deletes existing rows. A framework
that already exists (same name in that organization) is skipped, unless
--merge is given, in which case only its missing controls are added.
"""

import argparse
import sys
from importlib import import_module

CATALOG_MODULES = ("nist_csf", "iso_27001", "gdpr", "nis2", "dora")


def _clean(text: str) -> str:
    return " ".join(text.split())


def load_catalog() -> list[dict]:
    catalog = []

    for module_name in CATALOG_MODULES:
        data = import_module(f"app.seed.catalog.{module_name}").FRAMEWORK

        catalog.append(
            {
                "name": data["name"],
                "version": data["version"],
                "description": _clean(data["description"]),
                "controls": [
                    {
                        "code": code,
                        "title": title,
                        "description": _clean(description),
                    }
                    for code, title, description in data["controls"]
                ],
            }
        )

    return catalog


def seed_organization(db, organization_id: int, *, only=None, merge=False) -> list[dict]:
    """Add catalog frameworks to one organization. Does not commit."""

    from app.models.framework import Framework
    from app.models.framework_control import FrameworkControl

    wanted = {name.strip().lower() for name in only} if only else None
    results = []

    for entry in load_catalog():
        if wanted is not None and entry["name"].lower() not in wanted:
            continue

        existing = (
            db.query(Framework)
            .filter(
                Framework.organization_id == organization_id,
                Framework.name == entry["name"],
            )
            .first()
        )

        if existing is None:
            framework = Framework(
                organization_id=organization_id,
                name=entry["name"],
                version=entry["version"],
                description=entry["description"],
            )
            db.add(framework)
            db.flush()
            created = True
        elif merge:
            framework = existing
            created = False
        else:
            results.append(
                {
                    "framework": entry["name"],
                    "status": "skipped (already exists; use --merge to add missing controls)",
                    "controls_added": 0,
                }
            )
            continue

        known_codes = {
            code
            for (code,) in db.query(FrameworkControl.control_code).filter(
                FrameworkControl.framework_id == framework.id
            )
        }

        added = 0

        for control in entry["controls"]:
            if control["code"] in known_codes:
                continue

            db.add(
                FrameworkControl(
                    framework_id=framework.id,
                    control_code=control["code"],
                    title=control["title"],
                    description=control["description"],
                )
            )
            added += 1

        db.flush()

        results.append(
            {
                "framework": entry["name"],
                "status": "created" if created else "merged",
                "controls_added": added,
            }
        )

    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--organization-id", type=int)
    target.add_argument("--all-organizations", action="store_true")
    parser.add_argument("--framework", action="append", help="Only this catalog framework (repeatable).")
    parser.add_argument("--merge", action="store_true", help="Add missing controls to existing frameworks.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen; change nothing.")
    args = parser.parse_args(argv)

    from app.database.database import SessionLocal
    from app.models.organization import Organization

    db = SessionLocal()

    try:
        if args.all_organizations:
            organization_ids = [
                organization_id
                for (organization_id,) in db.query(Organization.id)
                .filter(Organization.is_active.is_(True))
                .order_by(Organization.id)
            ]
        else:
            if db.query(Organization.id).filter(Organization.id == args.organization_id).first() is None:
                print(f"Organization {args.organization_id} does not exist.")
                return 1
            organization_ids = [args.organization_id]

        for organization_id in organization_ids:
            print(f"Organization {organization_id}:")
            for row in seed_organization(
                db, organization_id, only=args.framework, merge=args.merge
            ):
                print(f"  {row['framework']}: {row['status']}, controls added: {row['controls_added']}")

        if args.dry_run:
            db.rollback()
            print("Dry run: nothing was saved.")
        else:
            db.commit()
            print("Saved.")

        return 0

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())