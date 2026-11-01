from http import HTTPStatus

from fastapi import Depends, Request

from app.models.user import User, UserRole
from core.exceptions import CustomException
from core.factory import Factory
from core.fastapi.dependencies.authentication import AuthenticationRequired


class InsufficientRoleException(CustomException):
    code = HTTPStatus.FORBIDDEN
    error_code = HTTPStatus.FORBIDDEN
    message = "This account does not have access to this interface"


class AdminRequiredException(CustomException):
    code = HTTPStatus.FORBIDDEN
    error_code = HTTPStatus.FORBIDDEN
    message = "Administrator access required"


class RequireRole:
    """
    Backend-side enforcement of the doctor/patient interface split — the
    frontend route guards keep each role out of the other's screens, but
    that alone is cosmetic. This dependency is what actually stops a
    patient account from hitting a doctor-only endpoint (or vice versa),
    since a client can always call the API directly.

    `is_admin` is treated as a superset of every role, matching how the
    lifespan migration backfills pre-existing accounts to `doctor` and how
    `UserPermission` already treats `is_admin` as "can do anything".
    """

    def __init__(self, role: UserRole):
        self.role = role

    async def __call__(
        self,
        request: Request,
        _: None = Depends(AuthenticationRequired),
        user_controller=Depends(Factory().get_user_controller),
    ) -> User:
        user: User = await user_controller.get_by_id(request.user.id)
        if user.role != self.role.value and not user.is_admin:
            raise InsufficientRoleException()
        return user


class AdminRequired:
    async def __call__(
        self,
        request: Request,
        _: None = Depends(AuthenticationRequired),
        user_controller=Depends(Factory().get_user_controller),
    ) -> User:
        user: User = await user_controller.get_by_id(request.user.id)
        if not user.is_admin:
            raise AdminRequiredException()
        return user


RequireDoctor = RequireRole(UserRole.DOCTOR)
RequirePatient = RequireRole(UserRole.PATIENT)
RequireAdmin = AdminRequired()
