from fastapi import APIRouter
from pydantic import BaseModel
from hand.services.hand_service import HandService

router = APIRouter(prefix="/hand", tags=["Hand"])

hand_service = HandService()


class HandSessionRequest(BaseModel):
    profile: str
    gestures: list[str]


@router.post("/session/start")
def start_hand_session(req: HandSessionRequest):
    hand_service.initialize_hand(req.profile)

    for gesture in req.gestures:
        hand_service.execute_gesture(gesture)

    return {
        "status": "ok",
        "profile": req.profile,
        "gestures": req.gestures,
    }
