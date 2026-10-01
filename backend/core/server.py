from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import router
from core.cache import Cache, CustomKeyMaker, RedisBackend
from core.config import config
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthBackend,
    AuthenticationMiddleware,
    ResponseLoggerMiddleware,
    SQLAlchemyMiddleware,
)

from app.routers import learning, websocket, hand, hand_mirror, safety, live_session

def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)
    app_.include_router(learning.router)
    app_.include_router(websocket.router)
    app_.include_router(hand.router)
    app_.include_router(hand_mirror.router)
    app_.include_router(safety.router)
    app_.include_router(live_session.router)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def _add_column_if_missing(sync_conn, table: str, column: str, ddl: str) -> None:
    """
    Best-effort, idempotent "migration" for a codebase with no Alembic
    migrations (schema is created via `create_all`, see CE-01 review).
    `create_all` never alters existing tables, so a column added to a model
    after a database already exists needs this instead. Works for both the
    sqlite dev database and Postgres.
    """
    from sqlalchemy import inspect

    inspector = inspect(sync_conn)
    if table not in inspector.get_table_names():
        return  # create_all will create it fresh with the column included
    existing = {col["name"] for col in inspector.get_columns(table)}
    if column in existing:
        return
    sync_conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {ddl}")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    from core.database import Base
    from core.database.session import engines
    import app.models  # Ensures all models are loaded

    async with engines["writer"].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Backfill legacy rows created before the doctor/patient role split.
        # They previously had full access to every screen, so they keep
        # doctor-level access instead of silently losing it as "patient".
        await conn.run_sync(
            lambda sync_conn: _add_column_if_missing(
                sync_conn, "users", "role",
                "role VARCHAR(20) NOT NULL DEFAULT 'doctor'",
            )
        )
        await conn.run_sync(
            lambda sync_conn: _add_column_if_missing(
                sync_conn, "patients", "user_id", "user_id INTEGER"
            )
        )

    yield


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=config.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        Middleware(SQLAlchemyMiddleware),
        Middleware(ResponseLoggerMiddleware),
    ]
    return middleware


def init_cache() -> None:
    pass
    # Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
    app_ = FastAPI(
        title="FastAPI Boilerplate",
        description="FastAPI Boilerplate by @iam-abbas",
        version="1.0.0",
        docs_url=None if config.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if config.ENVIRONMENT == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
        lifespan=lifespan,
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    # init_cache()
    return app_


app = create_app()
