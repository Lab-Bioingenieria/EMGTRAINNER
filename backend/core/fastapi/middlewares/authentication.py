from typing import Optional, Tuple

from starlette.authentication import AuthCredentials, AuthenticationBackend
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection

from app.schemas.extras.current_user import CurrentUser
from core.security.jwt import JWTDecodeError, JWTExpiredError, JWTHandler


class AuthBackend(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple[AuthCredentials, CurrentUser]]:
        authorization: str = conn.headers.get("Authorization")
        if not authorization:
            return None

        try:
            scheme, token = authorization.split(" ")
            if scheme.lower() != "bearer":
                return None
        except ValueError:
            return None

        if not token:
            return None

        try:
            payload = JWTHandler.decode(token)
            user_id = payload.get("user_id")
        except (JWTDecodeError, JWTExpiredError):
            return None

        if user_id is None:
            return None

        return AuthCredentials(["authenticated"]), CurrentUser(id=user_id)


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass
