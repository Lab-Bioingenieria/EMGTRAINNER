from pydantic import BaseModel, Field
from starlette.authentication import BaseUser


class CurrentUser(BaseModel, BaseUser):
    id: int | None = Field(None, description="User ID")

    @property
    def is_authenticated(self) -> bool:
        return self.id is not None

    @property
    def display_name(self) -> str:
        return str(self.id or "")

    class Config:
        validate_assignment = True
