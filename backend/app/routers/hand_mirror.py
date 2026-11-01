from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.hand_mirror_service import hand_mirror_service
from core.fastapi.dependencies.authentication import AuthenticationRequired

router = APIRouter(
    prefix="/hand/mirror",
    tags=["Hand Mirror"],
    dependencies=[Depends(AuthenticationRequired)],
)


class CalibrationStart(BaseModel):
    """Gesto de la contraccion de la calibracion (``esferico`` por defecto, o ``cerrar``)."""

    gesture: Optional[str] = None


class StudyStart(BaseModel):
    """Datos de la sesion del estudio; sin nombre se guarda como ``Guest``."""

    name: Optional[str] = None
    age: Optional[str] = None
    notes: Optional[str] = None     # colocacion de los sensores, observaciones
    reps: int = 5                   # repeticiones por dedo
    movements: Optional[List[str]] = None  # por defecto todos: 5 dedos + 7 gestos


def _status_payload() -> Dict[str, Any]:
    """Estado completo del espejo: mano, vista previa en vivo, calibracion y grabacion.

    - ``active`` / ``activation`` / ``last_error``: lazo que mueve la mano fisica.
    - ``monitoring``: el streaming esta encendido por el monitor de la pantalla.
    - ``signal`` / ``live`` / ``channels``: lo que ven los sensores ahora mismo
      (cierre 0..1 y nivel calibrado de cada canal), funciona aunque la mano
      fisica este detenida.
    - ``calibration``: progreso del asistente y calibracion vigente.
    - ``study``: estudio de calibracion por dedo (paso actual, progreso, carpeta guardada).
    - ``gesture``: movimiento detectado por el clasificador entrenado (solo informativo:
      no mueve la mano ni cambia el cierre proporcional).
    """
    live = hand_mirror_service.live_status()
    return {
        "active": hand_mirror_service.is_active,
        "activation": hand_mirror_service.activation,
        "last_error": hand_mirror_service.last_error,
        "monitoring": hand_mirror_service.monitoring,
        "signal": live["signal"],
        "live": live["activation"],
        "channels": live["channels"],
        "calibration": hand_mirror_service.calibration_status(),
        "study": hand_mirror_service.study_status(),
        "gesture": hand_mirror_service.gesture_status(),
    }


@router.post("/start")
async def start_mirror():
    """Arranca el modo Espejo en Tiempo Real.

    No sigue el protocolo de gestos: mueve la mano de forma continua segun
    la amplitud cruda que estan mandando los sensores en este momento.
    Falla con 409 si el interlock de emergencia sigue activo (igual que
    ``/hand/session/start``) y con 400 ante cualquier otro problema: mano o
    sensor no conectados, calibracion pendiente o en curso.
    """
    try:
        await hand_mirror_service.start()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _status_payload()


@router.post("/stop")
async def stop_mirror():
    await hand_mirror_service.stop()
    return _status_payload()


@router.get("/status")
async def mirror_status():
    return _status_payload()


@router.post("/monitor/start")
async def start_monitor():
    """Enciende el streaming sin grabar mientras la pantalla esta abierta (se renueva
    con cada ``GET /status`` y se apaga solo si deja de sondear)."""
    try:
        await hand_mirror_service.start_monitor()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _status_payload()


@router.post("/monitor/stop")
async def stop_monitor():
    await hand_mirror_service.stop_monitor()
    return _status_payload()


@router.post("/calibration/start")
async def start_calibration(body: Optional[CalibrationStart] = None):
    """Inicia el asistente de calibracion (reposo + una contraccion fuerte).

    No mueve la mano, asi que no exige el reset del e-stop. Falla con 400 si el
    espejo esta activo, hay una grabacion en curso o el sensor no esta conectado.
    """
    try:
        await hand_mirror_service.start_calibration(body.gesture if body else None)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _status_payload()


@router.post("/calibration/cancel")
async def cancel_calibration():
    await hand_mirror_service.cancel_calibration()
    return _status_payload()


@router.post("/calibration/reset")
async def reset_calibration():
    """Descarta la calibracion vigente y vuelve al comportamiento sin calibrar."""
    hand_mirror_service.clear_calibration()
    return _status_payload()


@router.post("/study/start")
async def start_study(body: Optional[StudyStart] = None):
    """Inicia el estudio de calibracion (reposo + cada dedo por separado + gestos completos, varias repeticiones).

    Guarda la sesion en ``storage/calibration_studies/<nombre>/<fecha>/`` (``data.csv``
    etiquetado + ``params.json``). No mueve la mano. Falla con 400 si el espejo esta
    activo, hay una calibracion en curso o el sensor no esta conectado.
    """
    body = body or StudyStart()
    try:
        await hand_mirror_service.start_study(body.name, body.age, body.notes, body.reps, body.movements)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _status_payload()


@router.post("/study/cancel")
async def cancel_study():
    """Cancela el estudio; lo grabado hasta ese momento queda guardado como ``cancelada``."""
    await hand_mirror_service.cancel_study()
    return _status_payload()


@router.get("/study/sessions")
async def study_sessions():
    """Sesiones del estudio ya guardadas (mas recientes primero)."""
    return {"sessions": hand_mirror_service.study_sessions()}
