from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User


def require_roles(*allowed_roles):
    def role_checker(current_user: User = Depends(get_current_user)):

        allowed_values = [
            role.value if hasattr(role, "value") else role
            for role in allowed_roles
        ]

        if current_user.role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action."
            )

        return current_user

    return role_checker