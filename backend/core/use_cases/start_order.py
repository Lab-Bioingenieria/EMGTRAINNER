from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderUpdate

class StartOrder:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, order_id: str):
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if order.status != "created":
             # If it's already running, idempotent ok? Or error?
             if order.status == "running":
                 return order
             raise ValueError(f"Order cannot be started from status {order.status}")

        order_update = OrderUpdate(
            status="running",
            started_at=datetime.utcnow()
        )
        
        updated_order = await self.order_repository.update(order, order_update)
        return updated_order
