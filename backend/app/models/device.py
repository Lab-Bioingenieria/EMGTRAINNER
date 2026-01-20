from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database.session import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True)  # Device ID (MAC or unique string)
    name = Column(String, nullable=True)
    api_key = Column(String, nullable=False) # Simple auth key
    last_seen = Column(DateTime, nullable=True)
    last_ip = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True)
    rssi = Column(Integer, nullable=True)
    battery_level = Column(Float, nullable=True)
    is_online = Column(Boolean, default=False) # Computed or cached status

    sensors = relationship("SensorStatus", back_populates="device", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="device")


class SensorStatus(Base):
    __tablename__ = "sensor_statuses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    sensor_name = Column(String, nullable=False) # e.g., 'myo_left', 'ppg'
    state = Column(String, default="disconnected") # connected, disconnected, error
    last_seen = Column(DateTime, default=datetime.utcnow)
    details = Column(String, nullable=True) # JSON or text details

    device = relationship("Device", back_populates="sensors")
