"""Modo "Espejo en Tiempo Real".

A diferencia del entrenamiento (CE-xx), que reconoce un gesto discreto del
protocolo ("PINZA", "CERRAR", ...) y lo ejecuta una vez, este modo NO
clasifica nada: toma la amplitud cruda que estan mandando los sensores en
este instante y mueve la mano de forma continua y proporcional a esa
amplitud, en tiempo real. Es lo que pidio el tutor: un apartado aparte de
los movimientos ya establecidos, para trabajar directamente con los
valores que arrojan los sensores.

Diseno:

- El unico lector del puerto serie sigue siendo el hilo de
  ``EMGDataService._streaming_loop`` (ver el docstring de
  ``api/v1/monitoring/sensor.py``: dos lectores del mismo puerto corrompen
  las tramas). Este servicio no abre el puerto por su cuenta; solo lee
  ``emg_service.latest_sample``, que ese hilo ya publica.
- Si el streaming no estaba activo, lo arranca con ``record=False`` para no
  mezclar sus muestras en el CSV de una sesion de entrenamiento (este modo
  no sigue ningun protocolo), y lo detiene al salir si fue quien lo prendio.
- El lazo de control corre en un ``asyncio.Task`` a ``TICK_HZ`` con un
  filtro paso-bajo simple sobre la activacion, y escribe los motores con
  ``move_motors_sync_fast`` (sin el monitoreo bloqueante de 1 s de
  ``move_motors_sync_safe``, pensado para un gesto puntual y no para un
  lazo continuo).
- Mapeo canal -> grupo de dedos: cada uno de los (hasta) 3 sensores mueve una
  parte distinta de la mano en vez de que la mano entera se mueva junta sin
  importar cual sensor este mas activo. Se usan los ``execution_groups`` del
  perfil si estan definidos (ej. ``ELEVEN_DOF_RIGHT``/``SIX_DOF_RIGHT``: los 4
  dedos largos vs el pulgar), o si no, cada dedo del perfil por separado (ver
  ``_finger_groups``). Un perfil con un solo grupo (ej. ``TWO_MOTORS``, sin
  dedos distinguibles) sigue moviendose entero con el canal mas activo, igual
  que antes de este mapeo.
- Requiere el interlock de emergencia (``estop_service``) igual que
  ``/hand/session/start``: nunca mueve la mano si el e-stop esta activo, y
  lo vuelve a comprobar en cada tick.
- Calibracion (obligatoria): un asistente guiado de ~16 s mide el reposo y UNA sola
  contraccion fuerte con la que se calibran todos los sensores a la vez (ver ``mirror_calibration``). El
  cierre de la mano sale de la amplitud cruda y limpia (``emg_cleaning``) de
  cada canal normalizada a su propio rango, con zona muerta en reposo. El
  espejo NO arranca sin calibracion: el sensor entrega niveles crudos en
  unidades arbitrarias y sin referencia la mano se iria a un extremo. La calibracion no mueve
  la mano, asi que no exige el e-stop; si se pierde la senal de los sensores,
  el objetivo es 0 (mano abierta) en vez de quedarse con el ultimo valor.
- Estudio de calibracion por dedo (``calibration_study``): protocolo guiado (reposo
  y cada dedo por separado, varias repeticiones) que guarda cada sesion en su
  carpeta (``data.csv`` etiquetado + ``params.json``) para entrenar despues la
  deteccion de cada dedo. No mueve la mano y es independiente de la calibracion
  rapida del espejo.
- Movimiento detectado (``gesture_recognition``): mientras hay streaming, una ventana
  deslizante de la senal limpia se pasa por el clasificador entrenado con
  ``scripts/train_gesture_classifier.py`` (si hay un modelo guardado y calibracion
  vigente). Es SOLO informativo: se muestra en pantalla, pero no cambia el cierre
  proporcional de la mano ni el resto del espejo.
"""
import asyncio
import time
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from app.core.dynamixel_interface import (
    DEFAULT_PROFILE_VELOCITY,
    DEFAULT_PROFILE_ACCELERATION,
    POSITION_MODE,
    DynamixelInterface,
)
from app.schemas.hand_profiles import HandProfile, apply_hand_orientation
from app.services.calibration_study import (
    MOVEMENTS,
    Step,
    StudyError,
    StudyWriter,
    build_protocol,
    list_studies,
    normalize_movements,
    total_seconds,
)
from app.services.emg_cleaning import ALPHA as CLEAN_ALPHA, WINDOW as CLEAN_WINDOW
from app.services.gesture_recognition import MIN_CONFIDENCE as GESTURE_MIN_CONFIDENCE, GestureRecognizer
from app.services.mirror_calibration import (
    CalibrationError,
    ChannelCalibration,
    MirrorCalibration,
    build_channel_calibration,
)
from core.safety.estop import estop_service


