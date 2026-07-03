from functools import partial

from fastapi import Depends

from app.controllers import AuthController, TaskController, UserController, PatientController
from app.models import Task, User, Patient
from app.repositories import TaskRepository, UserRepository, PatientRepository
from core.database import get_session


class Factory:
    """
    This is the factory container that will instantiate all the controllers and
    repositories which can be accessed by the rest of the application.
    """

    # Repositories
    task_repository = partial(TaskRepository, Task)
    user_repository = partial(UserRepository, User)
    patient_repository = partial(PatientRepository, Patient)

    def get_user_controller(self, db_session=Depends(get_session)):
        return UserController(
            user_repository=self.user_repository(db_session=db_session)
        )

    def get_patient_controller(self, db_session=Depends(get_session)):
        return PatientController(
            patient_repository=self.patient_repository(db_session=db_session)
        )

    def get_task_controller(self, db_session=Depends(get_session)):
        return TaskController(
            task_repository=self.task_repository(db_session=db_session)
        )

    def get_auth_controller(self, db_session=Depends(get_session)):
        return AuthController(
            user_repository=self.user_repository(db_session=db_session),
        )
