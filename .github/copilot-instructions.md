# Copilot Instructions for practicas-comunitarias-PAOII

## Project Overview
This repository is a full-stack system for managing community practices, with:
- **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS (in `frontend/`)
- **Backend**: Python (FastAPI-style structure) in `backend/`
- **Embedded**: ESP32 real-time gesture recognition code in `codigo_esp32/`
- **3D Models**: Hand/arm components in `Componentes_modelo3D/`

## Key Architectural Patterns
- **Backend** is modular: `app/` (business logic, routers, models, services), `core/` (config, server, utilities), `hand/` (hand-specific logic), `storage/`, and `worker/` (background tasks).
- **Frontend** uses Vite for fast builds and React for UI. Source code is in `frontend/src/`.
- **ESP32** code is standalone, focused on real-time EMG gesture recognition and BLE communication.

## Developer Workflows
- **Install prerequisites**: Node.js ≥ 20.19.5, pyenv, uv, pnpm
- **Frontend**: Use `pnpm` for dependency management and scripts (see `frontend/package.json`).
- **Backend**: Use `uv` for Python dependencies (`requirements.txt`). Python version managed by `pyenv` (see `.python-version`).
- **Docker**: Use `docker-compose.yml` for full-stack orchestration.
- **Testing**: Backend tests in `backend/tests/` (pytest structure). Frontend tests (if any) in `frontend/`.

## Project-Specific Conventions
- **Backend**: Follows FastAPI-like modularity, but may have custom folder names (e.g., `hand/`, `core/`).
- **Frontend**: Modern React with TypeScript and Tailwind. Use Vite conventions for config/build.
- **Embedded**: Arduino/ESP32 code expects specific hardware and libraries (see `codigo_esp32/EMG_uMyo_RealTime/README.md`).
- **3D Models**: Organized by type (Articulado, Ensamble, Piezas, Planos).

## Integration Points
- **API**: Frontend communicates with backend via REST endpoints (see `backend/app/routers/`).
- **ESP32**: Communicates with backend via BLE/WiFi for gesture data.
- **Docker**: Use for local development and deployment.

## Examples
- To run backend locally: `uv pip install -r requirements.txt` then `python main.py` in `backend/`
- To run frontend: `pnpm install` then `pnpm dev` in `frontend/`
- To build full stack: `docker-compose up --build`

## References
- See `README.md` in project root and in subfolders for more details.
- For hardware/embedded, see `codigo_esp32/EMG_uMyo_RealTime/README.md`.
# Copilot Instructions (Proyecto EMGarm)

## Stack
- Frontend: Vue 3 + Vite + TypeScript + TresJS/Three.js
- Backend: Python 3.11 + FastAPI + Uvicorn + Docker Compose

## Objetivo actual
Implementar gemelo virtual (rig GLB) sincronizable por estados articulares (JointState) para probar gestos sin hardware.

## Reglas
- No rompas compatibilidad existente.
- Cambios grandes: proponer plan y luego implementar por PR lógico (multi-archivo).
- Siempre incluir:
  - dónde se integra en frontend (componente + ruta)
  - contrato de datos (tipo JointState)
  - modo simulado (mock) si no hay hardware
- Evitar hardcode de puertos/paths; usar env y detección robusta.

---
For AI agents: Follow these conventions and reference the above directories for examples of project-specific patterns. When in doubt, prefer existing structure and scripts over inventing new ones.