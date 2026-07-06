# Makefile para automatizar la ejecución del proyecto

.PHONY: env-backend install-backend install-frontend install-all run-backend run-frontend run-all run-help build-frontend update
# Crear entorno virtual en el backend usando uv
env-backend:
	cd backend && uv venv

# Instalación de dependencias para ambos proyectos
install-all: install-backend install-frontend

install-backend: env-backend
	cd backend && uv pip install -r requirements.txt

install-frontend:
	cd frontend && pnpm install

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
	cd backend && uv run python main.py

run-frontend:
	cd frontend && pnpm run dev

# Construcción para producción del frontend
build-frontend:
	cd frontend && pnpm run build

# Actualizar el repositorio y reinstalar dependencias
update:
	git pull
	$(MAKE) install-all

# Levantar solo la infraestructura de base de datos y mensajería en Docker (para usar backend en Windows nativo)
infra:
	docker-compose up -d db redis rabbitmq

# Inicializar el entorno local copiando el .env y levantando la infra
init-local:
	if not exist "backend\.env" copy "backend\.env.example" "backend\.env"
	$(MAKE) infra
