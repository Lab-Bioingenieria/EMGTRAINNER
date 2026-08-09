from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DataFileRead(BaseModel):
    id: str
    order_id: str
    storage_path: str
    download_url: Optional[str] = None
    file_size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
