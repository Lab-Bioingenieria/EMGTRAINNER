from fastapi import APIRouter, HTTPException
from app.services.llc_service import llc_service

router = APIRouter(
    prefix="/learning",
    tags=["Learning Curriculum"]
)

@router.get("/next-gesture/{patient_name}")
async def get_next_gesture(patient_name: str):
    """
    Get the next recommended gesture based on Separability Index (LLC).
    Returns the gesture with the lowest separability score (weighted by practice count).
    """
    try:
        result = llc_service.suggest_next_gesture(patient_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
