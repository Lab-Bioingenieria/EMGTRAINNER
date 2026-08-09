from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from jose import jwt

from api.v1.microcontrollers.health_micro import health_microcontroller_router
from api.v1.monitoring.sensor import sensor_router
from app.routers.hand import get_hand_service, router as hand_router
from app.routers.safety import router as safety_router
from core.config import config
from core.exceptions import CustomException
from core.fastapi.middlewares.authentication import AuthBackend, AuthenticationMiddleware
from core.safety.estop import estop_service
from core.security.jwt import JWTHandler


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse(status_code=401, content={"message": str(exc)})


class FakeHandService:
    """Mocked lower-level hand service; never touches serial hardware."""

    def __init__(self):
        self.executed_gestures = []
        self.is_initialized = True

    def execute_gesture(self, gesture_name: str):
        self.executed_gestures.append(gesture_name)
        return {"status": "executed", "gesture_name": gesture_name}


@pytest.fixture(autouse=True)
def jwt_handler_config():
    """Other test modules mutate JWTHandler class state; pin it to the config."""
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


@pytest.fixture(autouse=True)
def reset_estop():
    estop_service.engage(reason="test setup", actor="test")
    yield
    estop_service.engage(reason="test teardown", actor="test")


@pytest.fixture
def fake_hand_service() -> FakeHandService:
    return FakeHandService()


@pytest.fixture
def hardware_app(fake_hand_service) -> FastAPI:
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

    app.include_router(hand_router)
    app.include_router(safety_router)
    app.include_router(sensor_router, prefix="/monitoring")
    app.include_router(health_microcontroller_router, prefix="/microcontrollers")
    app.dependency_overrides[get_hand_service] = lambda: fake_hand_service
    return app


def _auth_headers() -> dict:
    token = jwt.encode(
        {"user_id": 1, "exp": datetime.utcnow() + timedelta(minutes=5)},
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )
    return {"Authorization": f"Bearer {token}"}


UNAUTHENTICATED_CASES = [
    ("get", "/monitoring/emg/status"),
    ("post", "/monitoring/emg/connect"),
    ("post", "/monitoring/emg/disconnect"),
    ("post", "/monitoring/emg/start"),
    ("post", "/monitoring/emg/stop"),
    ("get", "/microcontrollers/ports"),
    ("get", "/microcontrollers/config"),
    ("get", "/hand/status"),
    ("post", "/hand/gesture"),
    ("get", "/hand/safety/status"),
    ("post", "/hand/safety/estop"),
    ("post", "/hand/safety/reset"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path", UNAUTHENTICATED_CASES)
async def test_hardware_endpoints_reject_unauthenticated_access(
    hardware_app, method, path
):
    transport = ASGITransport(app=hardware_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await getattr(client, method)(path)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_estop_engaged_blocks_gesture_execution(hardware_app, fake_hand_service):
    transport = ASGITransport(app=hardware_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/hand/gesture",
            json={"gesture_name": "open"},
            headers=_auth_headers(),
        )

    assert response.status_code == 409
    assert fake_hand_service.executed_gestures == []


@pytest.mark.asyncio
async def test_estop_reset_allows_gesture_to_reach_hand_service(
    hardware_app, fake_hand_service
):
    transport = ASGITransport(app=hardware_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reset = await client.post("/hand/safety/reset", headers=_auth_headers())
        assert reset.status_code == 200
        assert reset.json()["engaged"] is False

        response = await client.post(
            "/hand/gesture",
            json={"gesture_name": "open"},
            headers=_auth_headers(),
        )

    assert response.status_code == 200
    assert fake_hand_service.executed_gestures == ["open"]


@pytest.mark.asyncio
async def test_estop_endpoint_re_engages_and_blocks_again(
    hardware_app, fake_hand_service
):
    transport = ASGITransport(app=hardware_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/hand/safety/reset", headers=_auth_headers())
        engaged = await client.post(
            "/hand/safety/estop",
            json={"reason": "manual stop"},
            headers=_auth_headers(),
        )
        assert engaged.status_code == 200
        assert engaged.json()["engaged"] is True

        response = await client.post(
            "/hand/gesture",
            json={"gesture_name": "open"},
            headers=_auth_headers(),
        )

    assert response.status_code == 409
    assert fake_hand_service.executed_gestures == []


@pytest.mark.asyncio
async def test_safety_status_defaults_to_engaged(hardware_app):
    transport = ASGITransport(app=hardware_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/hand/safety/status", headers=_auth_headers())

    assert response.status_code == 200
    assert response.json()["engaged"] is True


@pytest.mark.asyncio
async def test_unauthenticated_request_cannot_change_safety_state(hardware_app):
    transport = ASGITransport(app=hardware_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/hand/safety/reset")

    assert response.status_code == 401
    assert estop_service.is_engaged is True
