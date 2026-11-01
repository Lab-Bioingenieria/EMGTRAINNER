import random

from pydantic import EmailStr

from app.models import User
from app.models.patient import Patient
from app.models.user import UserRole
from app.repositories import UserRepository
from app.schemas.extras.token import Token
from core.controller import BaseController
from core.database import Propagation, Transactional
from core.exceptions import BadRequestException, UnauthorizedException
from core.security import JWTHandler, PasswordHandler


class AuthController(BaseController[User]):
    def __init__(self, user_repository: UserRepository):
        super().__init__(model=User, repository=user_repository)
        self.user_repository = user_repository

    async def _create_user(
        self, email: EmailStr, password: str, username: str, role: UserRole
    ) -> User:
        # Check if user exists with email
        user = await self.user_repository.get_by_email(email)

        if user:
            raise BadRequestException("User already exists with this email")

        # Check if user exists with username
        user = await self.user_repository.get_by_username(username)

        if user:
            raise BadRequestException("User already exists with this username")

        hashed_password = PasswordHandler.hash(password)

        return await self.user_repository.create(
            {
                "email": email,
                "password": hashed_password,
                "username": username,
                "role": role.value,
            }
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def register(
        self, email: EmailStr, password: str, username: str, age: int
    ) -> User:
        """
        Public patient self-registration. This is the ONLY way a patient
        account is created, and it is also how the patient roster
        (`patients` table) is populated: every sign-up creates its matching
        `Patient` record instead of a doctor entering it by hand.
        """
        user = await self._create_user(
            email=email, password=password, username=username, role=UserRole.PATIENT
        )
        # `create()` only adds to the session; flush now so `user.id` is
        # assigned before it's used to build the patient_code below.
        await self.user_repository.session.flush()

        patient_code = f"P-{user.id:05d}-{random.randint(100, 999)}"
        patient = Patient(
            patient_code=patient_code,
            name=username,
            age=age,
            status="active",
            user_id=user.id,
        )
        self.user_repository.session.add(patient)
        await self.user_repository.session.flush()

        return user

    @Transactional(propagation=Propagation.REQUIRED)
    async def register_doctor(
        self, email: EmailStr, password: str, username: str
    ) -> User:
        """
        Administrative doctor provisioning. Never reachable from the public
        registration endpoint — only from an admin-authenticated request
        (`POST /users/doctors`) or from `seed_doctors.py`, which loads
        doctor data the team maintains externally (see that script).
        """
        return await self._create_user(
            email=email, password=password, username=username, role=UserRole.DOCTOR
        )

    async def login(self, email: EmailStr, password: str) -> Token:
        user = await self.user_repository.get_by_email(email)

        if not user:
            raise BadRequestException("Invalid credentials")

        if not PasswordHandler.verify(user.password, password):
            raise BadRequestException("Invalid credentials")

        return Token(
            access_token=JWTHandler.encode(
                payload={"user_id": user.id, "role": user.role}
            ),
            refresh_token=JWTHandler.encode(payload={"sub": "refresh_token"}),
        )

    async def refresh_token(self, access_token: str, refresh_token: str) -> Token:
        token = JWTHandler.decode(access_token)
        refresh_token = JWTHandler.decode(refresh_token)
        if refresh_token.get("sub") != "refresh_token":
            raise UnauthorizedException("Invalid refresh token")

        return Token(
            access_token=JWTHandler.encode(payload={"user_id": token.get("user_id")}),
            refresh_token=JWTHandler.encode(payload={"sub": "refresh_token"}),
        )
