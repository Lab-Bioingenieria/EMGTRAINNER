from urllib.parse import quote

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from jose import jwt

from api.v1.storage.router import storage_router
from app.services.csv_service import CSVService, csv_service
from core.config import config
from core.exceptions import CustomException
from core.fastapi.middlewares.authentication import AuthBackend, AuthenticationMiddleware
from core.security.jwt import JWTHandler


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse(status_code=401, content={"message": str(exc)})


@pytest.fixture
def jwt_handler_config():
    original = (
        JWTHandler.secret_key,
        JWTHandler.algorithm,
        JWTHandler.expire_minutes,
    )
    JWTHandler.secret_key = config.SECRET_KEY
    JWTHandler.algorithm = config.JWT_ALGORITHM
    JWTHandler.expire_minutes = config.JWT_EXPIRE_MINUTES
    yield
    (
        JWTHandler.secret_key,
        JWTHandler.algorithm,
        JWTHandler.expire_minutes,
    ) = original


@pytest.fixture
def storage_root(tmp_path, monkeypatch):
    root = tmp_path / "sessions"
    root.mkdir()
    (root / "Guest").mkdir()
    (root / "Guest" / "session_1.csv").write_text("nombre,edad,emg1\nAda,30,0.5\n")
    (tmp_path / "secret.csv").write_text("outside,the,root\n")
    monkeypatch.setattr(csv_service, "storage_dir", str(root))
    return root


@pytest.fixture
def storage_app(storage_root) -> FastAPI:
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

    app.include_router(storage_router, prefix="/storage")
    return app


def _auth_headers() -> dict:
    from datetime import datetime, timedelta

    token = jwt.encode(
        {"user_id": 1, "exp": datetime.utcnow() + timedelta(minutes=5)},
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/storage/sessions", "/storage/sessions/Guest/session_1.csv"])
async def test_storage_endpoints_reject_unauthenticated_access(storage_app, path):
    transport = ASGITransport(app=storage_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_download_of_in_root_file_succeeds(
    storage_app, jwt_handler_config
):
    transport = ASGITransport(app=storage_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/storage/sessions/Guest/session_1.csv", headers=_auth_headers()
        )

    assert response.status_code == 200
    assert response.text == "nombre,edad,emg1\nAda,30,0.5\n"


@pytest.mark.asyncio
async def test_authenticated_traversal_download_is_rejected(
    storage_app, jwt_handler_config
):
    traversal = quote("../secret.csv", safe="")
    transport = ASGITransport(app=storage_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            f"/storage/sessions/{traversal}", headers=_auth_headers()
        )

    assert response.status_code == 404
    assert "outside" not in response.text


def test_get_session_path_rejects_relative_traversal(storage_root):
    service = CSVService(storage_dir=str(storage_root))

    assert service.get_session_path("../secret.csv") is None
    assert service.get_session_path("Guest/../../secret.csv") is None


def test_get_session_path_rejects_absolute_path(storage_root, tmp_path):
    service = CSVService(storage_dir=str(storage_root))

    assert service.get_session_path(str(tmp_path / "secret.csv")) is None


def test_get_session_path_rejects_symlink_escape(storage_root, tmp_path):
    (storage_root / "escape.csv").symlink_to(tmp_path / "secret.csv")
    service = CSVService(storage_dir=str(storage_root))

    assert service.get_session_path("escape.csv") is None


def test_get_session_path_allows_in_root_file(storage_root):
    service = CSVService(storage_dir=str(storage_root))

    assert service.get_session_path("Guest/session_1.csv") == str(
        storage_root / "Guest" / "session_1.csv"
    )
