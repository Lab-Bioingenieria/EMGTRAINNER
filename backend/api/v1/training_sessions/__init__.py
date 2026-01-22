from fastapi import APIRouter
from .router import router as training_sessions_router

v1_router = APIRouter()
v1_router.include_router(training_sessions_router)

__all__ = ["router"]