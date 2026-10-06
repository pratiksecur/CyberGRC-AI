from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.auth.permissions import get_access_scope
from app.auth.scopes import AccessScope
from app.auth.visibility import get_visible_user_ids

from app.models.audit import Audit
from app.models.audit_finding import AuditFinding
from app.models.control import Control
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.user import User


# ==========================================================
# PHASE 68 — AUDIT & ASSURANCE AUTOMATION
# ==========================================================

OPEN_FINDING_STATUSES = {
    "open",
    "in progress",
    "pending",
}

CRITICAL_FINDING_SEVERITIES = {
    "critical",
}

OPEN_ACTION_STATUSES = {
    "pending",
    "open",
    "in progress",
}

COMPLETED_ACTION_STATUSES = {
    "completed",
    "closed",
}


# ==========================================================
# HELPERS
# ==========================================================

def _normalise(
    value,
) -> str:
    if value is None:
        return ""

    return str(
        value
    ).strip().lower()


def _today() -> date:
    return datetime.now(
        timezone.utc
    ).date()


def _is_open_finding(
    finding: AuditFinding,
) -> bool:
    return (
        _normalise(
            finding.status
        )
        in OPEN_FINDING_STATUSES
    )


def _is_critical_finding(
    finding: AuditFinding,
) -> bool:
    return (
        _normalise(
            finding.severity
        )
        in CRITICAL_FINDING_SEVERITIES
    )


def _is_open_action(
    action: CorrectiveAction,
) -> bool:
    return (
        _normalise(
            action.status
        )
        in OPEN_ACTION_STATUSES
    )


def _is_completed_action(
    action: CorrectiveAction,
) -> bool:
    return (
        _normalise(
            action.status
        )
        in COMPLETED_ACTION_STATUSES
    )


def _is_overdue_action(
    action: CorrectiveAction,
) -> bool:

    if not _is_open_action(
        action
    ):
        return False

    if action.due_date is None:
        return False

    return (
        action.due_date
        < _today()
    )


def _percentage(
    numerator: int,
    denominator: int,
) -> float:

    if denominator <= 0:
        return 100.0

    return round(
        (
            numerator
            / denominator
        )
        * 100,
        2,
    )


def _planning_complete(
    audit: Audit,
) -> bool:

    if not audit.framework_id:
        return False

    if not audit.auditor_id:
        return False

    if not audit.scope:
        return False

    if not audit.scope.strip():
        return False

    if not audit.start_date:
        return False

    if not audit.end_date:
        return False

    if (
        audit.end_date
        < audit.start_date
    ):
        return False

    return True


def _is_audit_overdue(
    audit: Audit,
) -> bool:

    if _normalise(
        audit.status
    ) in {
        "completed",
        "closed",
    }:
        return False

    if audit.end_date is None:
        return False

    return (
        audit.end_date
        < _today()
    )


# ==========================================================
# PHASE 68 SERVICE
# ==========================================================

