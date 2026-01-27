from sqlalchemy import Column, Integer, String, DateTime, JSON
from core.database import Base
from datetime import datetime

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, nullable=True)  # Stores the sensor readings
    status = Column(String, default="completed") # 'recording', 'completed', 'failed'
