from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database.session import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True) # UUID
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    created_by = Column(String, nullable=False) # User ID or name
    status = Column(String, default="created") # created, running, finished, failed, canceled
    
    # Request Parameters
    requested_duration = Column(Integer, nullable=True) # in seconds
    sample_rate = Column(Integer, nullable=True) # e.g., 200Hz
    signal_types = Column(JSON, nullable=True) # ["emg", "ppg"]
    notes = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    
    error_reason = Column(String, nullable=True)

    device = relationship("Device", back_populates="orders")
    data_files = relationship("DataFile", back_populates="order", cascade="all, delete-orphan")


class DataFile(Base):
    __tablename__ = "data_files"

    id = Column(String, primary_key=True, index=True) # UUID
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    device_id = Column(String, nullable=False) # Redundant but useful for fast query
    
    storage_path = Column(String, nullable=False) # Local path or S3 key
    download_url = Column(String, nullable=True) # Generated URL
    
    file_size_bytes = Column(Integer, default=0)
    checksum = Column(String, nullable=True) # MD5/SHA256
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="data_files")
