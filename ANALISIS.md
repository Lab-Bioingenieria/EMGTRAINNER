# ANÁLISIS DE ARQUITECTURA — EMGTRAINNER v1.0.0-beta.1

Sistema de rehabilitación neuromuscular que combina sensores EMG (uMyo + ESP32),
una mano robótica Dynamixel controlada por U2D2, y una aplicación web para
sesiones de entrenamiento supervisadas y autónomas.

---

## 1. Vista general

```
┌─────────────┐   HTTP/WS    ┌──────────────────┐   serie (115200)   ┌────────────┐
│  Frontend   │ ◄──────────► │  Backend FastAPI │ ◄────────────────► │ ESP32 +    │
│  Vue 3 + TS │  /v1,/learning│  (puerto 8000)   │                    │ sensores   │
│  (vite)     │              │                  │   TTL serie (1Mbps)│ uMyo EMG   │
└─────────────┘              │                  │ ◄────────────────► ┌────────────┐
                             │                  │                    │ U2D2 +     │
                             │                  │                    │ mano       │
                             │                  │                    │ Dynamixel  │
                             └────────┬─────────┘                    └────────────┘
                                      │ SQLAlchemy async
                               ┌──────┴──────┐        ┌────────────┐
                               │ SQLite/     │        │ CSV en     │
                               │ PostgreSQL  │        │ backend/   │
                               └─────────────┘        │ storage/   │
                                                      └────────────┘
```

En modo "programa instalado" (`./install.sh`), el comando `emgtrainner` levanta
el backend (uvicorn, 127.0.0.1:8000) y sirve el build del frontend con
`vite preview` (0.0.0.0:5173), que proxifica `/v1` y `/learning` hacia la API,
sin necesidad de nginx.

---

## 2. Backend

**Stack:** Python 3.11.9 · FastAPI 0.109 + Uvicorn · SQLAlchemy 2.0 async ·
Pydantic 2 / pydantic-settings · JWT (python-jose, HS256) · dynamixel-sdk.

### 2.1 Arranque y configuración
- `backend/main.py` lanza uvicorn apuntando a `core/server:app` (con reload
  fuera de producción).
- `backend/core/server.py` construye la app: routers, middlewares, manejador
  global de excepciones y un **lifespan** que crea el esquema con
  `Base.metadata.create_all`.
- `backend/core/config.py`: `Config(BaseSettings)` lee `.env` — `POSTGRES_URL`
  (por defecto SQLite aiosqlite), `SECRET_KEY`, JWT, CORS, URLs de Celery.
  Rechaza el SECRET_KEY por defecto fuera de dev/test.

### 2.2 Capas

```
api/v1/ (routers legacy)  ──►  controllers/  ──►  core/use_cases/  ──►  services/  ──►  repositories/
app/routers/ (nuevos)     ──────────────────────►  app/services/ (singletons)  ──►  repositories/
        │
        └──► app/models/ (SQLAlchemy)  +  app/schemas/ (DTOs Pydantic)
```

- **Routers** (`backend/api/v1/…`, `backend/app/routers/`): solo orquestan HTTP.
  Hay **dos estilos conviviendo**: los routers legacy van por controllers + casos
  de uso (`core/use_cases/`); los nuevos (`hand`, `learning`, `safety`,
  `websocket`) llaman directo a servicios singleton.
- **Servicios** (`backend/app/services/`): lógica de negocio con estado —
  `emg_service`, `csv_service`, `llc_service`, `websocket_manager`,
  `HandService.get_instance()`.
- **Repositorios** (`backend/app/repositories/`, `core/repository/`): acceso a
  datos, con writer/reader separados y decorador `@transactional`
  (`core/database/transactional.py`); `SQLAlchemyMiddleware` inyecta la sesión
  por request.
- **Modelos** (`backend/app/models/`): `User`, `Patient`, `Task`, `Device`,
  `Order`, `DataFile`.

### 2.3 Módulos funcionales (routers)