def build_audit_assurance(
    db: Session,
    current_user: User,
):
    """
    Build deterministic Audit & Assurance Intelligence.

    Phase 68 is strictly read-only.

    The service analyses:

        Audit
          ↓
        Planning
          ↓
        Findings
          ↓
        Controls
          ↓
        Evidence
          ↓
        Corrective Actions
          ↓
        Closure Readiness

    No audit, finding, control, evidence, or corrective
    action is modified.

    Resource-specific visibility is preserved.
    """

    # ======================================================
    # RESOURCE-SPECIFIC VISIBILITY
    # ======================================================

    audit_visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            "audits",
        )
    )

    finding_visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            "audit_findings",
        )
    )

    action_visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            "corrective_actions",
        )
    )

    evidence_visible_user_ids = set(
        get_visible_user_ids(
            db,
            current_user,
            "evidence",
        )
    )

    # ======================================================
    # AUDITS
    # ======================================================

    audits = (
        db.query(Audit)
        .filter(
            Audit.auditor_id.in_(
                audit_visible_user_ids
            )
        )
        .order_by(
            Audit.end_date.asc(),
            Audit.id.asc(),
        )
        .all()
    )

    audit_ids = {
        audit.id
        for audit in audits
    }

    # ======================================================
    # FINDINGS
    #
    # Findings inherit their parent audit relationship.
    # However, their own resource scope is also respected.
    # ======================================================

    findings = []

    if audit_ids:

        findings = (
            db.query(
                AuditFinding
            )
            .join(
                Audit,
                AuditFinding.audit_id
                == Audit.id,
            )
            .filter(
                AuditFinding.audit_id.in_(
                    audit_ids
                ),
                Audit.auditor_id.in_(
                    finding_visible_user_ids
                ),
            )
            .all()
        )

    finding_ids = {
        finding.id
        for finding in findings
    }

    # ======================================================
    # CORRECTIVE ACTIONS
    #
    # Both:
    #
    #   1. assigned user
    #   2. parent audit
    #
    # must remain within the user's corrective-action
    # visibility boundary.
    # ======================================================

    actions = []

    if finding_ids:

        action_query = (
            db.query(
                CorrectiveAction
            )
            .join(
                AuditFinding,
                CorrectiveAction.finding_id
                == AuditFinding.id,
            )
            .join(
                Audit,
                AuditFinding.audit_id
                == Audit.id,
            )
            .filter(
                CorrectiveAction.finding_id.in_(
                    finding_ids
                ),
                CorrectiveAction.assigned_to.in_(
                    action_visible_user_ids
                ),
            )
        )

        action_scope = get_access_scope(
            current_user,
            "corrective_actions",
        )

        if action_scope in {
            AccessScope.SUBORDINATES,
            AccessScope.ORGANIZATION,
        }:

            action_query = (
                action_query.filter(
                    Audit.auditor_id.in_(
                        action_visible_user_ids
                    )
                )
            )

        actions = (
            action_query
            .all()
        )

    # ======================================================
    # FINDINGS BY AUDIT
    # ======================================================

    findings_by_audit: dict[
        int,
        list[AuditFinding],
    ] = {}

    for finding in findings:

        findings_by_audit.setdefault(
            finding.audit_id,
            [],
        ).append(
            finding
        )

    # ======================================================
    # ACTIONS BY FINDING
    # ======================================================

    actions_by_finding: dict[
        int,
        list[CorrectiveAction],
    ] = {}

    for action in actions:

        actions_by_finding.setdefault(
            action.finding_id,
            [],
        ).append(
            action
        )

    # ======================================================
    # EMPTY PORTFOLIO
    # ======================================================

    if not audits:

        return {
            "generated_at": datetime.now(
                timezone.utc
            ),

            "portfolio": {
                "total_audits": 0,
                "planned": 0,
                "in_progress": 0,
                "completed": 0,
                "overdue": 0,
                "closure_ready": 0,
                "blocked": 0,
            },

            "planning": {
                "complete": 0,
                "incomplete": 0,
                "completion_percent": 100.0,
            },

            "testing": {
                "audits_with_findings": 0,
                "total_findings": 0,
                "open_findings": 0,
                "critical_findings": 0,
                "controls_referenced": 0,
            },

            "evidence": {
                "controls_referenced": 0,
                "controls_with_evidence": 0,
                "controls_without_evidence": 0,
                "coverage_percent": 100.0,
            },

            "remediation": {
                "total_actions": 0,
                "open_actions": 0,
                "completed_actions": 0,
                "overdue_actions": 0,
            },

            "closure": {
                "ready": 0,
                "not_ready": 0,
                "blocked": 0,
            },

            "assurance_signals": [],

            "audits": [],

            "scope": {
                "visible_audit_users": len(
                    audit_visible_user_ids
                ),
                "visible_finding_users": len(
                    finding_visible_user_ids
                ),
                "visible_action_users": len(
                    action_visible_user_ids
                ),
                "visible_evidence_users": len(
                    evidence_visible_user_ids
                ),
                "audit_count": 0,
            },
        }

    # ======================================================
    # AGGREGATES
    # ======================================================

    planned = 0
    in_progress = 0
    completed = 0
    overdue_audits = 0

    planning_complete_count = 0

    audits_with_findings = 0

    total_open_findings = 0
    total_critical_findings = 0

    total_control_references = 0
    total_controls_with_evidence = 0

    total_open_actions = 0
    total_completed_actions = 0
    total_overdue_actions = 0

    closure_ready_count = 0
    blocked_count = 0

    audit_results = []

    # ======================================================
    # AUDIT PROCESSING
    # ======================================================

    for audit in audits:

        audit_findings = (
            findings_by_audit.get(
                audit.id,
                [],
            )
        )

        if audit_findings:
            audits_with_findings += 1

        # --------------------------------------------------
        # Planning
        # --------------------------------------------------

        planning_complete = (
            _planning_complete(
                audit
            )
        )

        if planning_complete:
            planning_complete_count += 1

        # --------------------------------------------------
        # Audit status
        # --------------------------------------------------

        normalized_status = _normalise(
            audit.status
        )

        if normalized_status == "planned":
            planned += 1

        elif normalized_status == "in progress":
            in_progress += 1

        elif normalized_status in {
            "completed",
            "closed",
        }:
            completed += 1

        # --------------------------------------------------
        # Audit overdue
        # --------------------------------------------------

        audit_overdue = (
            _is_audit_overdue(
                audit
            )
        )

        if audit_overdue:
            overdue_audits += 1

        # --------------------------------------------------
        # Findings
        # --------------------------------------------------

        open_findings = [
            finding
            for finding
            in audit_findings
            if _is_open_finding(
                finding
            )
        ]

        critical_findings = [
            finding
            for finding
            in audit_findings
            if _is_critical_finding(
                finding
            )
        ]

        total_open_findings += len(
            open_findings
        )

        total_critical_findings += len(
            critical_findings
        )

        # --------------------------------------------------
        # Controls referenced by audit findings
        # --------------------------------------------------

        control_ids = {
            finding.control_id
            for finding in audit_findings
            if finding.control_id
            is not None
        }

        total_control_references += len(
            control_ids
        )

        # --------------------------------------------------
        # Evidence coverage
        #
        # Evidence is filtered using the existing evidence
        # resource visibility model through control ownership.
        # --------------------------------------------------

        controls_with_evidence = 0

        if control_ids:

            visible_evidence = (
                db.query(Evidence.control_id)
                .filter(
                    Evidence.control_id.in_(
                        control_ids
                    ),
                    Evidence.uploaded_by.in_(
                        evidence_visible_user_ids
                    ),
                )
                .distinct()
                .all()
            )

            evidence_control_ids = {
                control_id
                for (
                    control_id,
                ) in visible_evidence
            }

            controls_with_evidence = len(
                evidence_control_ids
            )

        total_controls_with_evidence += (
            controls_with_evidence
        )

        # --------------------------------------------------
        # Corrective actions
        # --------------------------------------------------

        audit_actions = []

        for finding in audit_findings:

            audit_actions.extend(
                actions_by_finding.get(
                    finding.id,
                    [],
                )
            )

        open_actions = [
            action
            for action
            in audit_actions
            if _is_open_action(
                action
            )
        ]

        completed_actions = [
            action
            for action
            in audit_actions
            if _is_completed_action(
                action
            )
        ]

        overdue_actions = [
            action
            for action
            in audit_actions
            if _is_overdue_action(
                action
            )
        ]

        total_open_actions += len(
            open_actions
        )

        total_completed_actions += len(
            completed_actions
        )

        total_overdue_actions += len(
            overdue_actions
        )

        # --------------------------------------------------
        # Closure blockers
        # --------------------------------------------------

        closure_blockers = []

        if not planning_complete:

            closure_blockers.append(
                "PLANNING_INCOMPLETE"
            )

        if audit_overdue:

            closure_blockers.append(
                "AUDIT_OVERDUE"
            )

        if open_findings:

            closure_blockers.append(
                "OPEN_FINDINGS"
            )

        if critical_findings:

            closure_blockers.append(
                "CRITICAL_FINDINGS"
            )

        if open_actions:

            closure_blockers.append(
                "OPEN_CORRECTIVE_ACTIONS"
            )

        if overdue_actions:

            closure_blockers.append(
                "OVERDUE_CORRECTIVE_ACTIONS"
            )

        # --------------------------------------------------
        # Closure readiness
        #
        # Completed/closed audits are already closed and
        # therefore are not reported as "ready for closure".
        # --------------------------------------------------

        closure_ready = (
            normalized_status
            not in {
                "completed",
                "closed",
            }
            and planning_complete
            and not audit_overdue
            and not open_findings
            and not open_actions
        )

        if closure_ready:

            closure_ready_count += 1

        if closure_blockers:

            blocked_count += 1

        # --------------------------------------------------
        # Per-audit result
        # --------------------------------------------------

        audit_results.append(
            {
                "id": audit.id,
                "name": audit.name,
                "status": audit.status,
                "start_date": audit.start_date,
                "end_date": audit.end_date,
                "overdue": audit_overdue,
                "planning_complete": planning_complete,

                "finding_count": len(
                    audit_findings
                ),

                "open_findings": len(
                    open_findings
                ),

                "critical_findings": len(
                    critical_findings
                ),

                "control_count": len(
                    control_ids
                ),

                "controls_with_evidence": (
                    controls_with_evidence
                ),

                "controls_without_evidence": max(
                    len(control_ids)
                    - controls_with_evidence,
                    0,
                ),

                "corrective_action_count": len(
                    audit_actions
                ),

                "open_corrective_actions": len(
                    open_actions
                ),

                "overdue_corrective_actions": len(
                    overdue_actions
                ),

                "completed_corrective_actions": len(
                    completed_actions
                ),

                "closure_ready": closure_ready,

                "closure_blockers": (
                    closure_blockers
                ),
            }
        )

    # ======================================================
    # EVIDENCE METRICS
    # ======================================================

    controls_without_evidence = max(
        total_control_references
        - total_controls_with_evidence,
        0,
    )

    evidence_coverage = _percentage(
        total_controls_with_evidence,
        total_control_references,
    )

    # ======================================================
    # ASSURANCE SIGNALS
    # ======================================================

    assurance_signals = []

    # ------------------------------------------------------
    # Overdue audits
    # ------------------------------------------------------

    if overdue_audits > 0:

        assurance_signals.append(
            {
                "signal": "OVERDUE_AUDITS",
                "severity": "HIGH",
                "count": overdue_audits,
                "why": (
                    "One or more visible audits have "
                    "passed their planned end date "
                    "without reaching a completed state."
                ),
            }
        )

    # ------------------------------------------------------
    # Critical findings
    # ------------------------------------------------------

    if total_critical_findings > 0:

        assurance_signals.append(
            {
                "signal": "CRITICAL_FINDINGS",
                "severity": "CRITICAL",
                "count": total_critical_findings,
                "why": (
                    "Critical findings remain open "
                    "within the visible audit portfolio."
                ),
            }
        )

    # ------------------------------------------------------
    # Open findings
    # ------------------------------------------------------

    if total_open_findings > 0:

        assurance_signals.append(
            {
                "signal": "OPEN_FINDINGS",
                "severity": "HIGH",
                "count": total_open_findings,
                "why": (
                    "Audit findings remain unresolved "
                    "and may prevent assurance closure."
                ),
            }
        )

    # ------------------------------------------------------
    # Overdue corrective actions
    # ------------------------------------------------------

    if total_overdue_actions > 0:

        assurance_signals.append(
            {
                "signal": "OVERDUE_CORRECTIVE_ACTIONS",
                "severity": "CRITICAL",
                "count": total_overdue_actions,
                "why": (
                    "Corrective actions have exceeded "
                    "their due dates without completion."
                ),
            }
        )

    # ------------------------------------------------------
    # Evidence gaps
    # ------------------------------------------------------

    if controls_without_evidence > 0:

        assurance_signals.append(
            {
                "signal": "EVIDENCE_GAPS",
                "severity": "MEDIUM",
                "count": controls_without_evidence,
                "why": (
                    "Controls referenced by audit findings "
                    "do not all have visible supporting evidence."
                ),
            }
        )

    # ------------------------------------------------------
    # Planning gaps
    # ------------------------------------------------------

    planning_incomplete = (
        len(audits)
        - planning_complete_count
    )

    if planning_incomplete > 0:

        assurance_signals.append(
            {
                "signal": "INCOMPLETE_AUDIT_PLANNING",
                "severity": "MEDIUM",
                "count": planning_incomplete,
                "why": (
                    "One or more audits are missing "
                    "required planning information."
                ),
            }
        )

    # ------------------------------------------------------
    # Closure readiness
    # ------------------------------------------------------

    if closure_ready_count > 0:

        assurance_signals.append(
            {
                "signal": "AUDITS_READY_FOR_CLOSURE",
                "severity": "INFO",
                "count": closure_ready_count,
                "why": (
                    "Audits satisfy the deterministic "
                    "Phase 68 closure-readiness checks."
                ),
            }
        )

    # ======================================================
    # FINAL RESPONSE
    # ======================================================

    return {
        "generated_at": datetime.now(
            timezone.utc
        ),

        "portfolio": {
            "total_audits": len(
                audits
            ),
            "planned": planned,
            "in_progress": in_progress,
            "completed": completed,
            "overdue": overdue_audits,
            "closure_ready": closure_ready_count,
            "blocked": blocked_count,
        },

        "planning": {
            "complete": planning_complete_count,
            "incomplete": planning_incomplete,
            "completion_percent": _percentage(
                planning_complete_count,
                len(audits),
            ),
        },

        "testing": {
            "audits_with_findings": (
                audits_with_findings
            ),
            "total_findings": len(
                findings
            ),
            "open_findings": (
                total_open_findings
            ),
            "critical_findings": (
                total_critical_findings
            ),
            "controls_referenced": (
                total_control_references
            ),
        },

        "evidence": {
            "controls_referenced": (
                total_control_references
            ),
            "controls_with_evidence": (
                total_controls_with_evidence
            ),
            "controls_without_evidence": (
                controls_without_evidence
            ),
            "coverage_percent": (
                evidence_coverage
            ),
        },

        "remediation": {
            "total_actions": len(
                actions
            ),
            "open_actions": (
                total_open_actions
            ),
            "completed_actions": (
                total_completed_actions
            ),
            "overdue_actions": (
                total_overdue_actions
            ),
        },

        "closure": {
            "ready": closure_ready_count,
            "not_ready": (
                len(audits)
                - closure_ready_count
            ),
            "blocked": blocked_count,
        },

        "assurance_signals": (
            assurance_signals
        ),

        "audits": audit_results,

        "scope": {
            "visible_audit_users": len(
                audit_visible_user_ids
            ),
            "visible_finding_users": len(
                finding_visible_user_ids
            ),
            "visible_action_users": len(
                action_visible_user_ids
            ),
            "visible_evidence_users": len(
                evidence_visible_user_ids
            ),
            "audit_count": len(
                audits
            ),
        },
    }