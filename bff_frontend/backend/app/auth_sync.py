"""Sync JWT auth helper for RS routes (no async needed)."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import get_settings

settings = get_settings()
_security = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
) -> str | None:
    """Extract user_id from JWT. Returns None if no token or invalid token."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None


def require_user_id(
    user_id: str | None = Depends(get_current_user_id),
) -> str:
    """Require authentication — raises 401 if no valid token."""
    if not user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id
