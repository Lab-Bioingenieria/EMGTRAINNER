from datetime import datetime
import uuid
from app.repositories.order_repository import OrderRepository
from app.repositories.device_repository import DeviceRepository
from app.schemas.order import OrderCreate

class CreateOrder:
    def __init__(self, order_repository: OrderRepository, device_repository: DeviceRepository):
        self.order_repository = order_repository
        self.device_repository = device_repository

    async def execute(self, order_in: OrderCreate, created_by: str):
        # Validate device exists
        device = await self.device_repository.get_by_id(order_in.device_id)
        if not device:
            raise ValueError("Device not found")
            
        # Optional: Check if device is online
        # Optional: Check if there is already a running order for this device?
        # For simple MVP, let's allow creating, but maybe warn if one is effectively running.
        
        order_id = str(uuid.uuid4())
        
        order = await self.order_repository.create(order_in, created_by, order_id)
        return order
