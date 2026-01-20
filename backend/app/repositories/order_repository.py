from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order_in: OrderCreate, created_by: str, order_id: str) -> Order:
        order_data = order_in.dict()
        order = Order(**order_data, created_by=created_by, id=order_id)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        query = select(Order).where(Order.id == order_id).options(selectinload(Order.data_files))
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_pending_by_device(self, device_id: str) -> Optional[Order]:
        # Get the oldest created order that hasn't started yet
        query = select(Order).where(
            Order.device_id == device_id,
            Order.status == "created"
        ).order_by(Order.created_at.asc())
        result = await self.session.execute(query)
        return result.scalars().first()

    async def update(self, order: Order, order_in: OrderUpdate) -> Order:
        update_data = order_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        await self.session.commit()
        await self.session.refresh(order)
        return order
