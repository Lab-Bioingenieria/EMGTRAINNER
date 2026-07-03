import asyncio
from core.database import get_session
from app.models.patient import Patient

async def seed():
    async for session in get_session():
        patients = [
            Patient(patient_code="P-2341", name="María González", age=45, sessions_count=12, last_session="2026-05-10", progress=89, status="active"),
            Patient(patient_code="P-1892", name="Carlos Rodríguez", age=38, sessions_count=8, last_session="2026-05-10", progress=76, status="active"),
            Patient(patient_code="P-3021", name="Ana Martínez", age=52, sessions_count=15, last_session="2026-05-09", progress=94, status="active"),
            Patient(patient_code="P-4156", name="Luis Fernández", age=41, sessions_count=5, last_session="2026-05-08", progress=62, status="inactive"),
            Patient(patient_code="P-5234", name="Elena Sánchez", age=35, sessions_count=20, last_session="2026-05-07", progress=97, status="completed"),
            Patient(patient_code="P-6789", name="Roberto López", age=48, sessions_count=3, last_session="2026-05-05", progress=45, status="active"),
        ]
        session.add_all(patients)
        try:
            await session.commit()
            print("Patients seeded!")
        except Exception as e:
            print(f"Error seeding or already exist: {e}")
        break

if __name__ == "__main__":
    asyncio.run(seed())
