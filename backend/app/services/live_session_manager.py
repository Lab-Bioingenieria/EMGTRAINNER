"""Gestor de sesiones supervisadas en vivo (doctor <-> paciente).

Mantiene en memoria una "sala" por cada codigo de sesion. El estado es
autoritativo en el servidor: cualquiera de los dos clientes envia una accion,
el servidor la valida, la aplica y difunde el estado completo a ambos.

Asi se resuelven tres problemas del flujo anterior:
  1. El codigo de sesion se genera UNA sola vez (aqui) y es el mismo en todas
     las pantallas del doctor y del paciente.
  2. El doctor solo avanza de "esperando conexion" cuando el paciente se une
     realmente con el codigo correcto.
  3. El paciente recibe el modo y los gestos que el doctor selecciono, no una
     eleccion aleatoria local.
"""

from __future__ import annotations

import asyncio
import random
import string
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

# Fases del ciclo de vida de una sesion supervisada.
#   waiting   -> el doctor publico el codigo y espera al paciente
#   connected -> el paciente valido el codigo y ve los protocolos de inicio
#   ready     -> el paciente pulso "Iniciar sesion" y espera al doctor
#   running   -> el doctor pulso "Iniciar": la sesion corre en ambos lados
#   paused    -> pausa controlada por el doctor
#   finished  -> sesion terminada, los datos ya se guardaron
PHASES = ("waiting", "connected", "ready", "running", "paused", "finished")

