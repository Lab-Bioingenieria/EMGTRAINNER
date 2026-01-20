import os
import uuid
import hashlib
from datetime import datetime
from fastapi import UploadFile
from app.repositories.order_repository import OrderRepository
from app.repositories.datafile_repository import DataFileRepository

class UploadCSV:
    def __init__(self, order_repository: OrderRepository, datafile_repository: DataFileRepository, storage_base_path: str = "storage/data"):
        self.order_repository = order_repository
        self.datafile_repository = datafile_repository
        self.storage_base_path = storage_base_path
        
        # Ensure storage directory exists
        os.makedirs(self.storage_base_path, exist_ok=True)

    async def execute(self, order_id: str, file: UploadFile):
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Save file
        file_id = str(uuid.uuid4())
        filename = f"{order_id}_{file_id}.csv"
        file_path = os.path.join(self.storage_base_path, filename)
        
        # Write chunks and calculate checksum
        hash_md5 = hashlib.md5()
        size_bytes = 0
        
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024): # 1MB chunks
                buffer.write(chunk)
                hash_md5.update(chunk)
                size_bytes += len(chunk)
                
        checksum = hash_md5.hexdigest()
        
        # Save metadata
        data_file = await self.datafile_repository.create(
            file_id=file_id,
            order_id=order_id,
            device_id=order.device_id,
            storage_path=file_path,
            file_size=size_bytes,
            checksum=checksum
        )
        
        return data_file
