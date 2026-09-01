import pytest
from httpx import AsyncClient

from tests.utils.login import _create_user_and_login


def _fake_patient(code: str = "P-0001") -> dict:
    return {"patient_code": code, "name": "Jane Doe", "age": 34}


@pytest.mark.asyncio
async def test_create_patient(client: AsyncClient, db_session) -> None:
    """A created patient is actually persisted, not just echoed back."""
    await _create_user_and_login(client)

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
    assert [p["patient_code"] for p in listed.json()] == ["P-0001"]


@pytest.mark.asyncio
async def test_create_patient_with_duplicate_code(
    client: AsyncClient, db_session
) -> None:
    """A duplicate patient_code is a client error, not a server crash."""
    await _create_user_and_login(client)

    await client.post("/v1/patients/", json=_fake_patient())
    response = await client.post("/v1/patients/", json=_fake_patient())

    assert response.status_code == 400
    assert "already exists" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_all_patients_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/v1/patients/")
    assert response.status_code == 401
