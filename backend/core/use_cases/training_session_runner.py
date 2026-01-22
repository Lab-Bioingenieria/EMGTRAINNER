from hand.session_runner import TrainingSession

class TrainingSessionUseCase:

    async def create(self, payload):
        config = {
            "hand_profile": payload.hand_profile,
            "gestures": payload.session.gestures,
            "gesture_duration": payload.session.gesture_duration_sec,
            "rest_time": payload.session.rest_time_sec,
            "port": payload.hardware.serial_port,
        }

        session = TrainingSession(config)
        return {
            "uuid": session.session_id,
            "status": "CREATED",
        }

    async def start(self, session_id: str):
        #lanzar en background
        pass