class HandMirrorService:
    TICK_HZ = 8.0        # ~125 ms/tick: razonable para XL330 + una lectura de corriente
    SMOOTH_ALPHA = 0.35  # filtro paso-bajo propio, aparte del promedio que ya hace emg_service

    # --- Calibracion (segundos) ---
    CALIB_HZ = 30.0             # frecuencia de muestreo de latest_raw durante la calibracion
    CALIB_PREP_REST_S = 3.0     # aviso antes de medir el reposo
    CALIB_REST_S = 5.0          # medicion de reposo
    CALIB_PREP_CONTRACT_S = 3.0 # aviso antes de la contraccion
    CALIB_CONTRACT_S = 5.0      # medicion de la contraccion (una sola, todos los sensores a la vez)
    CALIB_SETTLE_S = 0.5        # se descarta el inicio de la fase de reposo
    CALIB_CONTRACT_SETTLE_S = 1.0  # ... y el de la contraccion (tiempo de subir la fuerza)
    CALIB_STALE_S = 1.5         # sin muestra nueva en este tiempo = sin senal
    CALIB_WAIT_SIGNAL_S = 3.0   # cuanto esperar la primera muestra al arrancar

    # Gesto con el que se hace la contraccion de la calibracion: (aviso, orden).
    # Por defecto el agarre esferico: en un estudio real fue el que mas separa del reposo;
    # un puño flojo apenas sube el nivel de estos sensores y no pasa la calibracion.
    CALIB_GESTURES = {
        "esferico": (
            "Prepárate: vas a apretar fuerte como si sujetaras una pelota (agarre esférico) y a mantenerlo.",
            "¡Aprieta fuerte como si sujetaras una pelota y mantén!",
        ),
        "cerrar": (
            "Prepárate: vas a cerrar el puño con toda tu fuerza y a mantenerlo.",
            "¡Cierra el puño con fuerza y mantén!",
        ),
    }
    DEFAULT_CALIB_GESTURE = "esferico"

    # --- Monitor y estudio ---
    MONITOR_IDLE_S = 10.0       # sin sondeos de estado en este tiempo, el monitor se apaga solo
    STUDY_HZ = 30.0             # frecuencia con la que se lee la ultima linea durante el estudio
    GESTURE_HZ = 30.0           # frecuencia con la que se alimenta la ventana del clasificador

    def __init__(self) -> None:
        self._task: Optional[asyncio.Task] = None
        self._running = False
        # Nivel 0..1 suavizado de cada uno de los 3 canales EMG (ver ``_finger_groups``
        # y ``_closure_targets``: cada uno mueve un grupo de dedos distinto).
        self._activations: List[float] = [0.0, 0.0, 0.0]
        self._configured_motors: Set[int] = set()
        self.last_error: Optional[str] = None

        self.calibration: Optional[MirrorCalibration] = None
        self._calib_task: Optional[asyncio.Task] = None
        self._calib_state: Dict[str, Any] = self._idle_calib_state()

        # El lector del puerto serie (el hilo de `EMGDataService`) es uno solo y
        # varias funciones lo necesitan encendido a la vez: monitor de la
        # pantalla, calibracion, grabacion y espejo. Cada una lo "reserva" con
        # un nombre; se apaga cuando se libera la ultima, y solo si lo
        # encendimos nosotros (si ya estaba activo por una sesion, no se toca).
        self._stream_holders: Set[str] = set()
        self._stream_owned = False

        self._monitor_task: Optional[asyncio.Task] = None
        self._monitor_seen = 0.0

        # Estudio de calibracion por dedo (guarda cada sesion en disco).
        self.study_writer = StudyWriter()
        self._study_task: Optional[asyncio.Task] = None
        self._study_state: Dict[str, Any] = self._idle_study_state()

        # Movimiento detectado en vivo (solo informativo, ver el docstring del modulo).
        self.gesture = GestureRecognizer()
        self._gesture_task: Optional[asyncio.Task] = None
        self._gesture_result: Optional[Dict[str, Any]] = None

    @property
    def is_active(self) -> bool:
        return self._running

    @property
    def activation(self) -> float:
        """Ultimo valor de cierre aplicado, resumido en un solo numero (0 = mano abierta,
        1 = cerrada): el mas alto de los grupos de dedos, para mostrar en pantalla. Los
        grupos individuales pueden estar en valores distintos, ver ``_closure_targets``."""
        return max(self._activations) if self._activations else 0.0

    async def start(self) -> None:
        if self._running:
            return

        if self.calibrating:
            raise RuntimeError("Espera a que termine la calibración antes de iniciar el espejo")
        if self.studying:
            raise RuntimeError("Espera a que termine el estudio antes de iniciar el espejo")
        if self.calibration is None:
            # El sensor entrega el nivel crudo en unidades arbitrarias (~500-1500
            # en reposo): sin calibrar no hay forma de saber que es "mano abierta"
            # y que es "cerrada", y la mano se iria a un extremo.
            raise RuntimeError("Calibra los sensores antes de iniciar el espejo")

        # Fail-closed: sin reset explicito del e-stop, no se mueve nada.
        estop_service.assert_movement_allowed()

        from app.services.emg_service import emg_service as svc

        if svc.hand_interface is None:
            svc.connect_hand()
        if svc.hand_interface is None:
            raise RuntimeError("Mano Dynamixel no conectada (adaptador U2D2 no detectado)")

        self._acquire_stream("mirror", svc, "Espejo")

        self.last_error = None
        self._configured_motors.clear()
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        task, self._task = self._task, None
        if task:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

        from app.services.emg_service import emg_service as svc

        for motor_id in self._configured_motors:
            try:
                svc.hand_interface.disable_torque(motor_id)
            except Exception:
                pass
        self._configured_motors.clear()
        self._activations = [0.0, 0.0, 0.0]

        self._release_stream("mirror", svc)

    # ------------------------------------------------------------------
    # Reserva del lector serie (streaming) y monitor de la pantalla
    # ------------------------------------------------------------------
    def _acquire_stream(self, holder: str, svc, category: str) -> None:
        if not svc.serial_manager.is_connected():
            result = svc.connect_to_device()
            if not result.get("success"):
                raise RuntimeError(result.get("message") or "No se pudo conectar el sensor sEMG")
        if not svc.is_streaming:
            svc.start_streaming(category=category, record=False)
            self._stream_owned = True
        was_empty = not self._stream_holders
        self._stream_holders.add(holder)
        if was_empty and self._gesture_task is None:
            self.gesture.reset_window()
            self._gesture_result = None
            self._gesture_task = asyncio.create_task(self._gesture_loop())

    def _release_stream(self, holder: str, svc) -> None:
        self._stream_holders.discard(holder)
        if not self._stream_holders:
            task, self._gesture_task = self._gesture_task, None
            if task and not task.done():
                task.cancel()
            self._gesture_result = None
        if not self._stream_holders and self._stream_owned:
            self._stream_owned = False
            try:
                svc.stop_streaming()
            except Exception:
                pass

    @property
    def monitoring(self) -> bool:
        return "monitor" in self._stream_holders

    async def start_monitor(self) -> None:
        """Mantiene el streaming encendido (sin grabar) mientras la pantalla del espejo
        esta abierta, para que el grafico, la vista previa y las barras por sensor
        muestren datos aunque todavia no se haya iniciado nada. Se renueva con cada
        sondeo de estado y se apaga solo si la pantalla deja de sondear."""
        from app.services.emg_service import emg_service as svc

        self._monitor_seen = time.monotonic()
        if self.monitoring:
            return
        self._acquire_stream("monitor", svc, "Monitor")
        self._monitor_task = asyncio.create_task(self._monitor_watchdog())

    async def stop_monitor(self) -> None:
        from app.services.emg_service import emg_service as svc

        task, self._monitor_task = self._monitor_task, None
        if task and not task.done():
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        self._release_stream("monitor", svc)

    async def _monitor_watchdog(self) -> None:
        try:
            while time.monotonic() - self._monitor_seen <= self.MONITOR_IDLE_S:
                await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            return
        from app.services.emg_service import emg_service as svc

        self._monitor_task = None
        self._release_stream("monitor", svc)

    # ------------------------------------------------------------------
    # Estudio de calibracion por dedo
    # ------------------------------------------------------------------
    @staticmethod
    def _idle_study_state() -> Dict[str, Any]:
        return {
            "state": "idle",        # idle | running | done | error
            "phase": None,          # prepare | rest | contract | relax
            "step": 0,              # 1..steps
            "steps": 0,
            "movement": None,       # clave del movimiento (dedo o gesto) del bloque actual
            "rep": 0,
            "reps": 0,
            "seconds_left": 0.0,
            "total_seconds": 0.0,   # duracion del paso actual
            "elapsed": 0.0,         # segundos transcurridos del estudio completo
            "duration": 0.0,        # duracion total prevista
            "message": "",
            "error": None,
            "file": None,           # carpeta de la sesion guardada
            "rows": 0,
        }

    def _set_study(self, **fields: Any) -> None:
        self._study_state.update(fields)

    @property
    def studying(self) -> bool:
        return self._study_task is not None and not self._study_task.done()

    def study_status(self) -> Dict[str, Any]:
        state = {**self._study_state, "running": self.studying}
        if self.studying:
            state["rows"] = self.study_writer.rows
        return state

    def study_sessions(self) -> List[Dict[str, Any]]:
        return list_studies(self.study_writer.storage_dir)

    async def start_study(
        self,
        name: Optional[str] = None,
        age: Optional[str] = None,
        notes: Optional[str] = None,
        reps: int = 5,
        movements: Optional[List[str]] = None,
    ) -> None:
        if self.studying:
            return
        if self._running:
            raise RuntimeError("Detén el espejo antes de iniciar el estudio")
        if self.calibrating:
            raise RuntimeError("Espera a que termine la calibración antes de iniciar el estudio")
        try:
            steps = build_protocol(movements, reps)
            keys = normalize_movements(movements)
        except StudyError as exc:
            raise RuntimeError(str(exc)) from exc

        from app.services.emg_service import emg_service as svc

        self._acquire_stream("study", svc, "Estudio")
        try:
            path = self.study_writer.start(name, age)
        except Exception as exc:
            self._release_stream("study", svc)
            raise RuntimeError(f"No se pudo crear la carpeta del estudio: {exc}") from exc

        params = {
            "notes": (notes or "").strip()[:500],
            "protocol": {
                "movements": keys,
                "reps": reps,
                "labels": {k: MOVEMENTS[k][0] for k in keys},
                "duration_s": total_seconds(steps),
                "steps": len(steps),
            },
            "signal": {
                "source": "uMyo muscle level via ESP32 (texto)",
                "columns": "emg1..3 crudo; clean1..3 = mediana móvil + EMA",
                "cleaner": {"window": CLEAN_WINDOW, "alpha": CLEAN_ALPHA},
                "sample_hz_target": self.STUDY_HZ,
            },
            "mirror_calibration": self.calibration.to_list() if self.calibration else None,
        }
        self._study_state = {
            **self._idle_study_state(),
            "state": "running", "phase": "prepare", "steps": len(steps), "reps": reps,
            "duration": total_seconds(steps), "message": "Iniciando estudio…", "file": path,
        }
        self._study_task = asyncio.create_task(self._run_study(steps, params))

    async def cancel_study(self) -> None:
        task, self._study_task = self._study_task, None
        if task and not task.done():
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        # _run_study guarda lo grabado hasta ahora y deja el estado en "idle".

    async def _run_study(self, steps: List[Step], params: Dict[str, Any]) -> None:
        from app.services.emg_service import emg_service as svc

        status = "completa"
        state_after: Dict[str, Any] = {}
        elapsed_base = 0.0
        duration = total_seconds(steps)
        try:
            await self._wait_for_signal(svc)
            for index, step in enumerate(steps, start=1):
                await self._study_step(svc, step, index, len(steps), elapsed_base, duration)
                elapsed_base += step.seconds
            state_after = {"state": "done", "message": "Estudio completo. Los datos quedaron guardados."}
        except CalibrationError as exc:  # sin senal / senal perdida
            status = "error"
            state_after = {"state": "error", "error": str(exc)}
        except asyncio.CancelledError:
            status = "cancelada"
            state_after = {"message": "Estudio cancelado. Se guardó lo grabado hasta ese momento."}
        except Exception as exc:  # pragma: no cover - defensivo
            status = "error"
            state_after = {"state": "error", "error": str(exc)}
        finally:
            self._release_stream("study", svc)
            info = self.study_writer.finish(params, status)
            if state_after.get("state") == "error" and info["file"]:
                state_after["error"] += " Se guardó lo grabado hasta ese momento."
            self._study_state = {
                **self._idle_study_state(),
                "file": info["file"], "rows": info["rows"], **state_after,
            }

    async def _study_step(
        self, svc, step: Step, index: int, n_steps: int, elapsed_base: float, duration: float
    ) -> None:
        start = time.monotonic()
        end = start + step.seconds
        settle_until = start + step.settle
        last_t = 0.0
        stale_since: Optional[float] = None
        while True:
            now = time.monotonic()
            left = end - now
            if left <= 0:
                return
            self._set_study(
                phase=step.kind, step=index, steps=n_steps, movement=step.movement, rep=step.rep,
                seconds_left=left, total_seconds=step.seconds,
                elapsed=elapsed_base + (step.seconds - left), duration=duration,
                message=step.message, rows=self.study_writer.rows,
            )
            if step.records:
                latest = getattr(svc, "latest_raw", None)
                fresh = self._fresh_raw(svc, self.CALIB_STALE_S)
                if fresh is None:
                    if stale_since is None:
                        stale_since = now
                    elif now - stale_since > self.CALIB_STALE_S:
                        raise CalibrationError("Se perdió la señal de los sensores durante el estudio.")
                else:
                    stale_since = None
                    sample = svc.latest_sample or {}
                    # Una fila por linea nueva del sensor: no repetir la ultima si no llego nada.
                    if latest and latest[4] != last_t:
                        last_t = latest[4]
                        self.study_writer.write(
                            step, now >= settle_until,
                            (sample.get("dc0"), sample.get("dc1"), sample.get("dc2")),
                            latest[:3], int(latest[4] * 1000),
                        )
            await asyncio.sleep(1.0 / self.STUDY_HZ)

    # ------------------------------------------------------------------
    # Lectura de la senal (compartida por el espejo, la vista previa y la calibracion)
    # ------------------------------------------------------------------
    @staticmethod
    def _fresh_raw(svc, max_age: float) -> Optional[Tuple[Tuple[float, float, float], int]]:
        """((ch0, ch1, ch2), n_canales) de la ultima muestra cruda, o None si es vieja/no hay."""
        latest = getattr(svc, "latest_raw", None)
        if not latest:
            return None
        ch0, ch1, ch2, n, t = latest
        if time.time() - t > max_age:
            return None
        return (ch0, ch1, ch2), n

    def _target_channel_levels(self, svc) -> List[float]:
        """Nivel 0..1 de cada uno de los 3 canales que pide la senal ahora mismo (0 en los
        tres si no hay senal reciente o calibracion; un canal sin calibrar tambien da 0,
        ver ``MirrorCalibration.normalize``). Cada canal mueve un grupo de dedos distinto,
        ver ``_finger_groups``/``_closure_targets``."""
        fresh = self._fresh_raw(svc, self.CALIB_STALE_S)
        if fresh is None or self.calibration is None:
            return [0.0, 0.0, 0.0]
        return self.calibration.normalize(fresh[0])

    def live_status(self) -> Dict[str, Any]:
        """Lo que ve la vista previa: hay senal?, cierre 0..1 y nivel calibrado por canal."""
        from app.services.emg_service import emg_service as svc

        if self.monitoring:
            self._monitor_seen = time.monotonic()  # cada sondeo de la pantalla renueva el monitor

        fresh = self._fresh_raw(svc, self.CALIB_STALE_S)
        if fresh is None:
            return {"signal": False, "activation": 0.0, "channels": []}
        values, _n = fresh
        if self.calibration is None:
            return {"signal": True, "activation": 0.0, "channels": []}
        channels = [round(v, 3) for v in self.calibration.normalize(values)]
        return {"signal": True, "activation": max(channels) if channels else 0.0, "channels": channels}

    # ------------------------------------------------------------------
    # Movimiento detectado (solo informativo, ver el docstring del modulo)
    # ------------------------------------------------------------------
    def _gesture_baseline(self) -> Optional[Tuple[float, float, float]]:
        """Reposo por canal de la calibracion vigente, o None sin calibrar.

        Sin un reposo de referencia el clasificador veria valores crudos en vez de
        relativos al reposo (que es como se entreno, ver ``gesture_features``), asi
        que se prefiere no clasificar antes que clasificar con una escala distinta.
        """
        if self.calibration is None:
            return None
        chs = self.calibration.channels
        return tuple((chs[i].rest_level if i < len(chs) and chs[i] else 0.0) for i in range(3))

    async def _gesture_loop(self) -> None:
        from app.services.emg_service import emg_service as svc

        last_t = 0.0
        try:
            while True:
                latest = getattr(svc, "latest_raw", None)
                if latest and latest[4] != last_t:
                    last_t = latest[4]
                    self.gesture.push(latest[:3])
                    baseline = self._gesture_baseline()
                    self._gesture_result = self.gesture.predict(baseline) if baseline else None
                await asyncio.sleep(1.0 / self.GESTURE_HZ)
        except asyncio.CancelledError:
            pass

    def gesture_status(self) -> Dict[str, Any]:
        """Movimiento detectado ahora mismo, para mostrar en pantalla (nunca mueve la mano)."""
        result = self._gesture_result
        shown = result if result and result["confidence"] >= GESTURE_MIN_CONFIDENCE else None
        return {
            "available": self.gesture.available,
            "calibrated": self.calibration is not None,
            "label": shown["label"] if shown else None,
            "confidence": shown["confidence"] if shown else 0.0,
        }

    # ------------------------------------------------------------------
    # Calibracion
    # ------------------------------------------------------------------
    @staticmethod
    def _idle_calib_state() -> Dict[str, Any]:
        return {
            "state": "idle",        # idle | running | done | error
            "phase": None,          # prepare | measure
            "step": 0,              # 1..steps (1 = reposo, 2 = contraccion)
            "steps": 0,
            "channel": None,        # reservado (siempre None: la contraccion es comun a todos los sensores)
            "gesture": None,        # gesto de la contraccion (clave de CALIB_GESTURES)
            "seconds_left": 0.0,
            "total_seconds": 0.0,
            "message": "",
            "error": None,
        }

    def _set_calib(self, **fields: Any) -> None:
        self._calib_state.update(fields)

    @property
    def calibrating(self) -> bool:
        return self._calib_task is not None and not self._calib_task.done()

    def calibration_status(self) -> Dict[str, Any]:
        return {
            **self._calib_state,
            "running": self.calibrating,
            "calibrated": self.calibration is not None,
            "channels": self.calibration.to_list() if self.calibration else [],
        }

    def clear_calibration(self) -> None:
        self.calibration = None
        self.gesture.reset_window()
        self._gesture_result = None
        if not self.calibrating:
            self._calib_state = self._idle_calib_state()

    async def start_calibration(self, gesture: Optional[str] = None) -> None:
        if self.calibrating:
            return
        gesture = gesture or self.DEFAULT_CALIB_GESTURE
        if gesture not in self.CALIB_GESTURES:
            raise RuntimeError(f"Gesto de calibración desconocido: {gesture}")
        if self._running:
            raise RuntimeError("Detén el espejo antes de calibrar")
        if self.studying:
            raise RuntimeError("Espera a que termine el estudio antes de calibrar")

        from app.services.emg_service import emg_service as svc

        self._acquire_stream("calibration", svc, "Calibracion")

        self._calib_state = self._idle_calib_state()
        self._set_calib(state="running", phase="prepare", message="Iniciando calibración…", gesture=gesture)
        self._calib_task = asyncio.create_task(self._run_calibration(gesture))

    async def cancel_calibration(self) -> None:
        task, self._calib_task = self._calib_task, None
        if task and not task.done():
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
        # El propio _run_calibration deja el estado en "idle" al cancelarse.

    async def _wait_for_signal(self, svc) -> int:
        deadline = time.monotonic() + self.CALIB_WAIT_SIGNAL_S
        while time.monotonic() < deadline:
            fresh = self._fresh_raw(svc, self.CALIB_STALE_S)
            if fresh is not None and fresh[1] > 0:
                return fresh[1]
            await asyncio.sleep(0.1)
        raise CalibrationError(
            "No llegan datos de los sensores. Verifica que estén encendidos y conectados."
        )

    async def _countdown(self, step: int, channel: Optional[int], seconds: float, message: str) -> None:
        end = time.monotonic() + seconds
        while True:
            left = end - time.monotonic()
            if left <= 0:
                return
            self._set_calib(
                phase="prepare", step=step, channel=channel,
                seconds_left=left, total_seconds=seconds, message=message,
            )
            await asyncio.sleep(0.1)

    async def _measure(
        self, svc, step: int, channel: Optional[int], seconds: float, message: str,
        settle: Optional[float] = None,
    ) -> List[Tuple[float, float, float]]:
        samples: List[Tuple[float, float, float]] = []
        start = time.monotonic()
        end = start + seconds
        settle_until = start + (self.CALIB_SETTLE_S if settle is None else settle)
        stale_since: Optional[float] = None
        while True:
            now = time.monotonic()
            if end - now <= 0:
                break
            self._set_calib(
                phase="measure", step=step, channel=channel,
                seconds_left=end - now, total_seconds=seconds, message=message,
            )
            fresh = self._fresh_raw(svc, self.CALIB_STALE_S)
            if fresh is None:
                if stale_since is None:
                    stale_since = now
                elif now - stale_since > self.CALIB_STALE_S:
                    raise CalibrationError("Se perdió la señal de los sensores durante la calibración.")
            else:
                stale_since = None
                if now >= settle_until:
                    samples.append(fresh[0])
            await asyncio.sleep(1.0 / self.CALIB_HZ)
        return samples

    async def _run_calibration(self, gesture: str = DEFAULT_CALIB_GESTURE) -> None:
        from app.services.emg_service import emg_service as svc

        try:
            n = await self._wait_for_signal(svc)
            # Dos pasos: reposo y UNA sola contraccion fuerte con la que se
            # calibran todos los sensores a la vez. Los sensores van en una
            # misma correa, casi sobre el mismo musculo, asi que no tiene
            # sentido pedir una contraccion por sensor.
            self._set_calib(steps=2)

            await self._countdown(
                1, None, self.CALIB_PREP_REST_S,
                "Prepárate: relaja por completo el brazo y déjalo quieto.",
            )
            rest = await self._measure(
                svc, 1, None, self.CALIB_REST_S,
                "Reposo: mantén el brazo relajado, sin moverte.",
            )

            await self._countdown(
                2, None, self.CALIB_PREP_CONTRACT_S, self.CALIB_GESTURES[gesture][0],
            )
            contraction = await self._measure(
                svc, 2, None, self.CALIB_CONTRACT_S, self.CALIB_GESTURES[gesture][1],
                settle=self.CALIB_CONTRACT_SETTLE_S,
            )

            # Cada sensor se calibra con su propio reposo y su propia respuesta a
            # la contraccion. Un sensor que casi no responde (mal puesto o fuera
            # del musculo) se ignora, en vez de tumbar toda la calibracion; solo
            # falla si NINGUNO responde.
            channels: List[Optional[ChannelCalibration]] = []
            failures: Dict[int, str] = {}
            for i in range(n):
                try:
                    channels.append(
                        build_channel_calibration(
                            [s[i] for s in rest],
                            [s[i] for s in contraction],
                        )
                    )
                except CalibrationError as exc:
                    channels.append(None)
                    failures[i] = str(exc)
            channels += [None] * (3 - n)

            if not any(c is not None for c in channels):
                hint = (
                    " Prueba otro gesto para calibrar (agarre esférico o puño), apretando más fuerte."
                )
                raise CalibrationError((failures[0] if failures else "No se pudo calibrar ningún sensor.") + hint)

            message = "Calibración lista. Puedes iniciar el espejo."
            if failures:
                ignored = ", ".join(str(i + 1) for i in sorted(failures))
                message = (
                    f"Calibración lista, pero el sensor {ignored} casi no respondió y se ignora. "
                    "Revisa su posición o contacto con la piel y recalibra si quieres usarlo."
                )

            self.calibration = MirrorCalibration(channels)
            self.gesture.reset_window()  # el reposo de referencia cambio
            self._gesture_result = None
            self._calib_state = {**self._idle_calib_state(), "state": "done", "message": message}
        except CalibrationError as exc:
            self._calib_state = {**self._idle_calib_state(), "state": "error", "error": str(exc)}
        except asyncio.CancelledError:
            self._calib_state = {**self._idle_calib_state(), "message": "Calibración cancelada."}
        except Exception as exc:  # pragma: no cover - defensivo: nunca dejar el estado en "running"
            self._calib_state = {**self._idle_calib_state(), "state": "error", "error": str(exc)}
        finally:
            self._release_stream("calibration", svc)

    def _configure_once(self, dx: DynamixelInterface, profile: HandProfile) -> None:
        for finger in profile.fingers.values():
            for motor in finger.motors.values():
                if motor.locked or motor.motor_id in self._configured_motors:
                    continue
                dx.set_operating_mode(motor.motor_id, POSITION_MODE)
                dx.set_current_limit(motor.motor_id, dx.amps_to_current_units(motor.max_current_a))
                dx.set_profile_velocity(motor.motor_id, DEFAULT_PROFILE_VELOCITY)
                dx.set_profile_acceleration(motor.motor_id, DEFAULT_PROFILE_ACCELERATION)
                dx.enable_torque(motor.motor_id)
                self._configured_motors.add(motor.motor_id)

    @staticmethod
    def _finger_groups(profile: HandProfile) -> List[List[str]]:
        """Grupos de dedos que se mueven juntos en el Espejo continuo, cada uno con su
        propio canal EMG (ver ``_closure_targets``): los ``execution_groups`` del perfil
        si estan definidos (``ELEVEN_DOF_RIGHT``/``SIX_DOF_RIGHT``: los 4 dedos largos
        juntos vs el pulgar aparte), o si el perfil no los define (``TWO_DOF_LEFT``,
        ``TWO_MOTORS``), cada dedo del perfil por separado."""
        if profile.execution_groups:
            return profile.execution_groups
        return [[name] for name in profile.fingers]

    def _closure_targets(
        self, dx: DynamixelInterface, profile: HandProfile, channel_levels: Sequence[float]
    ) -> Dict[int, int]:
        """closure 0 -> min_deg de cada motor (grupo abierto); closure 1 -> max_deg (cerrado).

        Con un solo grupo de dedos (perfil sin ``execution_groups`` y con un unico dedo,
        ej. ``TWO_MOTORS``) toda la mano usa un unico cierre, el canal mas activo — igual
        que el comportamiento original, antes de mapear canales a dedos. Con 2 o mas
        grupos, cada uno usa SU PROPIO canal (grupo *i* -> canal *i*; si hay mas grupos
        que canales, los ultimos grupos repiten el ultimo canal): asi cada sensor mueve
        una parte de la mano en vez de que la mano entera se mueva junta sin importar
        cual sensor este mas activo.
        """
        groups = self._finger_groups(profile)
        uniform = len(groups) <= 1
        targets: Dict[int, int] = {}
        for group_idx, finger_names in enumerate(groups):
            closure = max(channel_levels) if uniform else channel_levels[min(group_idx, len(channel_levels) - 1)]
            for name in finger_names:
                finger = profile.fingers.get(name)
                if finger is None:
                    continue
                for motor in finger.motors.values():
                    if motor.locked:
                        continue
                    deg = motor.min_deg + (motor.max_deg - motor.min_deg) * closure
                    oriented = apply_hand_orientation(deg, motor, profile.side)
                    targets[motor.motor_id] = dx.degrees_to_ticks_centered(oriented)
        return targets

    async def _run(self) -> None:
        from app.services.emg_service import emg_service as svc

        dx = svc.hand_interface
        profile = svc.hand_profile
        period = 1.0 / self.TICK_HZ

        try:
            self._configure_once(dx, profile)
            while self._running:
                try:
                    estop_service.assert_movement_allowed()
                except Exception as exc:
                    self.last_error = str(exc)
                    break

                target_levels = self._target_channel_levels(svc)
                self._activations = [
                    a + (t - a) * self.SMOOTH_ALPHA for a, t in zip(self._activations, target_levels)
                ]

                targets = self._closure_targets(dx, profile, self._activations)
                try:
                    dx.move_motors_sync_fast(targets)
                except Exception as exc:
                    self.last_error = str(exc)
                    break

                await asyncio.sleep(period)
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
            self._release_stream("mirror", svc)


# Instancia singleton, igual que `emg_service`.
hand_mirror_service = HandMirrorService()
