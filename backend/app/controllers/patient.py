from app.models.patient import Patient
from app.repositories.patient import PatientRepository
from core.controller.base import BaseController
from core.exceptions import BadRequestException

class PatientController(BaseController[Patient]):
    def __init__(self, patient_repository: PatientRepository):
        super().__init__(model=Patient, repository=patient_repository)
        self.patient_repository = patient_repository

    async def get_all_patients(self):
        return await self.patient_repository.get_all()

    async def create_patient(self, **kwargs):
        existing = await self.patient_repository.get_by_code(kwargs.get("patient_code"))
        if existing:
            raise BadRequestException("A patient with this code already exists")
        return await self.patient_repository.create(kwargs)
