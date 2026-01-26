# Arquitectura del Repositorio (Resumen)

Este repositorio contiene la pila completa para el proyecto EMGarm: frontend en Vue (Vite + Pinia), backend en Python (FastAPI) y código embebido para ESP32 / Dynamixel.

- `frontend/`
  - `src/main.ts` — entrada de la app Vue; monta `Pinia` y el `router`.
  - `src/router/index.ts` — rutas de UI (`/dashboard`, `/patient`, `/patient/free`, `/ai-console`, `/storage`, ...).
  - `src/views/` — vistas principales (ej. `PatientSessionView.vue`, `PatientFreeView.vue`, `DashboardView.vue`).
  - `src/components/` — componentes UI reutilizables; `components/patient/PatientHandVisualization.vue` es el visualizador actual (imágenes), `GestureProgress.vue`, `RadialTimer.vue`.
  - `src/services/` — clientes HTTP hacia el backend: `emg.service.ts`, `patient.service.ts`, `health.service.ts`.
  - `src/stores/` — Pinia stores (pacientes, sesión, tests); archivos existen aunque están parcialmente vacíos.

- `backend/`
  - `core/server.py` — crea la app FastAPI (`app`) y agrega middlewares y routers.
  - `api/v1/` — routers por dominio: `monitoring`, `microcontrollers`, `storage`, `training_sessions`, `users`, `tasks`, etc.
  - `app/` — controladores, modelos, repositorios, servicios y routers adicionales (ej. `app.routers.orders`, `app.routers.devices`).
  - `hand/` — lógica de control de la mano: `hand.services.HandService`, `hand.control.hand_controller`, `hand.models.gestures`, `hand.core.dynamixel_interface`.
  - `storage` / `worker/` — manejo de archivos (CSV) y tareas background (si procede).

- Integración hardware:
  - EMG (ESP32) se maneja desde `app.services.emg_service` y expone endpoints WebSocket/REST en `api/v1/monitoring/sensor.py`.
  - Dynamixel / mano robótica se controla desde `hand.services.HandService` y los controladores (mapeos de gesto → posición de motores).

Puntos de entrada:
- Frontend: `frontend/src/main.ts` → `router` → vistas (`PatientSessionView.vue`, `PatientFreeView.vue`).
- Backend: `backend/core/server.py` crea `app` y monta `api.v1` routers.

Este documento es un resumen; ver los guías específicos para frontend/backend y el flujo de entrenamiento de gestos.