CODE_LENGTH = 6
CODE_ALPHABET = string.digits


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LiveSession:
    """Estado compartido de una sesion doctor/paciente."""

    code: str
    protocol_name: str = ""
    training_mode: Optional[str] = None  # "TLC" | "LLC"
    gestures: List[Dict[str, str]] = field(default_factory=list)
    gesture_duration: int = 5
    rest_time: int = 5
    repetitions: int = 1

    phase: str = "waiting"
    current_step: int = 0
    # Nombre del gesto en curso, reportado por el paciente. El doctor NO puede
    # deducirlo indexando `gestures` con `current_step`: en TLC la lista del
    # paciente es el protocolo repetido N veces, asi que el indice se sale de
    # rango en cuanto empieza la segunda repeticion.
    current_gesture: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    patient_name: str = ""
    patient_connected: bool = False
    patient_ready: bool = False

    # Resultados de la sesion
    csv_filename: str = ""
    duration_seconds: int = 0
    finished_at: str = ""

    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    doctor_ws: Optional[WebSocket] = None
    patient_ws: Optional[WebSocket] = None

    def snapshot(self) -> Dict[str, Any]:
        """Representacion serializable que se envia a los dos clientes."""
        return {
            "code": self.code,
            "protocolName": self.protocol_name,
            "trainingMode": self.training_mode,
            "gestures": self.gestures,
            "gestureDuration": self.gesture_duration,
            "restTime": self.rest_time,
            "repetitions": self.repetitions,
            "phase": self.phase,
            "currentStep": self.current_step,
            "currentGesture": self.current_gesture,
            "totalSteps": self.total_steps,
            "completedSteps": self.completed_steps,
            "csvFilename": self.csv_filename,
            "durationSeconds": self.duration_seconds,
            "finishedAt": self.finished_at,
            "patientName": self.patient_name,
            "patientConnected": self.patient_connected,
            "patientReady": self.patient_ready,
            "doctorConnected": self.doctor_ws is not None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class LiveSessionManager:
    """Registro de salas activas indexadas por codigo."""

    def __init__(self) -> None:
        self._sessions: Dict[str, LiveSession] = {}
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ codigo

    def _generate_code(self) -> str:
        """Codigo numerico unico entre las salas activas."""
        for _ in range(100):
            code = "".join(random.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
            if code not in self._sessions:
                return code
        # Fallback practicamente inalcanzable.
        return str(random.randint(10**(CODE_LENGTH - 1), 10**CODE_LENGTH - 1))

    def get(self, code: str) -> Optional[LiveSession]:
        return self._sessions.get(code)

    def list_codes(self) -> List[str]:
        return list(self._sessions.keys())

    # ------------------------------------------------------------- conexiones

    async def connect_doctor(
        self, websocket: WebSocket, code: Optional[str] = None
    ) -> LiveSession:
        """Crea una sala nueva (o reengancha una existente) para el doctor.

        Si el doctor no envia codigo, el servidor genera uno. Ese es el unico
        punto del sistema donde nace un codigo de sesion.
        """
        async with self._lock:
            session = self._sessions.get(code) if code else None
            if session is None:
                new_code = code or self._generate_code()
                session = LiveSession(code=new_code)
                self._sessions[new_code] = session

            previous = session.doctor_ws
            session.doctor_ws = websocket
            session.updated_at = _now()

        if previous is not None and previous is not websocket:
            await _safe_close(previous, reason="Sesion reabierta en otra pestana")

        await self.broadcast(session)
        return session

    async def connect_patient(self, websocket: WebSocket, code: str) -> LiveSession:
        """Une al paciente a una sala existente validando el codigo.

        Lanza LiveSessionError si el codigo no existe, la sesion ya termino o
        ya hay otro paciente conectado.
        """
        async with self._lock:
            session = self._sessions.get(code)
            if session is None:
                raise LiveSessionError("invalid_code", "El codigo no corresponde a ninguna sesion activa.")
            if session.phase == "finished":
                raise LiveSessionError("session_finished", "Esa sesion ya finalizo.")
            if session.patient_ws is not None and session.patient_ws is not websocket:
                raise LiveSessionError("session_busy", "Ya hay un paciente conectado a esa sesion.")

            session.patient_ws = websocket
            session.patient_connected = True
            # Llegar al codigo correcto es lo que saca al doctor de "esperando
            # conexion"; nunca un temporizador.
            if session.phase == "waiting":
                session.phase = "connected"
            session.updated_at = _now()

        await self.broadcast(session)
        return session

    async def disconnect(self, websocket: WebSocket) -> None:
        """Limpia la referencia al socket que se cayo y avisa al otro lado."""
        target: Optional[LiveSession] = None
        async with self._lock:
            for session in self._sessions.values():
                if session.doctor_ws is websocket:
                    session.doctor_ws = None
                    target = session
                    break
                if session.patient_ws is websocket:
                    session.patient_ws = None
                    session.patient_connected = False
                    session.patient_ready = False
                    # Si el paciente se cae antes de empezar, el doctor vuelve
                    # a la pantalla de espera con el MISMO codigo.
                    if session.phase in ("connected", "ready"):
                        session.phase = "waiting"
                    target = session
                    break

            # Sala huerfana: se descarta para no acumular memoria.
            if target is not None and target.doctor_ws is None and target.patient_ws is None:
                self._sessions.pop(target.code, None)
                target.updated_at = _now()
                return

        if target is not None:
            target.updated_at = _now()
            await self.broadcast(target)

    # ---------------------------------------------------------------- acciones

    async def handle_action(
        self, session: LiveSession, role: str, message: Dict[str, Any]
    ) -> None:
        """Aplica una accion enviada por uno de los clientes."""
        action = message.get("type")

        if role == "doctor":
            if action == "config":
                session.protocol_name = message.get("protocolName", session.protocol_name)
                session.training_mode = message.get("trainingMode", session.training_mode)
                gestures = message.get("gestures")
                if isinstance(gestures, list):
                    session.gestures = gestures
                session.gesture_duration = int(message.get("gestureDuration", session.gesture_duration))
                session.rest_time = int(message.get("restTime", session.rest_time))
                session.repetitions = int(message.get("repetitions", session.repetitions))

            elif action == "start_waiting":
                # No se regenera el codigo: el que ya tiene el paciente sigue valido.
                if session.phase in ("waiting", "connected"):
                    pass
                else:
                    session.phase = "waiting"

            elif action == "start":
                # Solo arranca si el paciente confirmo sus protocolos de inicio.
                if session.patient_ready and session.phase in ("ready", "paused"):
                    session.phase = "running"

            elif action == "pause":
                if session.phase == "running":
                    session.phase = "paused"

            elif action == "resume":
                if session.phase == "paused":
                    session.phase = "running"

            elif action == "finish":
                session.phase = "finished"
                session.finished_at = _now()
                session.duration_seconds = int(
                    message.get("durationSeconds", session.duration_seconds)
                )

            elif action == "reset":
                session.phase = "waiting"
                session.training_mode = None
                session.gestures = []
                session.current_step = 0
                session.current_gesture = ""
                session.total_steps = 0
                session.completed_steps = 0
                session.patient_ready = False
                session.protocol_name = ""
                session.csv_filename = ""
                session.duration_seconds = 0
                session.finished_at = ""

            elif action == "step":
                session.current_step = int(message.get("step", session.current_step))

        elif role == "patient":
            if action == "identify":
                session.patient_name = str(message.get("patientName", "") or "")

            elif action == "ready":
                # El paciente termino los protocolos de inicio: esto habilita
                # el boton "Iniciar" del doctor, no arranca la sesion.
                session.patient_ready = True
                if session.phase in ("connected", "waiting"):
                    session.phase = "ready"

            elif action == "step":
                # El paciente es la fuente de verdad del avance: manda indice,
                # nombre del gesto y totales para que el doctor no tenga que
                # recalcularlos.
                session.current_step = int(message.get("step", session.current_step))
                session.current_gesture = str(message.get("gestureName", "") or "")
                session.total_steps = int(message.get("totalSteps", session.total_steps))
                session.completed_steps = int(
                    message.get("completedSteps", session.completed_steps)
                )

            elif action == "result":
                # Resultado de la captura: no cambia la fase, solo adjunta el
                # CSV generado para que ambos lados puedan descargarlo.
                session.csv_filename = str(message.get("csvFilename", "") or "")
                session.duration_seconds = int(
                    message.get("durationSeconds", session.duration_seconds)
                )
                session.completed_steps = int(
                    message.get("completedSteps", session.completed_steps)
                )

            elif action == "finish":
                session.phase = "finished"
                session.finished_at = _now()
                session.duration_seconds = int(
                    message.get("durationSeconds", session.duration_seconds)
                )

        if action == "ping":
            return

        session.updated_at = _now()
        await self.broadcast(session)

    # -------------------------------------------------------------- broadcast

    async def broadcast(self, session: LiveSession) -> None:
        payload = {"type": "state", "state": session.snapshot()}
        for ws in (session.doctor_ws, session.patient_ws):
            if ws is None:
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                # El cierre real lo maneja el endpoint al detectar la desconexion.
                pass


class LiveSessionError(Exception):
    """Error de negocio al unirse a una sala (codigo invalido, sala ocupada...)."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason
        self.message = message


async def _safe_close(websocket: WebSocket, reason: str = "") -> None:
    try:
        await websocket.send_json({"type": "closed", "reason": reason})
        await websocket.close()
    except Exception:
        pass


# Instancia global
live_session_manager = LiveSessionManager()
