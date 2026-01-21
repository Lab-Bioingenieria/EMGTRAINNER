from fastapi import APIRouter

from .health import health_router
from .sensor import sensor_router

monitoring_router = APIRouter()
monitoring_router.include_router(health_router, prefix="/health", tags=["Health"])
monitoring_router.include_router(sensor_router, prefix="/sensor", tags=["Sensor"])

__all__ = ["monitoring_router"]
