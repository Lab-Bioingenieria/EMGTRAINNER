# EMGTRAINNER

Plataforma de entrenamiento y monitoreo sEMG: adquiere señales electromiográficas
desde un dispositivo ESP32, las transmite en tiempo real a una interfaz clínica y
controla una mano robótica Omnihand.

## Stack

### Frontend (`frontend/`)
- **Vue 3** + **TypeScript** con `<script setup>`
- **Vite** como build tool y dev server
- **TresJS / three.js** para la visualización 3D de la mano
- **Pinia** (estado) y **Vue Router** (ruteo con guard de autenticación)
- **Tailwind CSS v4**

### Backend (`backend/`)
- **FastAPI** sobre Python 3.11
- **SQLAlchemy 2** async + **Alembic**
- **PostgreSQL** en producción, SQLite (`aiosqlite`) en tests
- **Celery** + Redis para trabajos en background
- **JWT** (`python-jose`) para autenticación HTTP y WebSocket

### Hardware (`codigo_esp32/`)
Firmware del ESP32 que digitaliza los tres canales sEMG y publica el stream.

## Estructura

```
EMGTRAINNER/
├── backend/            # API FastAPI
│   ├── api/            # Routers versionados (/v1)
│   ├── app/            # Modelos, esquemas, controladores y servicios de dominio
│   ├── core/           # Config, seguridad, dependencias, base de datos
│   ├── tests/          # Suite pytest
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/           # Aplicación Vue 3
│   └── src/
│       ├── components/ # Componentes por rol (doctor, patient, common)
│       ├── lib/        # Cliente HTTP y helper de WebSocket autenticado
│       ├── router/     # Rutas y guard de autenticación
│       ├── services/   # Clientes de API por dominio
│       └── views/      # Vistas por rol
├── codigo_esp32/       # Firmware del sensor
├── docs/               # Documentación operativa
└── .github/workflows/  # CI
```

## Requisitos

- Python 3.11 (ver `backend/.python-version`)
- Node.js 20+ y pnpm
- Opcional: [uv](https://github.com/astral-sh/uv) para gestionar el entorno de Python

## Instalación

```bash
make install-all      # backend (uv venv + requirements) y frontend (pnpm install)
```

O por separado:

```bash
# Backend
cd backend
uv venv && uv pip install -r requirements.txt
# Creá backend/.env con las variables de la tabla de Configuración.
# Los defaults alcanzan para desarrollo local.

# Frontend
cd frontend
pnpm install
```

## Ejecución

```bash
make -j2 run-all      # backend en :8000 y frontend en :5173
```

El dev server de Vite proxea `/v1` y `/learning` hacia `http://127.0.0.1:8000`,
incluidos los WebSockets. Por eso el frontend nunca debe apuntar a un host
absoluto: usá `buildAuthenticatedWebSocketUrl()` de `frontend/src/lib/websocket.ts`,
que arma la URL sobre el origen actual y adjunta el JWT.

## Tests

```bash
cd backend
ENVIRONMENT=test TEST_POSTGRES_URL="sqlite+aiosqlite:///./test.db" pytest -q
```

`TEST_POSTGRES_URL` es obligatoria: `tests/conftest.py` la usa para levantar y
destruir el esquema en cada test. Las dependencias de test viven en
`requirements-dev.txt`, separadas de las de runtime.

Frontend:

```bash
cd frontend
pnpm build     # incluye type-check con vue-tsc
```

## CI

`.github/workflows/ci.yml` corre en cada push a `main` y en cada pull request:

- **backend**: instala `requirements-dev.txt` en Python 3.11 y ejecuta `pytest`
- **frontend**: instala con `pnpm --frozen-lockfile` y ejecuta `pnpm build`

## Configuración

### Backend (`backend/.env`)

| Variable | Descripción | Default |
| --- | --- | --- |
| `ENVIRONMENT` | `development`, `test` o `production` | `development` |
| `SECRET_KEY` | Clave de firma JWT | `super-secret-key` |
| `POSTGRES_URL` | DSN async de la base | SQLite local |
| `REDIS_URL` | Conexión a Redis | `redis://localhost:6379/7` |
| `JWT_ALGORITHM` | Algoritmo de firma | `HS256` |
| `JWT_EXPIRE_MINUTES` | Vigencia del token | `1440` |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos | `localhost:3000`, `localhost:5173` |
| `CELERY_BROKER_URL` / `CELERY_BACKEND_URL` | Cola de tareas | RabbitMQ / Redis |

Fuera de `development` y `test`, el arranque **falla** si `SECRET_KEY` sigue
siendo el valor por defecto. Es intencional: evita desplegar con una clave
pública. Configurá `CORS_ALLOWED_ORIGINS` con el dominio real al desplegar.

### Frontend

No requiere variables de entorno. La API y los WebSockets se resuelven contra el
mismo origen, por lo que el despliegue depende del reverse proxy y no de una URL
compilada en el bundle.

## Seguridad y datos

- Todas las rutas del frontend salvo el login exigen una sesión válida; un token
  expirado o malformado dispara logout automático.
- Los WebSockets de sensores y de la mano robótica requieren JWT.
- Los endpoints respaldados por órdenes verifican propiedad del recurso.
- Las descargas de storage pasan por `fetch` autenticado, no por enlaces directos.
- Los datos de pacientes en `backend/storage/` están fuera del control de
  versiones. Ver [docs/data-governance.md](docs/data-governance.md).

## Licencia

Proyecto privado con fines académicos.

## Autores

- Kevin Fernández
- Nager Naranja
