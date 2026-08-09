import pytest
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from core.config import Config
from core.server import make_middleware


def test_production_config_rejects_default_jwt_secret():
    with pytest.raises(ValidationError):
        Config(ENVIRONMENT="production", SECRET_KEY="super-secret-key")


def test_development_config_allows_default_jwt_secret_for_local_ergonomics():
    settings = Config(ENVIRONMENT="development", SECRET_KEY="super-secret-key")

    assert settings.SECRET_KEY == "super-secret-key"


def test_cors_middleware_does_not_allow_wildcard_origin_with_credentials():
    cors_middleware = next(
        middleware
        for middleware in make_middleware()
        if middleware.cls is CORSMiddleware
    )

    assert cors_middleware.kwargs["allow_credentials"] is True
    assert cors_middleware.kwargs["allow_origins"] != ["*"]
