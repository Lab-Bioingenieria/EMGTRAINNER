"""Emergency-stop interlock for anything that can move physical hardware.

The interlock is fail-closed: a freshly created service starts ENGAGED, so no
movement command reaches the motor layer until an authenticated operator
explicitly resets it.
"""
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional

from core.exceptions.base import CustomException


class EmergencyStopEngaged(CustomException):
    code = HTTPStatus.CONFLICT
    error_code = HTTPStatus.CONFLICT
    message = "Emergency stop is engaged; movement commands are blocked"


class EmergencyStopService:
    """In-memory E-stop state guarding the movement execution path."""

    def __init__(self) -> None:
        self._engaged: bool = True
        self._reason: Optional[str] = "default safe state"
        self._actor: Optional[str] = None
        self._changed_at: datetime = datetime.utcnow()

    @property
    def is_engaged(self) -> bool:
        return self._engaged

    def engage(self, reason: str = "manual engage", actor: Optional[str] = None) -> Dict[str, Any]:
        self._engaged = True
        self._reason = reason
        self._actor = actor
        self._changed_at = datetime.utcnow()
        return self.state()

    def reset(self, actor: Optional[str] = None) -> Dict[str, Any]:
        self._engaged = False
        self._reason = None
        self._actor = actor
        self._changed_at = datetime.utcnow()
        return self.state()

    def assert_movement_allowed(self) -> None:
        """Raise if any hardware movement is currently forbidden."""
        if self._engaged:
            raise EmergencyStopEngaged(
                f"Emergency stop is engaged ({self._reason or 'unknown reason'}); "
                "reset it before sending movement commands"
            )

    def state(self) -> Dict[str, Any]:
        return {
            "engaged": self._engaged,
            "reason": self._reason,
            "actor": self._actor,
            "changed_at": self._changed_at.isoformat(),
        }


estop_service = EmergencyStopService()
