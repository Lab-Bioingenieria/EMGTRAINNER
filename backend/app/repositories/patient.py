from core.repository.base import BaseRepository
from app.models.patient import Patient
from sqlalchemy import select

class PatientRepository(BaseRepository):
    async def get_by_code(self, patient_code: str) -> Patient | None:
        query = select(self.model_class).where(self.model_class.patient_code == patient_code)
        result = await self.session.execute(query)
        return result.scalars().first()
