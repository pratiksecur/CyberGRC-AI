"""Cross-framework crosswalk: related requirements and mapping suggestions.

The crosswalk data (app/seed/catalog/crosswalk.py) tags each built-in
catalog requirement with security themes. This service uses those tags to
answer three questions, always inside one organization:

  * Which requirements in other frameworks relate to this requirement?
  * Which further requirements might this control also support?
  * Which unmapped requirements might existing controls already support?

Nothing here creates a mapping. The results are suggestions for a person to
review; applying one goes through the normal mapping endpoint, with its own
authorization and audit logging.

Frameworks are matched to the crosswalk by their catalog name and
requirement code. A framework the organization created or renamed itself
has no crosswalk data and simply produces no suggestions.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.control import Control
from app.models.control_framework_control import ControlFrameworkControl
from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.seed.catalog.crosswalk import (
    CROSSWALK,
    DIRECT_THEME_COUNT,
    THEMES,
    UMBRELLA_THEME_COUNT,
)

DISCLAIMER = (
    "Suggestions come from a thematic crosswalk written for this platform. "
    "It is not an official mapping, and a shared theme does not mean two "
    "requirements are equivalent. Review each suggestion before applying it."
)

MAX_OPPORTUNITIES = 200

_CONFIDENCE_ORDER = {"direct": 0, "broad": 1}


@dataclass(frozen=True)
class _Requirement:
    id: int
    code: str
    title: str
    framework_id: int
    framework_name: str
    themes: frozenset[str]


# ----------------------------------------------------------
# Pure crosswalk logic
# ----------------------------------------------------------

def themes_for(framework_name: str, control_code: str) -> frozenset[str]:
    """Return the themes of a catalog requirement (empty if unknown)."""

    return frozenset(
        CROSSWALK.get(framework_name, {}).get(control_code, ())
    )


def is_umbrella(themes: frozenset[str]) -> bool:
    """Too broad to say which specific requirements a control supports."""

    return len(themes) >= UMBRELLA_THEME_COUNT


def link_confidence(
    source_themes: frozenset[str],
    target_themes: frozenset[str],
) -> str | None:
    """Return "direct", "broad", or None when the two do not share a theme."""

    if not source_themes & target_themes:
        return None

    if (
        len(source_themes) <= DIRECT_THEME_COUNT
        and len(target_themes) <= DIRECT_THEME_COUNT
    ):
        return "direct"

    return "broad"


def _theme_list(keys) -> list[dict]:
    return sorted(
        ({"key": key, "label": THEMES[key]} for key in keys),
        key=lambda theme: theme["label"],
    )


def _requirement_dict(requirement: _Requirement) -> dict:
    return {
        "framework_control_id": requirement.id,
        "control_code": requirement.code,
        "title": requirement.title,
        "framework_id": requirement.framework_id,
        "framework_name": requirement.framework_name,
    }


def _better(first: str, second: str) -> str:
    return (
        first
        if _CONFIDENCE_ORDER[first] <= _CONFIDENCE_ORDER[second]
        else second
    )


# ----------------------------------------------------------
# Data loading (always scoped to one organization)
# ----------------------------------------------------------

def _load_requirements(
    db: Session,
    organization_id: int,
) -> list[_Requirement]:
    rows = (
        db.query(FrameworkControl, Framework)
        .join(Framework, Framework.id == FrameworkControl.framework_id)
        .filter(Framework.organization_id == organization_id)
        .order_by(Framework.name.asc(), FrameworkControl.id.asc())
        .all()
    )

    return [
        _Requirement(
            id=requirement.id,
            code=requirement.control_code,
            title=requirement.title,
            framework_id=framework.id,
            framework_name=framework.name,
            themes=themes_for(framework.name, requirement.control_code),
        )
        for requirement, framework in rows
    ]


def _load_visible_mappings(
    db: Session,
    requirement_ids: set[int],
    visible_user_ids: set[int],
) -> dict[int, list[Control]]:
    """Controls mapped to each requirement, limited to what the user may see."""

    mapped: dict[int, list[Control]] = {}

    if not requirement_ids or not visible_user_ids:
        return mapped

    rows = (
        db.query(ControlFrameworkControl.framework_control_id, Control)
        .join(Control, Control.id == ControlFrameworkControl.control_id)
        .filter(Control.owner_id.in_(visible_user_ids))
        .order_by(Control.id.asc())
        .all()
    )

    for framework_control_id, control in rows:
        if framework_control_id in requirement_ids:
            mapped.setdefault(framework_control_id, []).append(control)

    return mapped


# ----------------------------------------------------------
# Related requirements for one requirement
# ----------------------------------------------------------

def get_related_requirements(
    db: Session,
    framework_control: FrameworkControl,
    organization_id: int,
    visible_user_ids: set[int],
) -> dict:
    requirements = _load_requirements(db, organization_id)

    source = next(
        (item for item in requirements if item.id == framework_control.id),
        None,
    )

    if source is None:
        raise ValueError("Requirement is outside the organization.")

    mappings = _load_visible_mappings(
        db,
        {item.id for item in requirements},
        visible_user_ids,
    )

    related = []

    for target in requirements:
        if target.framework_id == source.framework_id:
            continue

        confidence = link_confidence(source.themes, target.themes)

        if confidence is None:
            continue

        related.append(
            {
                **_requirement_dict(target),
                "shared_themes": _theme_list(source.themes & target.themes),
                "confidence": confidence,
                "mapped_control_count": len(mappings.get(target.id, [])),
            }
        )

    related.sort(
        key=lambda item: (
            _CONFIDENCE_ORDER[item["confidence"]],
            item["framework_name"],
            item["framework_control_id"],
        )
    )

    return {
        "requirement": _requirement_dict(source),
        "themes": _theme_list(source.themes),
        "in_crosswalk": bool(source.themes),
        "is_umbrella": is_umbrella(source.themes),
        "related": related,
    }


# ----------------------------------------------------------
# Suggestions for one control
# ----------------------------------------------------------

def get_control_suggestions(
    db: Session,
    control: Control,
    organization_id: int,
) -> dict:
    requirements = _load_requirements(db, organization_id)
    by_id = {item.id: item for item in requirements}

    mapped_ids = {
        framework_control_id
        for (framework_control_id,) in db.query(
            ControlFrameworkControl.framework_control_id
        ).filter(ControlFrameworkControl.control_id == control.id)
        if framework_control_id in by_id
    }

    sources = [
        by_id[requirement_id]
        for requirement_id in sorted(mapped_ids)
        if by_id[requirement_id].themes
        and not is_umbrella(by_id[requirement_id].themes)
    ]

    suggestions: dict[int, dict] = {}

    for source in sources:
        for target in requirements:
            if (
                target.id in mapped_ids
                or target.framework_id == source.framework_id
            ):
                continue

            confidence = link_confidence(source.themes, target.themes)

            if confidence is None:
                continue

            entry = suggestions.setdefault(
                target.id,
                {
                    **_requirement_dict(target),
                    "themes": set(),
                    "confidence": confidence,
                    "because_of": [],
                },
            )

            entry["themes"] |= source.themes & target.themes
            entry["confidence"] = _better(entry["confidence"], confidence)
            entry["because_of"].append(_requirement_dict(source))

    result = []

    for entry in suggestions.values():
        themes = entry.pop("themes")
        entry["shared_themes"] = _theme_list(themes)
        result.append(entry)

    result.sort(
        key=lambda item: (
            _CONFIDENCE_ORDER[item["confidence"]],
            item["framework_name"],
            item["framework_control_id"],
        )
    )

    return {
        "control_id": control.id,
        "mapped_requirement_count": len(mapped_ids),
        "suggestions": result,
    }


# ----------------------------------------------------------
# Organization-wide opportunities
# ----------------------------------------------------------

def get_crosswalk_opportunities(
    db: Session,
    organization_id: int,
    visible_user_ids: set[int],
) -> dict:
    """Unmapped requirements that already-mapped controls may support."""

    requirements = _load_requirements(db, organization_id)

    mappings = _load_visible_mappings(
        db,
        {item.id for item in requirements},
        visible_user_ids,
    )

    # Mapped, focused requirements are the only possible sources.
    sources = [
        item
        for item in requirements
        if item.id in mappings
        and item.themes
        and not is_umbrella(item.themes)
    ]

    summaries: dict[int, dict] = {}
    opportunities = []

    for target in requirements:
        summary = summaries.setdefault(
            target.framework_id,
            {
                "framework_id": target.framework_id,
                "framework_name": target.framework_name,
                "requirement_count": 0,
                "unmapped_requirements": 0,
                "opportunities": 0,
            },
        )

        summary["requirement_count"] += 1

        if target.id in mappings:
            continue

        summary["unmapped_requirements"] += 1

        candidates: dict[int, dict] = {}

        for source in sources:
            if source.framework_id == target.framework_id:
                continue

            confidence = link_confidence(source.themes, target.themes)

            if confidence is None:
                continue

            for control in mappings[source.id]:
                entry = candidates.setdefault(
                    control.id,
                    {
                        "control_id": control.id,
                        "control_title": control.title,
                        "confidence": confidence,
                        "themes": set(),
                        "via": [],
                    },
                )

                entry["themes"] |= source.themes & target.themes
                entry["confidence"] = _better(entry["confidence"], confidence)
                entry["via"].append(_requirement_dict(source))

        if not candidates:
            continue

        candidate_list = []

        for entry in candidates.values():
            themes = entry.pop("themes")
            entry["shared_themes"] = _theme_list(themes)
            candidate_list.append(entry)

        candidate_list.sort(
            key=lambda item: (
                _CONFIDENCE_ORDER[item["confidence"]],
                item["control_id"],
            )
        )

        summary["opportunities"] += 1

        opportunities.append(
            {
                **_requirement_dict(target),
                "best_confidence": candidate_list[0]["confidence"],
                "candidates": candidate_list,
            }
        )

    opportunities.sort(
        key=lambda item: (
            _CONFIDENCE_ORDER[item["best_confidence"]],
            item["framework_name"],
            item["framework_control_id"],
        )
    )

    return {
        "generated_at": datetime.now(timezone.utc),
        "total_requirements": len(requirements),
        "unmapped_requirements": sum(
            summary["unmapped_requirements"]
            for summary in summaries.values()
        ),
        "opportunity_count": len(opportunities),
        "direct_opportunity_count": sum(
            1
            for item in opportunities
            if item["best_confidence"] == "direct"
        ),
        "frameworks": sorted(
            summaries.values(),
            key=lambda summary: summary["framework_name"],
        ),
        "opportunities": opportunities[:MAX_OPPORTUNITIES],
        "disclaimer": DISCLAIMER,
    }
