from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
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
from core.fastapi.dependencies.authentication import AuthenticationRequired
from core.fastapi.dependencies.ownership import current_user_id, ensure_owner
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(AuthenticationRequired)],
)

async def get_repos(session: AsyncSession = Depends(get_session)):
    return {
        "order": OrderRepository(session),
        "device": DeviceRepository(session),
        "datafile": DataFileRepository(session)
    }

async def get_owned_order(order_id: str, request: Request, repos: dict):
    """Load an order and reject access from users that do not own it."""
    order = await repos["order"].get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    ensure_owner(order, current_user_id(request))
    return order

@router.post("", response_model=OrderRead)
async def create_order(
    order_in: OrderCreate,
    request: Request,
    repos: dict = Depends(get_repos)
):
    use_case = CreateOrder(repos["order"], repos["device"])
    try:
        order = await use_case.execute(order_in, created_by=current_user_id(request))
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pending", response_model=OrderRead)
async def get_pending_order(
    device_id: str,
    repos: dict = Depends(get_repos)
):
    # Device polling endpoint: orders are scoped by device, not by user.
    order = await repos["order"].get_pending_by_device(device_id)
    if not order:
         raise HTTPException(status_code=404, detail="No pending orders found")
    return order

@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: str,
    request: Request,
    repos: dict = Depends(get_repos)
):
    return await get_owned_order(order_id, request, repos)

@router.post("/{order_id}/start", response_model=OrderRead)
async def start_order(
    order_id: str,
    request: Request,
    repos: dict = Depends(get_repos)
):
    await get_owned_order(order_id, request, repos)
    use_case = StartOrder(repos["order"])
    try:
        order = await use_case.execute(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/finish", response_model=OrderRead)
async def finish_order(
    order_id: str,
    request: Request,
    repos: dict = Depends(get_repos)
):
    await get_owned_order(order_id, request, repos)
    use_case = FinishOrder(repos["order"])
    try:
        order = await use_case.execute(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/upload")
async def upload_csv(
    order_id: str,
    request: Request,
    file: UploadFile = File(...),
    repos: dict = Depends(get_repos)
):
    await get_owned_order(order_id, request, repos)
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
    request: Request,
    repos: dict = Depends(get_repos)
):
    # This logic assumes one file per order for MVP download endpoint
    order = await get_owned_order(order_id, request, repos)

    if not order.data_files:
        raise HTTPException(status_code=404, detail="No CSV file found for this order")

    # Get the latest file?
    data_file = order.data_files[0]

    return FileResponse(data_file.storage_path, media_type="text/csv", filename=f"order_{order_id}.csv")
