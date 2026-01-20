from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import DataFile
# from app.schemas.datafile import DataFileCreate # We might not need a schema for creation if it's internal

class DataFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, file_id: str, order_id: str, device_id: str, storage_path: str, file_size: int, checksum: str) -> DataFile:
        data_file = DataFile(
            id=file_id,
            order_id=order_id,
            device_id=device_id,
            storage_path=storage_path,
            file_size_bytes=file_size,
            checksum=checksum
        )
        self.session.add(data_file)
        await self.session.commit()
        await self.session.refresh(data_file)
        return data_file
