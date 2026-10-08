from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_permission
from app.database.database import get_db

from app.models.business_unit import BusinessUnit
from app.models.department import Department

from app.models.grc_team import GrcTeam
from app.models.user import User

from app.schemas.enterprise import (
    BusinessUnitCreate,
    BusinessUnitResponse,
    BusinessUnitUpdate,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    EnterpriseConfigurationResponse,
    EnterpriseConfigurationUpdate,
    GrcTeamCreate,
    GrcTeamResponse,
    GrcTeamUpdate,
    UserEnterpriseStructureUpdate,
)

from app.services.enterprise_configuration_service import (
    get_or_create_enterprise_configuration,
    update_enterprise_configuration,
)

router = APIRouter(
    prefix="/enterprise",
    tags=["Enterprise Architecture"],
)


# ==========================================================
# HELPERS
# ==========================================================


def _get_business_unit(
    db: Session,
    current_user: User,
    business_unit_id: int,
):
    return (
        db.query(BusinessUnit)
        .filter(
            BusinessUnit.id == business_unit_id,
            BusinessUnit.organization_id
            == current_user.organization_id,
        )
        .first()
    )


def _get_department(
    db: Session,
    current_user: User,
    department_id: int,
):
    return (
        db.query(Department)
        .filter(
            Department.id == department_id,
            Department.organization_id
            == current_user.organization_id,
        )
        .first()
    )


def _get_team(
    db: Session,
    current_user: User,
    team_id: int,
):
    return (
        db.query(GrcTeam)
        .filter(
            GrcTeam.id == team_id,
            GrcTeam.organization_id
            == current_user.organization_id,
        )
        .first()
    )


def _validate_department_relationships(
    db: Session,
    current_user: User,
    business_unit_id: int,
):
    business_unit = _get_business_unit(
        db,
        current_user,
        business_unit_id,
    )

    if business_unit is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Business unit does not belong "
                "to the current organization."
            ),
        )

    return business_unit


def _validate_team_relationships(
    db: Session,
    current_user: User,
    business_unit_id: int | None,
    department_id: int | None,
):
    business_unit = None
    department = None

    if business_unit_id is not None:
        business_unit = _get_business_unit(
            db,
            current_user,
            business_unit_id,
        )

        if business_unit is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Business unit does not belong "
                    "to the current organization."
                ),
            )

    if department_id is not None:
        department = _get_department(
            db,
            current_user,
            department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Department does not belong "
                    "to the current organization."
                ),
            )

        if (
            business_unit_id is not None
            and department.business_unit_id
            != business_unit_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Department does not belong "
                    "to the selected business unit."
                ),
            )

    return business_unit, department


# ==========================================================
# BUSINESS UNITS
# ==========================================================


@router.get(
    "/business-units",
    response_model=list[BusinessUnitResponse],
)
def list_business_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "business_units",
            "view",
        )
    ),
):
    return (
        db.query(BusinessUnit)
        .filter(
            BusinessUnit.organization_id
            == current_user.organization_id,
        )
        .order_by(BusinessUnit.name)
        .all()
    )


@router.post(
    "/business-units",
    response_model=BusinessUnitResponse,
)
def create_business_unit(
    data: BusinessUnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "business_units",
            "create",
        )
    ),
):
    existing = (
        db.query(BusinessUnit)
        .filter(
            BusinessUnit.organization_id
            == current_user.organization_id,
            (
                (BusinessUnit.name == data.name)
                | (BusinessUnit.slug == data.slug)
            ),
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business unit already exists.",
        )

    business_unit = BusinessUnit(
        organization_id=current_user.organization_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        is_active=data.is_active,
    )

    db.add(business_unit)
    db.commit()
    db.refresh(business_unit)

    return business_unit


@router.get(
    "/business-units/{business_unit_id}",
    response_model=BusinessUnitResponse,
)
def get_business_unit(
    business_unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "business_units",
            "view",
        )
    ),
):
    business_unit = _get_business_unit(
        db,
        current_user,
        business_unit_id,
    )

    if business_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business unit not found.",
        )

    return business_unit


@router.patch(
    "/business-units/{business_unit_id}",
    response_model=BusinessUnitResponse,
)
def update_business_unit(
    business_unit_id: int,
    data: BusinessUnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "business_units",
            "update",
        )
    ),
):
    business_unit = _get_business_unit(
        db,
        current_user,
        business_unit_id,
    )

    if business_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business unit not found.",
        )

    if data.name is not None:
        business_unit.name = data.name

    if data.slug is not None:
        business_unit.slug = data.slug

    if data.description is not None:
        business_unit.description = data.description

    if data.is_active is not None:
        business_unit.is_active = data.is_active

    duplicate = (
        db.query(BusinessUnit)
        .filter(
            BusinessUnit.organization_id
            == current_user.organization_id,
            BusinessUnit.id != business_unit.id,
            (
                (BusinessUnit.name == business_unit.name)
                | (BusinessUnit.slug == business_unit.slug)
            ),
        )
        .first()
    )

    if duplicate is not None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business unit already exists.",
        )

    db.commit()
    db.refresh(business_unit)

    return business_unit


