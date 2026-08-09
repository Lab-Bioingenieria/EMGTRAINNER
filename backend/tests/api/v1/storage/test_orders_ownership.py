"""Ownership boundary tests for order flows.

Orders carry an owner through `Order.created_by`, so an authenticated user must
only reach their own orders. Storage sessions under `backend/storage/sessions`
have no DB ownership relation yet and are intentionally out of scope here.
"""

from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from app.routers.orders import get_repos
from app.routers.orders import router as orders_router
from core.exceptions import CustomException
from core.fastapi.middlewares.authentication import AuthBackend, AuthenticationMiddleware
from core.security.jwt import JWTHandler

OWNER_ID = 1
INTRUDER_ID = 2


class FakeOrderRepository:
    def __init__(self, order):
        self.order = order
        self.updated = []

    async def get_by_id(self, order_id: str):
        if self.order is None or self.order.id != order_id:
            return None
        return self.order

    async def get_pending_by_device(self, device_id: str):
        if self.order is None or self.order.device_id != device_id:
            return None
        return self.order

    async def update(self, order, order_in):
        self.updated.append(order_in)
        for field, value in order_in.dict(exclude_unset=True).items():
            setattr(order, field, value)
        return order


class FakeDataFileRepository:
    async def create(self, *args, **kwargs):  # pragma: no cover - unused in tests
        raise AssertionError("upload must be blocked before touching storage")


def build_order(tmp_path, created_by: str, status: str = "created"):
    csv_path = tmp_path / f"{created_by}.csv"
    csv_path.write_text("a,b\n1,2\n")
    data_file = SimpleNamespace(
        id="file-1",
        order_id="order-1",
        device_id="device-1",
        storage_path=str(csv_path),
        download_url=None,
        file_size_bytes=csv_path.stat().st_size,
        checksum="deadbeef",
        created_at=datetime.utcnow(),
    )
    return SimpleNamespace(
        id="order-1",
        device_id="device-1",
        created_by=created_by,
        status=status,
        requested_duration=None,
        sample_rate=None,
        signal_types=None,
        notes=None,
        created_at=datetime.utcnow(),
        started_at=None,
        finished_at=None,
        error_reason=None,
        data_files=[data_file],
    )


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse(status_code=401, content={"message": str(exc)})


def make_app(order):
    app = FastAPI()
    app.add_middleware(
        AuthenticationMiddleware,
        backend=AuthBackend(),
        on_error=on_auth_error,
    )

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

    async def _get_repos():
        return {
            "order": FakeOrderRepository(order),
            "device": None,
            "datafile": FakeDataFileRepository(),
        }

    app.dependency_overrides[get_repos] = _get_repos
    app.include_router(orders_router)
    return app


def auth_headers(user_id: int) -> dict:
    return {"Authorization": f"Bearer {JWTHandler.encode({'user_id': user_id})}"}


@pytest.fixture
def owner_app(tmp_path):
    return make_app(build_order(tmp_path, created_by=str(OWNER_ID)))


async def request(app, method: str, url: str, **kwargs):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.request(method, url, **kwargs)


@pytest.mark.asyncio
async def test_owner_can_download_own_order_csv(owner_app):
    response = await request(
        owner_app, "GET", "/orders/order-1/csv", headers=auth_headers(OWNER_ID)
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_intruder_cannot_download_other_users_order_csv(owner_app):
    response = await request(
        owner_app, "GET", "/orders/order-1/csv", headers=auth_headers(INTRUDER_ID)
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_intruder_cannot_upload_to_other_users_order(owner_app):
    response = await request(
        owner_app,
        "POST",
        "/orders/order-1/upload",
        headers=auth_headers(INTRUDER_ID),
        files={"file": ("session.csv", b"a,b\n1,2\n", "text/csv")},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_intruder_cannot_read_other_users_order(owner_app):
    response = await request(
        owner_app, "GET", "/orders/order-1", headers=auth_headers(INTRUDER_ID)
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_intruder_cannot_start_other_users_order(owner_app):
    response = await request(
        owner_app, "POST", "/orders/order-1/start", headers=auth_headers(INTRUDER_ID)
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_intruder_cannot_finish_other_users_order(owner_app):
    response = await request(
        owner_app, "POST", "/orders/order-1/finish", headers=auth_headers(INTRUDER_ID)
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_owner_can_start_own_order(owner_app):
    response = await request(
        owner_app, "POST", "/orders/order-1/start", headers=auth_headers(OWNER_ID)
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_pending_route_is_not_shadowed_by_order_id_route(owner_app):
    response = await request(
        owner_app,
        "GET",
        "/orders/pending?device_id=device-1",
        headers=auth_headers(OWNER_ID),
    )

    assert response.status_code == 200
    assert response.json()["id"] == "order-1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,url",
    [
        ("GET", "/orders/order-1"),
        ("POST", "/orders/order-1/start"),
        ("POST", "/orders/order-1/finish"),
        ("GET", "/orders/order-1/csv"),
    ],
)
async def test_order_endpoints_require_authentication(owner_app, method, url):
    response = await request(owner_app, method, url)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_missing_order_is_not_found_for_authenticated_user(tmp_path):
    app = make_app(None)

    response = await request(
        app, "GET", "/orders/order-1/csv", headers=auth_headers(OWNER_ID)
    )

    assert response.status_code == 404
