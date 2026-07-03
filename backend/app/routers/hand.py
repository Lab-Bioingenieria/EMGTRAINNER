from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from app.schemas.hand import (
    GestureExecute,
    GestureResponse,
    HandStatusResponse,
    TrainingSessionConfig,
    SessionResponse,
)
from app.services.hand_service import HandService
from core.use_cases.initialize_hand import InitializeHand
from core.use_cases.execute_gesture import ExecuteGesture


router = APIRouter(
    prefix="/hand",
    tags=["Hand Control"],
)


def get_hand_service() -> HandService:
    """Dependency injection for HandService."""
    return HandService.get_instance()


@router.get("/status", response_model=HandStatusResponse)
async def get_hand_status(
    hand_service: HandService = Depends(get_hand_service)
):
    """Get the current status of the hand."""
    try:
        status = hand_service.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_hand(
    profile_name: str,
    hand_service: HandService = Depends(get_hand_service)
):
    """Initialize the hand with a specific profile."""
    use_case = InitializeHand(hand_service)
    try:
        result = use_case.execute(profile_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gesture", response_model=GestureResponse)
async def execute_gesture(
    request: GestureExecute,
    hand_service: HandService = Depends(get_hand_service)
):
    """Execute a predefined gesture."""
    use_case = ExecuteGesture(hand_service)
    try:
        result = use_case.execute(request.gesture_name)
        return GestureResponse(
            gesture_name=request.gesture_name,
            status="success",
            message=f"Gesto '{request.gesture_name}' ejecutado correctamente"
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/profiles")
async def list_profiles(
    hand_service: HandService = Depends(get_hand_service)
):
    """List available hand profiles."""
    profiles = hand_service.get_available_profiles()
    return {"profiles": profiles}


@router.get("/gestures")
async def list_gestures(
    profile_name: str = None,
    hand_service: HandService = Depends(get_hand_service)
):
    """List available gestures, optionally filtered by profile."""
    gestures = hand_service.get_available_gestures(profile_name)
    return {"gestures": gestures}


@router.post("/session/start", response_model=SessionResponse)
async def start_training_session(
    config: TrainingSessionConfig,
    hand_service: HandService = Depends(get_hand_service)
):
    """Start a training session with specified configuration."""
    # Initialize hand if not already initialized
    if not hand_service.is_initialized:
        use_case = InitializeHand(hand_service)
        try:
            use_case.execute(config.hand_profile)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize hand: {str(e)}")
    
    # Import here to avoid circular dependencies
    from app.services.hand_session_runner import TrainingSession
    
    try:
        session = TrainingSession(config.dict())
        # Run session in background or return session info
        # For now, we'll just return session details
        return SessionResponse(
            session_id=session.session_id,
            status="started",
            profile_name=config.hand_profile,
            gestures=config.gestures
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
