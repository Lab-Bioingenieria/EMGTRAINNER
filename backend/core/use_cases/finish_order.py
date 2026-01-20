from datetime import datetime
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderUpdate

class FinishOrder:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def execute(self, order_id: str, error_reason: str = None):
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # We can finish a running order, or maybe a created one if cancelled immediately?
        # Assuming we finish 'running' orders.
        
        status = "finished"
        if error_reason:
            status = "failed"
            
        order_update = OrderUpdate(
            status=status,
            finished_at=datetime.utcnow(),
            error_reason=error_reason
        )
        
        updated_order = await self.order_repository.update(order, order_update)
        return updated_order
