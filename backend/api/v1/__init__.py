from fastapi import APIRouter

from .monitoring import monitoring_router
from .tasks import tasks_router
from .users import users_router
from .microcontrollers import microcontroller_router
from .storage.router import storage_router
from app.routers.devices import router as devices_router
from app.routers.orders import router as orders_router
from .training_sessions import router as training_sessions_router
v1_router = APIRouter()
v1_router.include_router(monitoring_router, prefix="/monitoring")
v1_router.include_router(tasks_router, prefix="/tasks")
v1_router.include_router(users_router, prefix="/users")
v1_router.include_router(microcontroller_router, prefix="/microcontrollers")
v1_router.include_router(storage_router, prefix="/storage")
v1_router.include_router(devices_router)
v1_router.include_router(orders_router)
v1_router.include_router(training_sessions_router, prefix="/training-sessions", tags=["Training Sessions"],)
