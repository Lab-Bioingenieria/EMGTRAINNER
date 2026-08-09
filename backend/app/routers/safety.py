"""Emergency-stop control endpoints.

All endpoints require authentication: unauthenticated callers can neither read
nor change the safety state.
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from core.fastapi.dependencies.authentication import AuthenticationRequired
from core.safety.estop import estop_service

router = APIRouter(
    prefix="/hand/safety",
    tags=["Hand Safety"],
    dependencies=[Depends(AuthenticationRequired)],
)


class EmergencyStopRequest(BaseModel):
    reason: Optional[str] = None


def _actor(request: Request) -> Optional[str]:
    return getattr(getattr(request, "user", None), "id", None)


@router.get("/status")
async def get_safety_status() -> Dict[str, Any]:
    """Report the current emergency-stop state."""
    return estop_service.state()


@router.post("/estop")
async def engage_emergency_stop(
    request: Request,
    payload: EmergencyStopRequest = EmergencyStopRequest(),
) -> Dict[str, Any]:
    """Engage the emergency stop and block all movement commands."""
    return estop_service.engage(
        reason=payload.reason or "manual engage",
        actor=_actor(request),
    )


@router.post("/reset")
async def reset_emergency_stop(request: Request) -> Dict[str, Any]:
    """Reset the emergency stop so movement commands are allowed again."""
    return estop_service.reset(actor=_actor(request))
