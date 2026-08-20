# EMGTRAINNER

Plataforma de entrenamiento y monitoreo sEMG: adquiere señales electromiográficas
desde un dispositivo ESP32, las transmite en tiempo real a una interfaz clínica y
controla una mano robótica Omnihand sobre un bus Dynamixel (familia XL330).

## Stack

### Frontend (`frontend/`)
- **Vue 3** + **TypeScript** con `<script setup>`
- **Vite** como build tool y dev server
- **TresJS / three.js** para la visualización 3D de la mano
- **Pinia** (estado) y **Vue Router** (ruteo con guard de autenticación)
- **Tailwind CSS v4**

### Backend (`backend/`)
- **FastAPI** sobre Python 3.11.9
- **SQLAlchemy 2** async + **Alembic**
- **PostgreSQL** en producción, SQLite (`aiosqlite`) en tests
- **Celery** + Redis para trabajos en background
- **JWT** (`python-jose`) para autenticación HTTP y WebSocket
- **dynamixel-sdk** para el bus U2D2/Dynamixel

### Hardware (`codigo_esp32/`)
Firmware del ESP32 que digitaliza los tres canales sEMG y publica el stream.

## Estructura

```
EMGTRAINNER/
├── backend/            # API FastAPI
│   ├── api/            # Routers versionados (/v1)
│   ├── app/            # Modelos, esquemas, controladores y servicios de dominio
│   ├── core/           # Config, seguridad, dependencias, base de datos
│   ├── tests/          # Suite pytest y pruebas de contrato de hardware
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
├── docs/               # Documentación operativa y de hardware
├── scripts/            # Doctor y contrato automatizado del repositorio
└── .github/workflows/  # CI
```

## Requisitos reproducibles

- uv **0.11.32**
- Python **3.11.9** (`backend/.python-version`)
- Node.js **22.23.2** (`frontend/.node-version`)
- pnpm **11.17.0** (`frontend/package.json#packageManager`)

La instalación detallada, los componentes descargables, el flujo para una Jetson
reciclada/offline y la política de cachés están en
[docs/reproducible-environment.md](docs/reproducible-environment.md).

## Instalación desde cero

```bash
make install-all   # backend dev/runtime deps + frontend con lockfile congelado
make init-local    # crea backend/.env solo si no existe
make doctor        # valida versiones; no abre ni mueve hardware
make verify        # doctor + contrato + pytest + typecheck/build frontend
```

O por separado:

```bash
# Backend
cd backend
uv venv --python 3.11.9
uv pip install -r requirements-dev.txt

# Frontend
cd frontend
pnpm install --frozen-lockfile
```

## Ejecución

```bash
make -j2 run-all      # backend en :8000 y frontend en :5173
```

El dev server de Vite proxea `/v1` y `/learning` hacia `http://127.0.0.1:8000`,
incluidos los WebSockets. Por eso el frontend nunca debe apuntar a un host
absoluto: usá `buildAuthenticatedWebSocketUrl()` de `frontend/src/lib/websocket.ts`,
que arma la URL sobre el origen actual y adjunta el JWT.

## Verificación

```bash
make verify           # preflight local de las mismas puertas de calidad
make check-contract   # toolchain, lockfiles, docs y seguridad del hardware
make test-backend     # 110 pruebas en la línea base actual
make build-frontend   # vue-tsc + build de producción
```

`TEST_POSTGRES_URL` es obligatoria al invocar pytest directamente:
`tests/conftest.py` la usa para levantar y destruir el esquema en cada test.
Las dependencias de test viven en `requirements-dev.txt`.

## Hardware Dynamixel

El contrato de software usa U2D2, Dynamixel Protocol 2.0, 1.000.000 bps e IDs
1–15. El inventario sobre la mano ensamblada devolvió `model_number=1200` en los
once motores, es decir **XL330-M288-T**, leído del propio firmware.

Antes de cualquier movimiento, verificá alimentación, cableado TTL, tierra común
y conectores; después ejecutá el inventario read-only:

```bash
make hand-inventory
```

El comando nunca habilita torque ni escribe registros.

### Tabla de movimientos

Mapeo verificado moviendo **un motor a la vez** sobre la mano ensamblada. La
cadena daisy está cableada del meñique hacia adentro, al revés del orden
anatómico: el perfil original asumía `4,5=index` y estaba equivocado.

| ID | Dedo | Articulación | Recorrido medido | Estado |
| ---: | --- | --- | ---: | --- |
| 1 | thumb | `MCP_FE` | 34.5° | OK |
| 2 | thumb | `CMC_AA` | 32.1° | OK |
| 3 | thumb | `CMC_FE` | **1.7°** | **trabado** |
| 4 | pinky | `PIP` | 69.3° | OK |
| 5 | pinky | `MCP` | 69.0° | OK |
| 6 | ring | `PIP` | 68.9° | OK |
| 7 | ring | `MCP` | 68.7° | OK |
| 8 | middle | `PIP` | 69.7° | OK |
| 9 | middle | `MCP` | sin medir | pendiente |
| 10 | index | `PIP` | 68.6° | OK |
| 11 | index | `MCP` | sin medir | pendiente |

El *recorrido medido* es la excursión real de punta a punta, no el rango
declarado en el perfil. Para reproducir la tabla, el bus tiene que estar
**exclusivo**: con el backend corriendo y el puerto tomado, un escaneo devolvió
solo 5 de 11 motores.

```bash
cd backend
PYTHONPATH=. .venv/bin/python -m tests.hand.identify_motors 4
```

El motor 3 (trapecio del pulgar) tiene 1.7° de recorrido útil y descansa en
-14.7°, fuera del rango 0–45° que declara el perfil. Los detalles, el riesgo
térmico de bloquearlo y qué está confirmado visualmente frente a qué está
inferido, en [docs/motion-table.md](docs/motion-table.md).

La guía completa de hardware, permisos seriales, modelos oficiales y límites de
seguridad está en [docs/hardware-inventory.md](docs/hardware-inventory.md).

## CI

`.github/workflows/ci.yml` corre en cada push a `main` y pull request:

- **repo-contract**: valida toolchain, lockfiles y documentación crítica;
- **backend**: Python 3.11.9, `requirements-dev.txt` y `pytest`;
- **frontend**: Node 22.23.2, pnpm 11.17.0, instalación congelada y `pnpm build`.

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
| `DYNAMIXEL_PORT` | Puerto U2D2 opcional | autodetectado |

Fuera de `development` y `test`, el arranque **falla** si `SECRET_KEY` sigue
siendo el valor por defecto. Configurá `CORS_ALLOWED_ORIGINS` con el dominio real.

### Frontend

No requiere variables de entorno. API y WebSockets se resuelven contra el mismo
origen, por lo que el despliegue depende del reverse proxy.

## Seguridad y datos

- Todas las rutas del frontend salvo el login exigen una sesión válida.
- WebSockets de sensores y mano robótica requieren JWT.
- Los endpoints respaldados por órdenes verifican propiedad del recurso.
- Las descargas de storage pasan por `fetch` autenticado.
- Los datos de pacientes en `backend/storage/` no se versionan. Ver
  [docs/data-governance.md](docs/data-governance.md).

## Documentación

- [Entornos reproducibles y reciclables](docs/reproducible-environment.md)
- [Inventario y seguridad del hardware](docs/hardware-inventory.md)
- [Tabla de movimientos de la mano](docs/motion-table.md)
- [Gobernanza de datos](docs/data-governance.md)

## Licencia

Proyecto privado con fines académicos.

## Autores

- Kevin Fernández
- Nager Naranja
