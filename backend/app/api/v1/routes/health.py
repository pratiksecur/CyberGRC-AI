from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "CyberGRC AI",
        "version": "1.0.0"
    }