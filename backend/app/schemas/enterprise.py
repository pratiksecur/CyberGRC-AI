from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ==========================================================
# BUSINESS UNITS
# ==========================================================


class BusinessUnitCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    is_active: bool = True


class BusinessUnitUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    is_active: bool | None = None


class BusinessUnitResponse(BaseModel):

    id: int
    organization_id: int
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# DEPARTMENTS
# ==========================================================


class DepartmentCreate(BaseModel):

    business_unit_id: int

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    is_active: bool = True


class DepartmentUpdate(BaseModel):

    business_unit_id: int | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = None

    is_active: bool | None = None


class DepartmentResponse(BaseModel):

    id: int
    organization_id: int
    business_unit_id: int
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# GRC TEAMS
# ==========================================================


class GrcTeamCreate(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    business_unit_id: int | None = None

    department_id: int | None = None

    description: str | None = None

    is_active: bool = True


class GrcTeamUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    business_unit_id: int | None = None

    department_id: int | None = None

    description: str | None = None

    is_active: bool | None = None


class GrcTeamResponse(BaseModel):

    id: int
    organization_id: int
    business_unit_id: int | None
    department_id: int | None
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# ENTERPRISE CONFIGURATION
# ==========================================================


class EnterpriseConfigurationUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    timezone: str = Field(
        default="UTC",
        min_length=1,
        max_length=100,
    )

    default_risk_threshold: int = Field(
        default=15,
        ge=1,
        le=100,
    )

    critical_risk_threshold: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    critical_risk_notification_threshold: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    ineffective_control_threshold: int = Field(
        default=50,
        ge=0,
        le=100,
    )

    stale_evidence_days: int = Field(
        default=90,
        ge=1,
        le=3650,
    )

    treatment_stuck_days: int = Field(
        default=30,
        ge=1,
        le=3650,
    )

    treatment_residual_threshold: int = Field(
        default=15,
        ge=1,
        le=100,
    )

    continuous_risk_reassessment_enabled: bool = True

    notifications_enabled: bool = True

    ai_enabled: bool = True

    @model_validator(mode="after")
    def validate_threshold_relationships(self):

        if (
            self.default_risk_threshold
            > self.critical_risk_threshold
        ):
            raise ValueError(
                "default_risk_threshold cannot exceed "
                "critical_risk_threshold."
            )

        if (
            self.critical_risk_notification_threshold
            < self.critical_risk_threshold
        ):
            raise ValueError(
                "critical_risk_notification_threshold "
                "cannot be lower than "
                "critical_risk_threshold."
            )

        return self


class EnterpriseConfigurationResponse(
    EnterpriseConfigurationUpdate
):

    id: int

    organization_id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# USER ENTERPRISE STRUCTURE
# ==========================================================


class UserEnterpriseStructureUpdate(BaseModel):

    business_unit_id: int | None = None

    department_id: int | None = None

    team_id: int | None = None