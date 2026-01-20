from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from app.schemas.order import OrderCreate, OrderRead
from app.repositories.order_repository import OrderRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.datafile_repository import DataFileRepository
from core.use_cases.create_order import CreateOrder
from core.use_cases.start_order import StartOrder
from core.use_cases.finish_order import FinishOrder
from core.use_cases.upload_csv import UploadCSV
from core.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)

async def get_repos(session: AsyncSession = Depends(get_session)):
    return {
        "order": OrderRepository(session),
        "device": DeviceRepository(session),
        "datafile": DataFileRepository(session)
    }

@router.post("", response_model=OrderRead)
async def create_order(
    order_in: OrderCreate,
    repos: dict = Depends(get_repos)
):
    # Mock user ID for MVP
    user_id = "test_user" 
    
    use_case = CreateOrder(repos["order"], repos["device"])
    try:
        order = await use_case.execute(order_in, created_by=user_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: str,
    repos: dict = Depends(get_repos)
):
    order = await repos["order"].get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/pending", response_model=OrderRead)
async def get_pending_order(
    device_id: str,
    repos: dict = Depends(get_repos)
):
    order = await repos["order"].get_pending_by_device(device_id)
    if not order:
         raise HTTPException(status_code=404, detail="No pending orders found")
    return order

@router.post("/{order_id}/start", response_model=OrderRead)
async def start_order(
    order_id: str,
    repos: dict = Depends(get_repos)
):
    use_case = StartOrder(repos["order"])
    try:
        order = await use_case.execute(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/finish", response_model=OrderRead)
async def finish_order(
    order_id: str,
    repos: dict = Depends(get_repos)
):
    use_case = FinishOrder(repos["order"])
    try:
        order = await use_case.execute(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/upload")
async def upload_csv(
    order_id: str,
    file: UploadFile = File(...),
    repos: dict = Depends(get_repos)
):
    # Note: Ensure storage_base_path is configured possibly via env
    use_case = UploadCSV(repos["order"], repos["datafile"])
    try:
        data_file = await use_case.execute(order_id, file)
        return {"status": "uploaded", "file_id": data_file.id, "checksum": data_file.checksum}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{order_id}/csv")
async def download_csv(
    order_id: str,
    repos: dict = Depends(get_repos)
):
    # This logic assumes one file per order for MVP download endpoint
    # Or we list files? User said "Endpoint para descargar el CSV"
    
    order = await repos["order"].get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if not order.data_files:
        raise HTTPException(status_code=404, detail="No CSV file found for this order")
        
    # Get the latest file?
    data_file = order.data_files[0]
    
    return FileResponse(data_file.storage_path, media_type="text/csv", filename=f"order_{order_id}.csv")
