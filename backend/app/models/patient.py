from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from core.database import Base
from core.database.mixins import TimestampMixin

class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_code = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    sessions_count = Column(Integer, default=0)
    last_session = Column(String(50), nullable=True)
    progress = Column(Integer, default=0)
    status = Column(String(50), default="active")
    # Set when this roster entry comes from a patient's own account
    # (self-registration). NULL for legacy/manually entered records that
    # have no login of their own.
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True
    )

    user = relationship("User", back_populates="patient_profile", lazy="raise")

    __mapper_args__ = {"eager_defaults": True}
