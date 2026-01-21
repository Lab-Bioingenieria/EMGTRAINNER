from fastapi import APIRouter

from .health_micro import health_microcontroller_router

microcontroller_router = APIRouter()
microcontroller_router.include_router(health_microcontroller_router,prefix="/health_micro", tags=["Microcontrollers"])

__all__ = ["microcontroller_router"]


