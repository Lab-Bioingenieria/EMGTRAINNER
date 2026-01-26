# Guía Backend (FastAPI, Servicios, Modelos)

Resumen corto: el backend ofrece endpoints para EMG (streaming y control), gestión de órdenes/sesiones, control de la mano (Dynamixel) y almacenamiento CSV.

- Entrada principal:
  - `backend/core/server.py` crea `app` y monta `api` (prefijo `/v1`).

- Rutas importantes (ejemplos):
  - `api/v1/monitoring/sensor.py` — endpoints y WebSocket para EMG:
    - `websocket /v1/ws/emg-stream` — streaming real-time EMG.
    - `GET /v1/monitoring/sensor/emg/status`.
    - `POST /v1/monitoring/sensor/emg/start` / `/stop` / `/connect` / `/disconnect`.
    - `POST /v1/monitoring/sensor/emg/session/info` (set patient name).
    - `POST /v1/monitoring/sensor/emg/label` (set movement label).
    - `GET /v1/monitoring/sensor/emg/sample`.

  - `api/v1/microcontrollers/health_micro.py` — `GET /v1/microcontrollers/health_micro/ports` (serial ports).
  - `api/v1/storage/router.py` — `GET /v1/storage/sessions` y `GET /v1/storage/sessions/{filename}` (descarga CSV).
  - `app.routers.orders` — endpoints `POST /v1/orders`, `GET /v1/orders/{id}`, `POST /v1/orders/{id}/start/finish`, `POST /v1/orders/{id}/upload`.
  - `api/v1/training_sessions/router.py` — `POST /v1/training-sessions/hand/session/start` (iniciar secuencia de gestos usando `HandService`).

- Servicios y módulos clave:
  - `app.services.emg_service` — manager de conexión al ESP32, parsing de líneas, streaming y CSV write.
  - `hand.services.HandService` — inicializa perfil de mano, conecta `DynamixelInterface`, `initialize_hand(profile)` y `execute_gesture(name)`.
  - `hand.control.hand_controller` — mapea GESTURES → targets (motor ticks), configura motores y llama a `DynamixelInterface.move_motors_sync_safe`.
  - `hand.models.gestures` — diccionario `GESTURES` con definiciones por perfil (finger->joint->angle_deg).
  - `hand.models.hand_profiles` — perfiles `HandProfile` con límites, grupos de ejecución, orientación y mapeo motor/joint.

- Qué hace el backend al recibir llamadas relevantes:
  - `POST /v1/monitoring/sensor/emg/start`: valida que el dispositivo esté conectado y llama a `emg_service.start_streaming(category)`; devuelve estado de streaming.
  - `POST /v1/monitoring/sensor/emg/label`: actualiza etiqueta actual para anotar CSV y experimentos.
  - `POST /v1/training-sessions/hand/session/start` (router): crea `HandService`, `initialize_hand(profile)`, y llama `execute_gesture` por cada gesto en la lista; cada `execute_gesture` realiza conversiones de ángulo→ticks y mueve motores de forma segura y sincronizada.
  - `POST /v1/orders`: crea orden (DB) y la usa para coordinar adquisición de datos; `POST /v1/orders/{id}/start` hace el cambio de estado de la orden.

- Workers / Colas: carpeta `worker/` existe para tareas background; en el repo actual no hay una cola explícita usada por el flujo de entrenamiento, pero CSV y tareas de postprocesado podrían delegarse a `worker.tasks`.

- Recomendaciones para gemelo virtual:
  - Añadir endpoint simulado opcional `POST /v1/hand/simulate` o `ws /v1/ws/joint-state` que emita `JointState` para pruebas (ver GESTURE_TRAINING_FLOW.md).
  - Mantener `hand.models.gestures` sincronizado con el formato `JointState` (exportable).