| Prefijo | Dominio |
|---|---|
| `/v1/users` | CRUD + login de usuarios |
| `/v1/patients` | Gestión de pacientes (datos reales desde #46) |
| `/v1/monitoring/health` | Health check de la API |
| `/v1/monitoring/sensor` | Estado del sensor EMG + `WS /ws/emg-stream` |
| `/v1/microcontrollers/…` | Health/config del ESP32 y puertos USB |
| `/v1/tasks`, `/v1/storage` | Tareas; listado/descarga de sesiones CSV |
| `/hand` | Estado, inicialización, gestos y sesiones de la mano Dynamixel |
| `/hand/safety` | E-stop (status/engage/reset), autenticado |
| `/learning` | Curriculum LLC: siguiente gesto por Índice de Separabilidad |
| `/ws/emg` | Broadcast WebSocket de EMG (autenticado por token en query) |

### 2.4 Hardware
- **Mano Dynamixel**: `app/core/dynamixel_interface.py` (Protocol 2.0, 1 MBaud,
  XL330). Descubrimiento de puerto por **VID FTDI 0x0403**, validación del
  puerto configurado (#47) y **reconexión perezosa al re-enchufar el U2D2**
  (#48 — `EMGDataService` reintenta `connect_hand()` y suelta el handle tras
  fallos de transporte).
- **Latencia serie**: regla udev `scripts/99-emgtrainner-u2d2.rules` fija
  `latency_timer=1` (mejora medida de ~15.6 ms a ~2.1 ms por lectura en Jetson).
- **EMG**: `core/serial/manager.py` (115200) + `app/utils/umyo/umyo_parser.py`
  parsean tramas binarias; `emg_service` publica a WebSocket desde un hilo.
- **Tiempo real de la mano**: `hand_realtime_manager.py` con backends
  serie/UDP/mock, planner, feedback de motores, librería de gestos y
  `hand_safety_manager` + `core/safety/estop.py` (todo movimiento verifica el
  e-stop).

### 2.5 Base de datos
- SQLAlchemy 2.0 async; **SQLite por defecto**, Postgres vía `POSTGRES_URL`.
- **Sin Alembic**: esquema solo por `create_all` (tech debt: sin migraciones
  reales de datos).
- Los CSV de sesiones viven en `backend/storage/` (filesystem), fuera de
  transacción con la BD.

### 2.6 Autenticación
- JWT HS256, expiración 24 h (`core/security/jwt.py`); bcrypt para passwords.
- `AuthBackend` resuelve el usuario del Bearer en cada request.
- **Sin roles ni refresh tokens** (`CurrentUser` solo lleva `id`).

### 2.7 Infra opcional y tests
- `docker-compose.yml`: Postgres 15, Redis 7, RabbitMQ 3, backend.
- **Celery y `worker/` declarados pero sin tareas**; caché Redis cableada y
  poco usada; `app/integrations/` vacío.
- Tests en `backend/tests/` (api, core, hand con bus simulado, services):
  `cd backend && .venv/bin/pytest -q`.

### 2.8 Tech debt backend
Dos arquitecturas paralelas (legacy vs. routers nuevos), sin migraciones,
Celery scaffold vacío, `emg_service` mezcla parsing/threading/negocio en un
archivo grande, el "learning" es estadística de separabilidad sobre CSV, no ML
real.

---

## 3. Frontend

**Stack:** Vue 3 (Composition API + `<script setup lang="ts">`) · TypeScript ·
Vite 7 · Pinia 3 · vue-router 4 (hash history) · axios · three + @tresjs ·
lucide-vue-next · pnpm 11 / Node 22.

### 3.1 Estructura de `frontend/src/`

| Carpeta | Rol |
|---|---|
| `views/` | 12 vistas, una carpeta por módulo |
| `components/` | Por dominio: `ai/`, `charts/`, `doctor/`, `emg/`, `patient/`, `session/`, `common/` (EmgSerialPlotter, sidebar, header) |
| `stores/` | Solo `session.ts` tiene contenido (los demás están **vacíos**) |
| `services/` | Clases estáticas por dominio (auth, emg, health, patient) |
| `lib/` | `api.ts` (axios), `websocket.ts`, `auth-redirect.ts`, `constants.ts`, `download.ts` |
| `router/` | Rutas + guard inline (`guards.ts` vacío) |
| `types/` | Interfaces sueltas (solapadas con `services/`) |

### 3.2 Rutas principales

| Ruta | Vista | Estado |
|---|---|---|
| `/login` | `LoginView.vue` | Login + registro reales |
| `/` | `HomeView.vue` | Hub de módulos + configuración USB |
| `/doctor` | `DoctorSessionView.vue` | Sesión supervisada real (grabación + gráfica EMG por WS) |
| `/patient` | `PatientSessionView.vue` | Wizard supervisado (TTS, sugerencias `/learning`) |
| `/patient/free` | `PatientFreeView.vue` | Sesión autónoma con tutorial en vídeo |
| `/patients` | `PatientsPanelView.vue` | CRUD real de pacientes |
| `/patients/:id` | `PatientsDetailsView.vue` | **100% mock** |
| `/dashboard` | `DashboardView.vue` | Panel (usa fetch crudo, duplica PatientsPanel) |
| `/storage` | `StorageView.vue` | Descarga de CSV reales |
| `/test` | `TestView.vue` | Pruebas de hardware + plotter EMG |
| `/ai-console` | `AiConsoleView.vue` | **100% maqueta** |

### 3.3 Estado y comunicación
- **Pinia**: único store operativo es `stores/session.ts` (sesión doctor:
  código de 4 dígitos, modo TLC/LLC, fases, cronómetro). El resto usa `ref`
  locales dentro de vistas.
- **HTTP**: axios (`lib/api.ts`, `baseURL=/v1`) con interceptor que inyecta el
  JWT y, en 401, borra el token y redirige a login preservando la ruta.
  **Inconsistencia**: `authService`, `DashboardView` y `PatientSessionView`
  usan `fetch` con un wrapper `authFetch` duplicado.
- **WebSockets**: `buildAuthenticatedWebSocketUrl()` pasa el JWT como query
  param; stream EMG consumido por `EmgSerialPlotter.vue` (canvas 3 canales).
- **Proxy Vite**: `/v1` y `/learning` → `127.0.0.1:8000`, en `server` (dev) y
  `preview` (producción vía launcher).

### 3.4 Autenticación en el cliente
- JWT en `localStorage`; decodificación del payload con tolerancia de reloj de
  5 s (fail-closed: token inválido → borrado).
- Guard global en `router/index.ts:70`: todas las rutas excepto `/login`
  requieren sesión; redirige a `/login?redirect=<ruta>`.

### 3.5 Estilos y 3D
- CSS global artesanal con design tokens (`--bone-*`, `--signal`, …) en oklch;
  IBM Plex Sans/Mono. Tailwind 4 está en devDependencies pero **sin usar**
  (residual).
- Uso 3D mínimo: `TheExperience.vue` (demo de cubo) y un GLB del ESP32 en
  TestView. La "mano" de las vistas es **sprite-based** (2 PNG por gesto en
  `public/movements/`, alternados cada 800 ms); vídeos en `public/movements_video/`.

### 3.6 Tech debt frontend
- **AI Console completo sin backend** (`AiConsoleView`, `ModelVersions`,
  `components/ai/*`).
- Ficheros vacíos (`stores/patient|session|test`, `services/session.service`,
  `router/guards`), layouts muertos (`layouts/*.vue` no importados).
- Vistas gigantes sin composables (`PatientFreeView` 1040 líneas, `LoginView`
  871), duplicación de componentes y de listado de pacientes.
- **Sin tests**; ESLint 9 con config duplicada (`.eslintrc.json` + flat config).

---

## 4. Resumen de riesgos priorizados

1. **Módulo AI inexistente** (frontend maqueta, backend solo estadística LLC).
2. **Sin migraciones de BD** y Celery/worker vacío (infra declarada sin uso).
3. Duplicación de estilos arquitectónicos (backend legacy vs. nuevo; axios vs.
   fetch en frontend) que encarece el onboarding.
4. Datos mock en vistas de detalle que pueden confundir en demo clínica
   (`PatientsDetailsView`, parte de `TestView`).
5. Seguridad básica: JWT sin roles/refresh; E-stop correctamente autenticado.
