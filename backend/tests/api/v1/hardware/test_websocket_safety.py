from datetime import datetime, timedelta

import pytest
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
from jose import jwt
from starlette.websockets import WebSocketDisconnect

from core.config import config
from core.fastapi.dependencies.websocket_auth import authenticate_websocket
from core.security.jwt import JWTHandler


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
def ws_app() -> FastAPI:
    app = FastAPI()

    @app.websocket("/ws/guarded")
    async def guarded(websocket: WebSocket):
        user = await authenticate_websocket(websocket)
        if user is None:
            return
        await websocket.send_json({"user_id": user.id})
        await websocket.close()

    return app


def _token() -> str:
    return jwt.encode(
        {"user_id": 7, "exp": datetime.utcnow() + timedelta(minutes=5)},
        config.SECRET_KEY,
        algorithm=config.JWT_ALGORITHM,
    )


def test_websocket_without_token_is_rejected(ws_app):
    client = TestClient(ws_app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/guarded") as ws:
            ws.receive_json()


def test_websocket_with_invalid_token_is_rejected(ws_app, jwt_handler_config):
    client = TestClient(ws_app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/guarded?token=not-a-jwt") as ws:
            ws.receive_json()


def test_websocket_with_valid_token_is_accepted(ws_app, jwt_handler_config):
    client = TestClient(ws_app)
    with client.websocket_connect(f"/ws/guarded?token={_token()}") as ws:
        assert ws.receive_json() == {"user_id": 7}


@pytest.fixture
def hardware_ws_app() -> FastAPI:
    from api.v1.monitoring.sensor import sensor_ws_router
    from app.routers.websocket import router as emg_ws_router

    app = FastAPI()
    app.include_router(sensor_ws_router)
    app.include_router(emg_ws_router)
    return app


@pytest.mark.parametrize("path", ["/ws/emg-stream", "/ws/emg"])
def test_hardware_websockets_reject_unauthenticated_clients(hardware_ws_app, path):
    client = TestClient(hardware_ws_app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(path) as ws:
            ws.receive_json()
