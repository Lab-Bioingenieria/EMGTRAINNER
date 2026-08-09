import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

from app.routers.orders import router as orders_router
from core.exceptions import CustomException
from core.fastapi.middlewares.authentication import AuthBackend, AuthenticationMiddleware


def on_auth_error(request: Request, exc: Exception):
    return JSONResponse(status_code=401, content={"message": str(exc)})


@pytest.fixture
def orders_app() -> FastAPI:
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

    app.include_router(orders_router)
    return app


@pytest.mark.asyncio
async def test_order_csv_download_requires_authentication(orders_app):
    transport = ASGITransport(app=orders_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/orders/order-1/csv")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_order_csv_upload_requires_authentication(orders_app):
    transport = ASGITransport(app=orders_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/orders/order-1/upload",
            files={"file": ("session.csv", b"a,b\n1,2\n", "text/csv")},
        )

    assert response.status_code == 401
