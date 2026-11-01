import pytest
from httpx import AsyncClient

from tests.factory.users import create_fake_user
from tests.utils.login import _create_doctor_and_login, _create_user_and_login


def _fake_patient(code: str = "P-0001") -> dict:
    return {"patient_code": code, "name": "Jane Doe", "age": 34}


@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient, db_session) -> None:
    """A created patient is actually persisted, not just echoed back."""
    await _create_doctor_and_login(client, db_session)

    response = await client.post("/v1/patients/", json=_fake_patient())
    assert response.status_code == 201

    body = response.json()
    assert body["id"] is not None
    assert body["patient_code"] == "P-0001"
    assert body["sessions_count"] == 0
    assert body["progress"] == 0
    assert body["status"] == "active"
    assert body["created_at"] is not None
    assert body["updated_at"] is not None

    listed = await client.get("/v1/patients/")
    assert listed.status_code == 200
    # Not asserting the roster is exactly ["P-0001"]: the doctor account used
    # to call this endpoint is itself provisioned through patient
    # self-registration (see _create_doctor_and_login), which now also
    # creates its own linked Patient row.
    assert "P-0001" in [p["patient_code"] for p in listed.json()]


@pytest.mark.asyncio
async def test_create_patient_with_duplicate_code(
    client: AsyncClient, db_session
) -> None:
    """A duplicate patient_code is a client error, not a server crash."""
    await _create_doctor_and_login(client, db_session)

    await client.post("/v1/patients/", json=_fake_patient())
    response = await client.post("/v1/patients/", json=_fake_patient())

    assert response.status_code == 400
    assert "already exists" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_all_patients_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/v1/patients/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_patients_requires_doctor_role(
    client: AsyncClient, db_session
) -> None:
    """A patient account (the default for public sign-up) can't list the roster."""
    await _create_user_and_login(client)

    response = await client.get("/v1/patients/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_patient_registration_creates_linked_patient_record(
    client: AsyncClient, db_session
) -> None:
    """The patient roster is generated from user registration, not typed in by hand."""
    fake_user = create_fake_user()
    response = await client.post("/v1/users/", json=fake_user)
    assert response.status_code == 201

    await _create_doctor_and_login(client, db_session)
    listed = await client.get("/v1/patients/")
    assert listed.status_code == 200
    names = [p["name"] for p in listed.json()]
    assert fake_user["username"] in names
