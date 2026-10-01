from typing import Callable

from fastapi import APIRouter, Depends

from app.controllers import AuthController, UserController
from app.models.user import User, UserPermission
from app.schemas.extras.token import Token
from app.schemas.requests.users import (
    LoginUserRequest,
    RegisterDoctorRequest,
    RegisterUserRequest,
)
from app.schemas.responses.users import UserResponse
from core.factory import Factory
from core.fastapi.dependencies import AuthenticationRequired
from core.fastapi.dependencies.current_user import get_current_user
from core.fastapi.dependencies.permissions import Permissions
from core.fastapi.dependencies.role import RequireAdmin

user_router = APIRouter()


@user_router.get("/", dependencies=[Depends(AuthenticationRequired)])
async def get_users(
    user_controller: UserController = Depends(Factory().get_user_controller),
    assert_access: Callable = Depends(Permissions(UserPermission.READ)),
) -> list[UserResponse]:
    users = await user_controller.get_all()

    assert_access(resource=users)
    return users


@user_router.post("/", status_code=201)
async def register_user(
    register_user_request: RegisterUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> UserResponse:
    """
    Public patient sign-up. There is no way to request a doctor account
    here — see `POST /users/doctors` for that. This is the "patient
    database generated from user registration" path.
    """
    return await auth_controller.register(
        email=register_user_request.email,
        password=register_user_request.password,
        username=register_user_request.username,
        age=register_user_request.age,
    )


@user_router.post(
    "/doctors", status_code=201, dependencies=[Depends(RequireAdmin)]
)
async def register_doctor(
    register_doctor_request: RegisterDoctorRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> UserResponse:
    """
    Administrative doctor provisioning. Requires an already-authenticated
    admin account — a doctor is never created by public self-registration.
    For a bulk import from externally-maintained data, use
    `backend/seed_doctors.py` instead.
    """
    return await auth_controller.register_doctor(
        email=register_doctor_request.email,
        password=register_doctor_request.password,
        username=register_doctor_request.username,
    )


@user_router.post("/login")
async def login_user(
    login_user_request: LoginUserRequest,
    auth_controller: AuthController = Depends(Factory().get_auth_controller),
) -> Token:
    return await auth_controller.login(
        email=login_user_request.email, password=login_user_request.password
    )


@user_router.get("/me", dependencies=[Depends(AuthenticationRequired)])
def get_user(
    user: User = Depends(get_current_user),
) -> UserResponse:
    return user
