# Flujo de Entrenamiento de Gestos y Gemelo Virtual

Objetivo: permitir visualizar y reproducir gestos en un rig 3D (GLB) desde datos reales o simulados, con un formato de estado articular independiente del hardware.

1) Resumen de piezas (tu división A–D)

- A) Modelo 3D exportable y controlable
  - En Blender: crear rig con huesos nombrados consistentemente (ej.: `thumb_mcp`, `thumb_ip`, `index_mcp`, `index_pip`, `index_dip`, `wrist_yaw`).
  - Pintar pesos (skin) y probar deformaciones. Exportar a glTF/GLB.
  - Convención de nombres exigida por el frontend: lista corta de huesos por dedo y ejes en el perfil (ej. `index_proximal`, `index_middle`, `index_distal`, `thumb_mcp`).

- B) Capa de estado articular (independiente del hardware)
  - Definición recomendada (JSON):
    - JointState: {
        "timestamp": 1670000000.123,    // segundos float UTC
        "joints": { "thumb_mcp": 0.52, "index_mcp": -0.23 } // rotación en radianes
      }
  - Alternativa: motor-centric
    - { timestamp, motors: { "1": 45.0, "2": 120.0 } } // grados
  - Recomendación: usar `bone_name -> rotation_rad` en frontend viewer; backend puede convertir motor→bone usando perfil JSON.

- C) Fuente de datos: real vs simulada
  - Modo simulado (recomendado para inicio):
    - Backend expone `ws /v1/ws/joint-state` o `POST /v1/hand/simulate` que emite secuencias de `JointState` (JSON) a distintas velocidades.
    - Biblioteca de gestos (JSON) en `hand.models.gestures` se puede convertir a `JointState` por perfil.
  - Modo real: `HandService` produce objetivos motor → `JointState` (mediante `hand.models.hand_profiles`); se publica por WebSocket la posición actual/objetivo.

- D) Sincronización front (aplicar al rig)
  - Frontend: crear `HandViewer.vue` que cargue `.glb` y exponga API `applyJointState(js: JointState, opts?)`.
  - Mapear `motor_id -> bone_name` con fichero `config/hand_profile.json`; aplicar ejes y offsets.
  - Implementar smoothing: linear interpolation + easing (lerp/quaternion slerp para rotaciones) entre timestamps.
  - Definir calibración centralizada (profile): `zero_offsets`, `min_deg`, `max_deg` por joint.

2) API propuesta mínima para desarrollo del gemelo virtual

- REST (rápida prueba):
  - `POST /v1/hand/simulate` { "pattern": "pinch", "rate": 20 } → inicia secuencia simulada en backend y devuelve session id.
  - `GET /v1/hand/simulate/{id}/state` → último JointState (polling).

- WebSocket (recomendado para realtime):
  - `ws /v1/ws/joint-state` → envía mensajes `JointState` JSON en tiempo real.

Ejemplo de `JointState` (JSON):
{
  "timestamp": 1700000000.123,
  "joints": {
    "wrist_yaw": 0.0,
    "thumb_mcp": 0.349,    // radians
    "index_mcp": 1.047
  }
}

3) Mapeos y perfiles

- Mantener un archivo `profiles/hand_profile.json` con:
  - joint -> motor_id mapping (si aplica)
  - zero_offset (deg or rad)
  - min_deg / max_deg
  - execution_groups

4) Plan de integración incremental (práctico)

- Paso 1: Frontend – Viewer mock
  - Implementar `HandViewer.vue` que carga GLB y aplica `JointState` desde un Pinia store.
  - Crear util de interpolación y controles (play/pause/speed).

- Paso 2: Simulador backend
  - Implementar `POST /v1/hand/simulate` y `ws /v1/ws/joint-state` que reproduzca gestos de `hand.models.gestures` convertido a `JointState`.

- Paso 3: Conexión real
  - Cuando exista hardware, adaptar `HandService` para publicar `JointState` (posición objetivo y actual) en el mismo WS, sin cambiar el viewer.

5) Notas prácticas y advertencias

- Cero absoluto y límites: almacenar en `hand.models.hand_profiles` y usarlo tanto para controlar motores como para normalizar el viewer.
- Ejes: documentar si `rotation` es en radianes y qué eje local se usa (X/Y/Z) por hueso.
- Si el GLB usa jerarquía diferente al perfil físico, crear mapeo `profile.bone_map`.

6) Recursos de implementación rápida

- Frontend: usar `@tresjs/tres` o `three.glTFLoader` para cargar GLB y `three.Quaternion.slerp` para interpolación.
- Backend: usar la infraestructura FastAPI existente; añadir un pequeño módulo `hand.simulator` que lea `hand.models.gestures` y emita `JointState`.
