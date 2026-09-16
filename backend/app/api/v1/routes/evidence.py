from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_user_in_scope

from app.models.user import User
from app.models.evidence import Evidence
from app.models.control import Control

from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
)

from app.services.evidence_service import (
    create_evidence,
    update_evidence,
    delete_evidence,
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


router = APIRouter(
    prefix="/evidence",
    tags=["Evidence Management"],
)


@router.post(
    "/",
    response_model=EvidenceResponse,
)
def create_new_evidence(
    control_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "evidence",
            "create",
        )
    ),
):
    """
    Upload evidence for a control.

    The uploader is always the authenticated user.
    """

    # ------------------------------------------------------
    # Verify control exists
    # ------------------------------------------------------

    control = (
        db.query(Control)
        .filter(Control.id == control_id)
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found.",
        )

    # ------------------------------------------------------
    # Verify control owner is within user's scope
    # ------------------------------------------------------

    ensure_user_in_scope(
        db,
        current_user,
        control.owner_id,
        "evidence",
    )

    # ------------------------------------------------------
    # Save uploaded file
    # ------------------------------------------------------

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer,
        )

    # ------------------------------------------------------
    # Create evidence
    # ------------------------------------------------------

    evidence_data = EvidenceCreate(
        control_id=control_id,
        title=title,
        description=description,
        file_name=safe_filename,
        file_path=str(file_path),
    )

    evidence = create_evidence(
        db,
        evidence_data,
        current_user.id,
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Unable to create evidence.",
        )

    return evidence


@router.get(
    "/",
    response_model=list[EvidenceResponse],
)
def list_all_evidence(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "evidence",
            "view",
        )
    ),
):
    """
    Get evidence attached to controls
    within the current user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "evidence",
    )

    return (
        db.query(Evidence)
        .join(
            Control,
            Evidence.control_id == Control.id,
        )
        .filter(
            Control.owner_id.in_(visible_user_ids)
        )
        .all()
    )


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "evidence",
            "view",
        )
    ),
):
    """
    Get evidence by ID if its associated control
    is within the current user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "evidence",
    )

    evidence = (
        db.query(Evidence)
        .join(
            Control,
            Evidence.control_id == Control.id,
        )
        .filter(
            Evidence.id == evidence_id,
            Control.owner_id.in_(visible_user_ids),
        )
        .first()
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    return evidence


@router.patch(
    "/{evidence_id}",
    response_model=EvidenceResponse,
)
def update_existing_evidence(
    evidence_id: int,
    evidence_data: EvidenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "evidence",
            "update",
        )
    ),
):
    """
    Update evidence attached to a control
    within the user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "evidence",
    )

    evidence = (
        db.query(Evidence)
        .join(
            Control,
            Evidence.control_id == Control.id,
        )
        .filter(
            Evidence.id == evidence_id,
            Control.owner_id.in_(visible_user_ids),
        )
        .first()
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    updated_evidence = update_evidence(
        db,
        evidence_id,
        evidence_data,
    )

    if updated_evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    return updated_evidence


@router.delete(
    "/{evidence_id}",
)
def delete_existing_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "evidence",
            "delete",
        )
    ),
):
    """
    Delete evidence attached to a control
    within the user's organizational scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "evidence",
    )

    evidence = (
        db.query(Evidence)
        .join(
            Control,
            Evidence.control_id == Control.id,
        )
        .filter(
            Evidence.id == evidence_id,
            Control.owner_id.in_(visible_user_ids),
        )
        .first()
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    deleted = delete_evidence(
        db,
        evidence_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found.",
        )

    return {
        "message": "Evidence deleted successfully.",
    }