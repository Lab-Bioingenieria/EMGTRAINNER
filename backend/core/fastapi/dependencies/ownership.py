"""Minimal ownership boundary helpers.

Only resources that already carry an owner column are covered. Anything without
a persisted user linkage (for example raw session folders under
`backend/storage/sessions`) is deliberately not handled here.
"""

from fastapi import Request, status

from core.exceptions.base import CustomException


class OwnershipRequiredException(CustomException):
    code = status.HTTP_403_FORBIDDEN
    error_code = status.HTTP_403_FORBIDDEN
    message = "You do not have access to this resource"


def current_user_id(request: Request) -> str:
    """Return the authenticated user identity used as the resource owner value."""
    user = getattr(request, "user", None)
    user_id = getattr(user, "id", None)
    if user_id is None:
        raise OwnershipRequiredException()
    return str(user_id)


def ensure_owner(resource, user_id: str, owner_field: str = "created_by") -> None:
    """Raise 403 when `resource` is not owned by `user_id`."""
    owner = getattr(resource, owner_field, None)
    if owner is None or str(owner) != str(user_id):
        raise OwnershipRequiredException()
