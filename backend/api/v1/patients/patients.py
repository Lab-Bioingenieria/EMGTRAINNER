from fastapi import APIRouter, Depends
from typing import List

from app.controllers.patient import PatientController
from app.schemas.requests.patients import CreatePatientRequest
from app.schemas.responses.patients import PatientResponse
from core.factory.factory import Factory
from core.fastapi.dependencies import AuthenticationRequired

patients_router = APIRouter()

@patients_router.get("/", dependencies=[Depends(AuthenticationRequired)])
async def get_patients(
    patient_controller: PatientController = Depends(Factory().get_patient_controller),
) -> List[PatientResponse]:
    patients = await patient_controller.get_all_patients()
    return patients

@patients_router.post("/", status_code=201, dependencies=[Depends(AuthenticationRequired)])
async def create_patient(
    request: CreatePatientRequest,
    patient_controller: PatientController = Depends(Factory().get_patient_controller),
) -> PatientResponse:
    return await patient_controller.create_patient(**request.dict())