@router.delete(
    "/business-units/{business_unit_id}",
)
def delete_business_unit(
    business_unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "business_units",
            "delete",
        )
    ),
):
    business_unit = _get_business_unit(
        db,
        current_user,
        business_unit_id,
    )

    if business_unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business unit not found.",
        )

    if (
        business_unit.departments
        or business_unit.teams
        or business_unit.users
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Business unit cannot be deleted while "
                "it contains departments, teams, or users."
            ),
        )

    db.delete(business_unit)
    db.commit()

    return {
        "message": "Business unit deleted successfully."
    }


# ==========================================================
# DEPARTMENTS
# ==========================================================


@router.get(
    "/departments",
    response_model=list[DepartmentResponse],
)
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "departments",
            "view",
        )
    ),
):
    return (
        db.query(Department)
        .filter(
            Department.organization_id
            == current_user.organization_id,
        )
        .order_by(Department.name)
        .all()
    )


@router.post(
    "/departments",
    response_model=DepartmentResponse,
)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "departments",
            "create",
        )
    ),
):
    _validate_department_relationships(
        db,
        current_user,
        data.business_unit_id,
    )

    existing = (
        db.query(Department)
        .filter(
            Department.organization_id
            == current_user.organization_id,
            (
                (Department.name == data.name)
                | (Department.slug == data.slug)
            ),
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department already exists.",
        )

    department = Department(
        organization_id=current_user.organization_id,
        business_unit_id=data.business_unit_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        is_active=data.is_active,
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


@router.get(
    "/departments/{department_id}",
    response_model=DepartmentResponse,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "departments",
            "view",
        )
    ),
):
    department = _get_department(
        db,
        current_user,
        department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    return department


@router.patch(
    "/departments/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "departments",
            "update",
        )
    ),
):
    department = _get_department(
        db,
        current_user,
        department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    if data.business_unit_id is not None:
        _validate_department_relationships(
            db,
            current_user,
            data.business_unit_id,
        )

        department.business_unit_id = (
            data.business_unit_id
        )

    if data.name is not None:
        department.name = data.name

    if data.slug is not None:
        department.slug = data.slug

    if data.description is not None:
        department.description = data.description

    if data.is_active is not None:
        department.is_active = data.is_active

    duplicate = (
        db.query(Department)
        .filter(
            Department.organization_id
            == current_user.organization_id,
            Department.id != department.id,
            (
                (Department.name == department.name)
                | (Department.slug == department.slug)
            ),
        )
        .first()
    )

    if duplicate is not None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department already exists.",
        )

    db.commit()
    db.refresh(department)

    return department


@router.delete(
    "/departments/{department_id}",
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "departments",
            "delete",
        )
    ),
):
    department = _get_department(
        db,
        current_user,
        department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found.",
        )

    if department.teams or department.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Department cannot be deleted while "
                "it contains teams or users."
            ),
        )

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully."
    }


# ==========================================================
# GRC TEAMS
# ==========================================================


@router.get(
    "/teams",
    response_model=list[GrcTeamResponse],
)
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "grc_teams",
            "view",
        )
    ),
):
    return (
        db.query(GrcTeam)
        .filter(
            GrcTeam.organization_id
            == current_user.organization_id,
        )
        .order_by(GrcTeam.name)
        .all()
    )


@router.post(
    "/teams",
    response_model=GrcTeamResponse,
)
def create_team(
    data: GrcTeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "grc_teams",
            "create",
        )
    ),
):
    _validate_team_relationships(
        db,
        current_user,
        data.business_unit_id,
        data.department_id,
    )

    existing = (
        db.query(GrcTeam)
        .filter(
            GrcTeam.organization_id
            == current_user.organization_id,
            (
                (GrcTeam.name == data.name)
                | (GrcTeam.slug == data.slug)
            ),
        )
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="GRC team already exists.",
        )

    team = GrcTeam(
        organization_id=current_user.organization_id,
        business_unit_id=data.business_unit_id,
        department_id=data.department_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        is_active=data.is_active,
    )

    db.add(team)
    db.commit()
    db.refresh(team)

    return team


@router.get(
    "/teams/{team_id}",
    response_model=GrcTeamResponse,
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "grc_teams",
            "view",
        )
    ),
):
    team = _get_team(
        db,
        current_user,
        team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRC team not found.",
        )

    return team


