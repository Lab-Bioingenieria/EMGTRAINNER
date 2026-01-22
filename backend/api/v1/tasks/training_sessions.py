from fastapi import APIRouter, Depends
from app.schemas.requests.training_session import TrainingSessionCreate
from app.schemas.responses.training_session import TrainingSessionResponse
from core.factory import Factory
from core.fastapi.dependencies.permissions import Permissions
from app.models.task import TaskPermission

training_router = APIRouter(prefix="/training-sessions")

@training_router.post(
    "/",
    response_model=TrainingSessionResponse,
    status_code=201,
)
async def create_training_session(
    payload: TrainingSessionCreate,
    use_case = Depends(Factory().get_training_session_use_case),
    assert_access = Depends(Permissions(TaskPermission.CREATE)),
):
    session = await use_case.create(payload)
    return session
