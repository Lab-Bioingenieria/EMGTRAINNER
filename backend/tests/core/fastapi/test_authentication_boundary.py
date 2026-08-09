from datetime import datetime, timedelta

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from jose import jwt

from core.config import config
from core.exceptions import CustomException
from core.fastapi.dependencies.authentication import AuthenticationRequired
from core.fastapi.middlewares.authentication import AuthBackend, AuthenticationMiddleware
from core.security.jwt import JWTHandler


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=401,
        content={"error_code": None, "message": str(exc)},
    )


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
def protected_app() -> FastAPI:
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

    @app.get("/protected", dependencies=[Depends(AuthenticationRequired)])
    async def protected(request: Request):
        return {"user_id": request.user.id}

    return app


def _token(payload: dict) -> str:
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.JWT_ALGORITHM)


@pytest.mark.asyncio
async def test_protected_dependency_rejects_malformed_bearer_token(
    protected_app,
    jwt_handler_config,
):
    transport = ASGITransport(app=protected_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/protected",
            headers={"Authorization": "Bearer not-a-jwt"},
        )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"


@pytest.mark.asyncio
async def test_protected_dependency_rejects_expired_bearer_token(
    protected_app,
    jwt_handler_config,
):
    expired_token = _token(
        {"user_id": 123, "exp": datetime.utcnow() - timedelta(minutes=1)}
    )

    transport = ASGITransport(app=protected_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/protected",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"


@pytest.mark.asyncio
async def test_protected_dependency_rejects_token_without_user_principal(
    protected_app,
    jwt_handler_config,
):
    token_without_principal = _token(
        {"sub": "legacy-subject-only", "exp": datetime.utcnow() + timedelta(minutes=1)}
    )

    transport = ASGITransport(app=protected_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token_without_principal}"},
        )

    assert response.status_code == 401
    assert response.json()["message"] == "Authentication required"


@pytest.mark.asyncio
async def test_protected_dependency_accepts_valid_bearer_token_with_user_principal(
    protected_app,
    jwt_handler_config,
):
    valid_token = _token(
        {"user_id": 123, "exp": datetime.utcnow() + timedelta(minutes=1)}
    )

    transport = ASGITransport(app=protected_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/protected",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

    assert response.status_code == 200
    assert response.json() == {"user_id": 123}
