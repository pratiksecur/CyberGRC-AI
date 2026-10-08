from sqlalchemy.orm import Session

from app.models.enterprise_configuration import (
    EnterpriseConfiguration,
)
from app.models.user import User
from app.schemas.enterprise import (
    EnterpriseConfigurationUpdate,
)


# ==========================================================
# DEFAULTS
# ==========================================================

DEFAULT_ENTERPRISE_CONFIGURATION = {
    "timezone": "UTC",
    "default_risk_threshold": 15,
    "critical_risk_threshold": 20,
    "critical_risk_notification_threshold": 20,
    "ineffective_control_threshold": 50,
    "stale_evidence_days": 90,
    "treatment_stuck_days": 30,
    "treatment_residual_threshold": 15,
    "continuous_risk_reassessment_enabled": True,
    "notifications_enabled": True,
    "ai_enabled": True,
}


# ==========================================================
# GET
# ==========================================================


def get_enterprise_configuration(
    db: Session,
    current_user: User,
) -> EnterpriseConfiguration | None:

    return (
        db.query(EnterpriseConfiguration)
        .filter(
            EnterpriseConfiguration.organization_id
            == current_user.organization_id,
        )
        .first()
    )


# ==========================================================
# GET OR CREATE
# ==========================================================


def get_or_create_enterprise_configuration(
    db: Session,
    current_user: User,
) -> EnterpriseConfiguration:

    configuration = get_enterprise_configuration(
        db,
        current_user,
    )

    if configuration is not None:
        return configuration

    configuration = EnterpriseConfiguration(
        organization_id=current_user.organization_id,
        **DEFAULT_ENTERPRISE_CONFIGURATION,
    )

    db.add(configuration)
    db.commit()
    db.refresh(configuration)

    return configuration


# ==========================================================
# UPDATE
# ==========================================================


def update_enterprise_configuration(
    db: Session,
    current_user: User,
    data: EnterpriseConfigurationUpdate,
) -> EnterpriseConfiguration:

    configuration = (
        get_or_create_enterprise_configuration(
            db,
            current_user,
        )
    )

    configuration.timezone = data.timezone

    configuration.default_risk_threshold = (
        data.default_risk_threshold
    )

    configuration.critical_risk_threshold = (
        data.critical_risk_threshold
    )

    configuration.critical_risk_notification_threshold = (
        data.critical_risk_notification_threshold
    )

    configuration.ineffective_control_threshold = (
        data.ineffective_control_threshold
    )

    configuration.stale_evidence_days = (
        data.stale_evidence_days
    )

    configuration.treatment_stuck_days = (
        data.treatment_stuck_days
    )

    configuration.treatment_residual_threshold = (
        data.treatment_residual_threshold
    )

    configuration.continuous_risk_reassessment_enabled = (
        data.continuous_risk_reassessment_enabled
    )

    configuration.notifications_enabled = (
        data.notifications_enabled
    )

    configuration.ai_enabled = (
        data.ai_enabled
    )

    # ------------------------------------------------------
    # IMPORTANT:
    # organization_id is intentionally NEVER assigned from
    # request data.
    #
    # It remains permanently bound to:
    #
    # current_user.organization_id
    # ------------------------------------------------------

    db.commit()
    db.refresh(configuration)

    return configuration