from fastapi import APIRouter, Depends
from core.fastapi.dependencies.authentication import AuthenticationRequired
from .training_sessions import training_router
from .tasks import task_router

tasks_router = APIRouter()
tasks_router.include_router(
    task_router,training_router,
    tags=["Tasks","Training Sessions"],
    dependencies=[Depends(AuthenticationRequired)],
)

__all__ = ["tasks_router"]
