"""Endpoints de la sesion supervisada en vivo (doctor <-> paciente)."""

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.services.live_session_manager import (
    LiveSessionError,
    live_session_manager,
)

router = APIRouter(tags=["Live Session"])


@router.get("/v1/live-session/{code}")
async def get_live_session(code: str):
    """Consulta puntual del estado de una sala (util para depurar o para un
    chequeo previo del codigo desde el cliente)."""
    session = live_session_manager.get(code)
    if session is None:
        raise HTTPException(status_code=404, detail="Codigo de sesion no valido")
    return session.snapshot()


@router.websocket("/ws/live-session")
async def live_session_endpoint(
    websocket: WebSocket,
    role: str = Query(..., pattern="^(doctor|patient)$"),
    code: str | None = Query(None),
):
    """Canal de sincronizacion.

    - El doctor se conecta sin codigo: el servidor crea la sala y le devuelve
      el unico codigo de la sesion dentro del primer mensaje de estado.
    - El paciente se conecta con ese codigo. Si no coincide con ninguna sala
      activa se le responde `error/invalid_code` y se cierra la conexion, de
      modo que no puede avanzar en la plataforma con un codigo incorrecto.
    """
    await websocket.accept()

    try:
        if role == "doctor":
            session = await live_session_manager.connect_doctor(websocket, code)
        else:
            if not code:
                await websocket.send_json(
                    {"type": "error", "reason": "missing_code", "message": "Ingrese el codigo de la sesion."}
                )
                await websocket.close()
                return
            session = await live_session_manager.connect_patient(websocket, code)
    except LiveSessionError as exc:
        await websocket.send_json(
            {"type": "error", "reason": exc.reason, "message": exc.message}
        )
        await websocket.close()
        return

    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict):
                continue
            await live_session_manager.handle_action(session, role, message)
    except WebSocketDisconnect:
        await live_session_manager.disconnect(websocket)
    except Exception as exc:  # pragma: no cover - defensivo
        print(f"Live session error: {exc}")
        await live_session_manager.disconnect(websocket)
