from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Column, Unicode
from sqlalchemy.types import Uuid as UUID
from sqlalchemy.orm import relationship

from core.database import Base
from core.database.mixins import TimestampMixin
from core.database.types import BigIntPk
from core.security.access_control import Allow, Everyone, RolePrincipal, UserPrincipal


class UserPermission(Enum):
    CREATE = "create"
    READ = "read"
    EDIT = "edit"
    DELETE = "delete"


class UserRole(str, Enum):
    """
    Separates the two interfaces of the system.

    DOCTOR accounts are never created through public self-registration: they
    are provisioned out-of-band (admin endpoint or the `seed_doctors.py`
    import script) from data entered externally by the team, per the
    "external database" requirement for doctors.

    PATIENT accounts are the ones created by the public registration
    endpoint; each one generates its own `Patient` record, so the patient
    roster is built directly from user sign-up.
    """

    DOCTOR = "doctor"
    PATIENT = "patient"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    email = Column(Unicode(255), nullable=False, unique=True)
    password = Column(Unicode(255), nullable=False)
    username = Column(Unicode(255), nullable=False, unique=True)
    is_admin = Column(Boolean, default=False)
    role = Column(
        Unicode(20), nullable=False, default=UserRole.PATIENT.value,
        server_default=UserRole.PATIENT.value,
    )

    tasks = relationship(
        "Task", back_populates="author", lazy="raise", passive_deletes=True
    )
    patient_profile = relationship(
        "Patient", back_populates="user", uselist=False, lazy="raise"
    )

    __mapper_args__ = {"eager_defaults": True}

    def __acl__(self):
        basic_permissions = [UserPermission.READ, UserPermission.CREATE]
        self_permissions = [
            UserPermission.READ,
            UserPermission.EDIT,
            UserPermission.CREATE,
        ]
        all_permissions = list(UserPermission)

        return [
            (Allow, Everyone, basic_permissions),
            (Allow, UserPrincipal(value=self.id), self_permissions),
            (Allow, RolePrincipal(value="admin"), all_permissions),
        ]