@router.patch(
    "/teams/{team_id}",
    response_model=GrcTeamResponse,
)
def update_team(
    team_id: int,
    data: GrcTeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "grc_teams",
            "update",
        )
    ),
):
    team = _get_team(
        db,
        current_user,
        team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRC team not found.",
        )

    business_unit_id = (
        data.business_unit_id
        if data.business_unit_id is not None
        else team.business_unit_id
    )

    department_id = (
        data.department_id
        if data.department_id is not None
        else team.department_id
    )

    _validate_team_relationships(
        db,
        current_user,
        business_unit_id,
        department_id,
    )

    if data.business_unit_id is not None:
        team.business_unit_id = (
            data.business_unit_id
        )

    if data.department_id is not None:
        team.department_id = (
            data.department_id
        )

    if data.name is not None:
        team.name = data.name

    if data.slug is not None:
        team.slug = data.slug

    if data.description is not None:
        team.description = data.description

    if data.is_active is not None:
        team.is_active = data.is_active

    duplicate = (
        db.query(GrcTeam)
        .filter(
            GrcTeam.organization_id
            == current_user.organization_id,
            GrcTeam.id != team.id,
            (
                (GrcTeam.name == team.name)
                | (GrcTeam.slug == team.slug)
            ),
        )
        .first()
    )

    if duplicate is not None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="GRC team already exists.",
        )

    db.commit()
    db.refresh(team)

    return team


@router.delete(
    "/teams/{team_id}",
)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "grc_teams",
            "delete",
        )
    ),
):
    team = _get_team(
        db,
        current_user,
        team_id,
    )

    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GRC team not found.",
        )

    if team.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "GRC team cannot be deleted while "
                "users are assigned to it."
            ),
        )

    db.delete(team)
    db.commit()

    return {
        "message": "GRC team deleted successfully."
    }


# ==========================================================
# USER STRUCTURE ASSIGNMENT
# ==========================================================


@router.patch(
    "/users/{user_id}/structure",
)
def update_user_structure(
    user_id: int,
    data: UserEnterpriseStructureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "enterprise_structure",
            "update",
        )
    ),
):
    target_user = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if data.business_unit_id is not None:
        business_unit = _get_business_unit(
            db,
            current_user,
            data.business_unit_id,
        )

        if business_unit is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Business unit does not belong "
                    "to the current organization."
                ),
            )

        target_user.business_unit_id = (
            data.business_unit_id
        )
    else:
        target_user.business_unit_id = None

    if data.department_id is not None:
        department = _get_department(
            db,
            current_user,
            data.department_id,
        )

        if department is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Department does not belong "
                    "to the current organization."
                ),
            )

        if (
            target_user.business_unit_id is not None
            and department.business_unit_id
            != target_user.business_unit_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Department does not belong "
                    "to the selected business unit."
                ),
            )

        target_user.department_id = (
            data.department_id
        )
        target_user.department = (
            department.name
        )
    else:
        target_user.department_id = None

    if data.team_id is not None:
        team = _get_team(
            db,
            current_user,
            data.team_id,
        )

        if team is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "GRC team does not belong "
                    "to the current organization."
                ),
            )

        if (
            target_user.business_unit_id is not None
            and team.business_unit_id is not None
            and team.business_unit_id
            != target_user.business_unit_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "GRC team does not belong "
                    "to the selected business unit."
                ),
            )

        if (
            target_user.department_id is not None
            and team.department_id is not None
            and team.department_id
            != target_user.department_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "GRC team does not belong "
                    "to the selected department."
                ),
            )

        target_user.team_id = data.team_id
    else:
        target_user.team_id = None

    db.commit()
    db.refresh(target_user)

    return {
        "message": (
            "User enterprise structure updated successfully."
        ),
        "user_id": target_user.id,
        "organization_id": target_user.organization_id,
        "business_unit_id": target_user.business_unit_id,
        "department_id": target_user.department_id,
        "team_id": target_user.team_id,
    }


# ==========================================================
# ENTERPRISE CONFIGURATION
# ==========================================================


@router.get(
    "/configuration",
    response_model=EnterpriseConfigurationResponse,
)
def get_enterprise_configuration_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "enterprise_configuration",
            "view",
        )
    ),
):
    """
    Return the enterprise configuration belonging to the
    authenticated user's organization.

    The tenant is always derived from current_user.
    """

    return get_or_create_enterprise_configuration(
        db,
        current_user,
    )


@router.put(
    "/configuration",
    response_model=EnterpriseConfigurationResponse,
)
def update_enterprise_configuration_endpoint(
    data: EnterpriseConfigurationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "enterprise_configuration",
            "update",
        )
    ),
):
    """
    Update the enterprise configuration for the authenticated
    user's organization.

    organization_id is never accepted from the request body.
    """

    return update_enterprise_configuration(
        db,
        current_user,
        data,
    )