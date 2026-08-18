from __future__ import annotations

import os
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


def require_jwt(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token required")

    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT validation is not configured")

    try:
        claims = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")],
            issuer=os.getenv("JWT_ISSUER") or None,
            audience=os.getenv("JWT_AUDIENCE") or None,
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token") from exc

    client_id = claims.get("client_id", claims.get("sub"))
    if not isinstance(client_id, str) or not client_id.strip():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="JWT has no valid client identity")

    claims["client_id"] = client_id
    return claims
