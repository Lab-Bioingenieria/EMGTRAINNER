from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.exceptions.base import CustomException


class AuthenticationRequiredException(CustomException):
    code = status.HTTP_401_UNAUTHORIZED
    error_code = status.HTTP_401_UNAUTHORIZED
    message = "Authentication required"


class AuthenticationRequired:
    def __init__(
        self,
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    ):
        user = request.user
        if not token or not getattr(user, "is_authenticated", False):
            raise AuthenticationRequiredException()
