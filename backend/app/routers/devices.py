from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.device import HeartbeatRequest, DeviceRead
from app.models.device import Device
from app.repositories.device_repository import DeviceRepository
from core.use_cases.record_heartbeat import RecordHeartbeat
from core.use_cases.get_device_status import GetDeviceStatus
from core.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)

async def get_device_repo(session: AsyncSession = Depends(get_session)) -> DeviceRepository:
    return DeviceRepository(session)

@router.post("/{device_id}/heartbeat")
async def heartbeat(
    device_id: str,
    request: HeartbeatRequest,
    repo: DeviceRepository = Depends(get_device_repo)
):
    if device_id != request.device_id:
        raise HTTPException(status_code=400, detail="Device ID mismatch")
    
    use_case = RecordHeartbeat(repo)
    try:
        result = await use_case.execute(request)
        return result
    except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))

@router.get("/{device_id}/status", response_model=DeviceRead)
async def get_status(
    device_id: str,
    repo: DeviceRepository = Depends(get_device_repo)
):
    use_case = GetDeviceStatus(repo)
    try:
        device = await use_case.execute(device_id)
        return device
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
