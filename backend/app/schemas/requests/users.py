# pylint: disable=all

import re

from pydantic import BaseModel, EmailStr, conint, constr, field_validator


class RegisterUserRequest(BaseModel):
    """
    Public self-registration. This always creates a PATIENT account — there
    is no `role` field here on purpose, so a caller cannot request a doctor
    account through this endpoint. Doctor accounts are provisioned
    separately (see `POST /users/doctors` and `seed_doctors.py`).

    `age` is required because it feeds the `Patient` roster record created
    alongside the user: the patient database is generated from this
    registration, not entered by hand afterwards.
    """

    email: EmailStr
    password: constr(min_length=8, max_length=64)
    username: constr(min_length=3, max_length=64)
    age: conint(ge=1, le=120)

    @field_validator("password")
    @classmethod
    def password_must_contain_numbers(cls, v):
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain numbers")
        return v

    @field_validator("password")
    @classmethod
    def password_must_contain_uppercase(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase characters")
        return v

    @field_validator("password")
    @classmethod
    def password_must_contain_lowercase(cls, v):
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase characters")
        return v

    @field_validator("username")
    @classmethod
    def username_must_not_contain_special_characters(cls, v):
        if re.search(r"[^a-zA-Z0-9 áéíóúÁÉÍÓÚñÑ_.-]", v):
            raise ValueError("Username contains invalid characters")
        return v


class RegisterDoctorRequest(BaseModel):
    """
    Administrative doctor provisioning (not exposed as public sign-up).
    Used by `POST /users/doctors` (admin-only) and by `seed_doctors.py`,
    which reads this same shape from an externally-maintained data file.
    """

    email: EmailStr
    password: constr(min_length=8, max_length=64)
    username: constr(min_length=3, max_length=64)

    @field_validator("password")
    @classmethod
    def password_must_contain_numbers(cls, v):
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain numbers")
        return v

    @field_validator("password")
    @classmethod
    def password_must_contain_uppercase(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase characters")
        return v

    @field_validator("password")
    @classmethod
    def password_must_contain_lowercase(cls, v):
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase characters")
        return v

    @field_validator("username")
    @classmethod
    def username_must_not_contain_special_characters(cls, v):
        if re.search(r"[^a-zA-Z0-9 áéíóúÁÉÍÓÚñÑ_.-]", v):
            raise ValueError("Username contains invalid characters")
        return v


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str
