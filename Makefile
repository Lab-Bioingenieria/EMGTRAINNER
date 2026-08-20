# Makefile para automatizar la ejecución del proyecto
#
# Toolchain esperado (ver docs/reproducible-environment.md):
#   Python 3.11.9  -> backend/.python-version
#   Node 22.23.2   -> frontend/.node-version
#   pnpm 11.17.0   -> frontend/package.json#packageManager

.PHONY: env-backend install-backend install-frontend install-all \
	run-backend run-frontend run-all run-help build-frontend update \
	infra init-local doctor check-contract test-backend \
	verify hand-inventory install-udev

TEST_ENV := ENVIRONMENT=test TEST_POSTGRES_URL="sqlite+aiosqlite:///./test.db"

# Crear entorno virtual en el backend usando uv, fijado explícitamente a
# la versión de backend/.python-version (uv no siempre resuelve el pin
# implícitamente si ya hay un venv previo de otra versión).
env-backend:
	cd backend && uv venv --python 3.11.9

# Instalación de dependencias para ambos proyectos
install-all: install-backend install-frontend

# requirements-dev.txt incluye requirements.txt (-r requirements.txt), así
# que esto deja instaladas tanto las dependencias de runtime como las de
# test (pytest, httpx, faker) en un solo paso determinista.
install-backend: env-backend
	cd backend && uv pip install -r requirements-dev.txt

# --frozen-lockfile falla si pnpm-lock.yaml no coincide con package.json,
# en vez de resolver versiones nuevas en silencio.
install-frontend:
	cd frontend && pnpm install --frozen-lockfile

# Ejecutar el entorno de desarrollo
# Nota: La forma más sencilla de correr ambos en una sola terminal usando Make
# es con el comando: make -j2 run-all
run-all: run-backend run-frontend

run-help:
	@echo "=========================================================="
	@echo "Para ejecutar ambos proyectos al mismo tiempo, puedes usar:"
	@echo "  make -j2 run-all"
	@echo "=========================================================="
	@echo "Alternativamente, abre dos terminales:"
	@echo "  Terminal 1: make run-backend"
	@echo "  Terminal 2: make run-frontend"
	@echo "=========================================================="

run-backend:
	cd backend && .venv/bin/python main.py

run-frontend:
	cd frontend && pnpm run dev

# Construcción para producción del frontend
build-frontend:
	cd frontend && pnpm run build

# Actualizar el repositorio y reinstalar dependencias
update:
	git pull
	$(MAKE) install-all

# Levantar solo la infraestructura de base de datos y mensajería en Docker.
# Opcional: el flujo local básico con SQLite (make test-backend) no la
# necesita; sólo hace falta para correr el backend contra Postgres/Redis/
# RabbitMQ reales. Soporta tanto el plugin `docker compose` como el
# binario legacy `docker-compose`; falla con un mensaje claro si no
# encuentra ninguno de los dos.
infra:
	@if docker compose version >/dev/null 2>&1; then \
		docker compose up -d db redis rabbitmq; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose up -d db redis rabbitmq; \
	else \
		echo "[FAIL] neither the 'docker compose' plugin nor legacy 'docker-compose' was found" >&2; \
		exit 1; \
	fi

# Inicializar el entorno local: copia backend/.env.example a backend/.env
# sólo si todavía no existe. Nunca pisa un .env existente y no requiere
# Docker.
init-local:
	test -f backend/.env || cp backend/.env.example backend/.env

# Instala la regla udev del U2D2. Sin esto el driver ftdi_sio deja
# latency_timer en 16 ms y cada transacción Dynamixel espera ese timer en
# vez de los ~0.2 ms que tarda el paquete a 1 Mbps. Requiere sudo una sola
# vez; después la regla se aplica sola en cada conexión del adaptador.
install-udev:
	sudo install -m 0644 scripts/99-emgtrainner-u2d2.rules /etc/udev/rules.d/99-emgtrainner-u2d2.rules
	sudo udevadm control --reload-rules
	sudo udevadm trigger --subsystem-match=usb-serial --action=add
	@echo "[OK] regla udev instalada; reconecta el U2D2 si ya estaba enchufado"

# Diagnóstico del entorno: toolchain, configuración y (si está conectado)
# el adaptador U2D2. De sólo lectura: nunca abre el bus ni mueve motores.
# Falla (exit != 0) si uv/Python/Node/pnpm no coinciden con la versión
# fijada; ver scripts/doctor.sh.
doctor:
	@bash scripts/doctor.sh

# Contrato mínimo y verificable del repositorio: un solo lockfile de
# frontend, sin dependencias "latest", versiones de toolchain fijadas,
# hechos de hardware documentados y Makefile sin sintaxis no portable.
check-contract:
	@bash scripts/check-repo-contract.sh

test-backend:
	cd backend && $(TEST_ENV) .venv/bin/pytest -q

# Inventario de solo lectura del bus Dynamixel: un ping por ID, nunca
# habilita torque ni escribe registros. Seguro de correr antes de
# cualquier prueba de movimiento.
hand-inventory:
	cd backend && PYTHONPATH=. .venv/bin/python -m tests.hand.inventory_scan

# Preflight local: toolchain + contrato + tests de backend + build de frontend.
# CI ejecuta las mismas puertas en jobs aislados, con provisión propia.
verify: doctor check-contract test-backend build-frontend
