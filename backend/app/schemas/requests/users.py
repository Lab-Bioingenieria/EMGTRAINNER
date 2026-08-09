# pylint: disable=all

import re

from pydantic import BaseModel, EmailStr, constr, field_validator


class RegisterUserRequest(BaseModel):
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
