# Guía Frontend (Vistas, Rutas, Stores, Servicios)

Resumen corto: el módulo de entrenamiento de gestos está implementado principalmente en:

- Vistas clave:
  - `frontend/src/views/patient/PatientSessionView.vue` — flujo supervisado (sesión guiada, fullscreen, tutorial, training).
  - `frontend/src/views/patient/PatientFreeView.vue` — modo libre/independiente (selección de gestos, configuración, ejecución y guardado CSV).

- Componentes que renderizan / ayudan al entrenamiento:
  - `frontend/src/components/patient/PatientHandVisualization.vue` — visualizador actual (imagen-based). Ideal reemplazo por GLB viewer (Three/TresJS).
  - `frontend/src/components/patient/GestureProgress.vue` — barra de progreso del circuito.
  - `frontend/src/components/patient/RadialTimer.vue` — temporizador circular.
  - `frontend/src/components/patient/SessionCodeInput.vue` — entrada de código de sesión.

- Rutas relevantes (ver `frontend/src/router/index.ts`):
  - `/patient` → `PatientSessionView.vue`
  - `/patient/free` → `PatientFreeView.vue`

- Stores / Estado (Pinia):
  - `src/stores/session.store.ts` — pensado para almacenar estado de sesión; actualmente vacío (implementación por hacer).
  - `src/stores/patient.store.ts` — paciente/selección; actualmente vacío.
  - Nota: la vista mantiene mucho estado local; para gemelo virtual conviene mover `JointState` y viewer state a un store compartido.

- Servicios (llamadas a backend):
  - `src/services/emg.service.ts` → endpoints usados:
    - `GET /v1/monitoring/sensor/emg/status` (estado conexión)
    - `POST /v1/monitoring/sensor/emg/start` (iniciar sesión EMG)
    - `POST /v1/monitoring/sensor/emg/stop` (detener)
    - `POST /v1/monitoring/sensor/emg/session/info` (set patient name)
    - `POST /v1/monitoring/sensor/emg/label` (set movement label)
    - `POST /v1/monitoring/sensor/emg/connect` (conectar)
    - `GET /v1/storage/sessions` (listar sesiones / obtener último CSV)
  - `src/services/patient.service.ts` → orders API:
    - `POST /v1/orders` (crear orden)
    - `GET /v1/orders/{orderId}`
    - `GET /v1/orders/pending?device_id=...` (orden pendiente por dispositivo)
    - `POST /v1/orders/{orderId}/start` y `/finish`

Recomendaciones prácticas para integrar el gemelo virtual (frontend):
- Reemplazar `PatientHandVisualization.vue` por un nuevo componente `HandViewer.vue` que use TresJS/Three.js para cargar `glb`.
- Exponer en un `Pinia` store el `JointState` (objeto serializable) y una API `applyJointState(j: JointState)` con smoothing/interpolación.
- Mantener una tabla de mapeo `motor_id -> bone_name` en la configuración (JSON) y un `profile` con límites y cero absoluto.
