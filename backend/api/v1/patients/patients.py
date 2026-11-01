from fastapi import APIRouter, Depends
from typing import List

from app.controllers.patient import PatientController
from app.schemas.requests.patients import CreatePatientRequest
from app.schemas.responses.patients import PatientResponse
from core.factory.factory import Factory
from core.fastapi.dependencies.role import RequireDoctor

# The patient roster is doctor/admin territory: it's how a clinician looks
# up or manually adds a patient, which is a different thing from a patient
# managing their own account. RequireDoctor keeps a patient account (whose
# own record lives in this same table) from listing everyone else's.
patients_router = APIRouter()

@patients_router.get("/", dependencies=[Depends(RequireDoctor)])
async def get_patients(
    patient_controller: PatientController = Depends(Factory().get_patient_controller),
) -> List[PatientResponse]:
    patients = await patient_controller.get_all_patients()
    return patients

@patients_router.post("/", status_code=201, dependencies=[Depends(RequireDoctor)])
async def create_patient(
    request: CreatePatientRequest,
    patient_controller: PatientController = Depends(Factory().get_patient_controller),
) -> PatientResponse:
    return await patient_controller.create_patient(**request.model_dump())
