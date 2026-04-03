import os
import logging
from fastapi import HTTPException, status, Header
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth, credentials
except Exception:
    firebase_admin = None
    firebase_auth = None
    credentials = None


def init_firebase_admin():
    """Initialize the firebase_admin SDK if not already initialized."""
    if not firebase_admin:
        logger.warning("firebase_admin package not available; server-side token verification disabled.")
        return
    if firebase_admin._apps:
        return
    sa_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    try:
        if sa_path and os.path.exists(sa_path):
            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred)
            logger.info("Initialized firebase_admin with service account %s", sa_path)
        else:
            firebase_admin.initialize_app()
            logger.info("Initialized firebase_admin with application default credentials")
    except Exception as e:
        logger.exception("Failed to initialize firebase_admin: %s", e)


def get_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be a Bearer token",
        )
    return parts[1]


async def verify_firebase_token(authorization: Optional[str] = Header(None)) -> dict:
    """FastAPI dependency to verify Firebase ID token from Authorization header.

    Returns the decoded token on success. Raises HTTPException(401) on failure.
    """
    init_firebase_admin()
    if not firebase_auth:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server does not support Firebase token verification (missing firebase_admin)."
        )
    token = get_bearer_token(authorization)
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        logger.warning("Invalid Firebase ID token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )
