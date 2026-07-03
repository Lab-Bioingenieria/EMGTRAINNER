from pydantic import BaseModel, Field

class CreatePatientRequest(BaseModel):
    patient_code: str = Field(..., description="Unique patient code e.g. P-1234")
    name: str = Field(..., description="Full name of the patient")
    age: int = Field(..., description="Age of the patient")
    status: str = Field("active", description="Status of the patient: active, inactive, completed")
