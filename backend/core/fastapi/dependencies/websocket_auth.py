"""Authentication guard for WebSocket endpoints.

HTTP dependencies (HTTPBearer) cannot be reused on WebSocket routes, so this
helper validates the bearer token from the `Authorization` header or the
`token` query parameter and closes the socket with a policy-violation code
when it is missing or invalid.
"""
from typing import Optional

from fastapi import WebSocket

from app.schemas.extras.current_user import CurrentUser
from core.security.jwt import JWTDecodeError, JWTExpiredError, JWTHandler

WS_POLICY_VIOLATION = 1008


def _extract_token(websocket: WebSocket) -> Optional[str]:
    authorization = websocket.headers.get("Authorization")
    if authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1]:
            return parts[1]
        return None

    return websocket.query_params.get("token") or None


async def authenticate_websocket(websocket: WebSocket) -> Optional[CurrentUser]:
    """Return the authenticated user, or close the socket and return None."""
    token = _extract_token(websocket)
    if not token:
        await websocket.close(code=WS_POLICY_VIOLATION)
        return None

    try:
        payload = JWTHandler.decode(token)
    except (JWTDecodeError, JWTExpiredError):
        await websocket.close(code=WS_POLICY_VIOLATION)
        return None

    user_id = payload.get("user_id")
    if user_id is None:
        await websocket.close(code=WS_POLICY_VIOLATION)
        return None

    await websocket.accept()
    return CurrentUser(id=user_id)
