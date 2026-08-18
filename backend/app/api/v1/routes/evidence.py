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
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
)

from app.services.evidence_service import (
    create_evidence,
    get_all_evidence,
    get_evidence_by_id,
    update_evidence,
    delete_evidence,
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(
    prefix="/evidence",
    tags=["Evidence Management"]
)


@router.post(
    "/",
    response_model=EvidenceResponse
)
def create_new_evidence(
    control_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    uploaded_by: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.RISK_ANALYST,
        )
    )
):
    """
    Upload evidence with a real file.
    """

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    evidence_data = EvidenceCreate(
        control_id=control_id,
        title=title,
        description=description,
        file_name=file.filename,
        file_path=str(file_path),
        uploaded_by=uploaded_by,
    )

    evidence = create_evidence(
        db,
        evidence_data
    )

    if evidence == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    if evidence == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return evidence


@router.get(
    "/",
    response_model=list[EvidenceResponse]
)
def list_all_evidence(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get all evidence.
    """

    return get_all_evidence(db)


@router.get(
    "/{evidence_id}",
    response_model=EvidenceResponse
)
def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get evidence by ID.
    """

    evidence = get_evidence_by_id(
        db,
        evidence_id
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    return evidence


@router.patch(
    "/{evidence_id}",
    response_model=EvidenceResponse
)
def update_existing_evidence(
    evidence_id: int,
    evidence_data: EvidenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Update evidence.
    """

    evidence = update_evidence(
        db,
        evidence_id,
        evidence_data,
    )

    if evidence is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    return evidence


@router.delete(
    "/{evidence_id}"
)
def delete_existing_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Delete evidence.
    """

    deleted = delete_evidence(
        db,
        evidence_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found."
        )

    return {
        "message": "Evidence deleted successfully."
    }