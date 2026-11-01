from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User, UserRole
from tests.factory.users import create_fake_user


async def _create_user_and_login(
    client: AsyncClient, fake_user=create_fake_user()
) -> None:
    """Registers a patient account (the only kind public sign-up allows) and logs in."""
    await client.post("/v1/users/", json=fake_user)

    response = await client.post("/v1/users/login", json=fake_user)
    access_token = response.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {access_token}"})

    return None


async def _create_doctor_and_login(client: AsyncClient, db_session) -> dict:
    """
    Doctor accounts can't come from `POST /v1/users/` (see
    `RegisterUserRequest` — it has no `role` field on purpose), so tests
    that need one register a normal account and then promote it directly
    in the test database, the same way `seed_doctors.py` / the admin-only
    `POST /v1/users/doctors` endpoint would in a real deployment.
    Role checks (`RequireRole`) re-read the role from the database on every
    request, so the already-issued token keeps working after the promotion.
    """
    fake_user = create_fake_user()
    await client.post("/v1/users/", json=fake_user)

    response = await client.post("/v1/users/login", json=fake_user)
    access_token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {access_token}"})

    result = await db_session.execute(
        select(User).where(User.email == fake_user["email"])
    )
    user = result.scalar_one()
    user.role = UserRole.DOCTOR.value
    await db_session.commit()

    return fake_user


__all__ = ["_create_user_and_login", "_create_doctor_and_login"]
