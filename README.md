# Prácticas Comunitarias - PAO II

Sistema de gestión para prácticas comunitarias desarrollado con un stack moderno full-stack.

## 🚀 Stack Tecnológico

### Frontend
- ⚡ **Vite** - Build tool ultrarrápido
- ⚛️ **React 19** - Librería UI
- 📘 **TypeScript** - Tipado estático
- 🎨 **Tailwind CSS v3** - Framework CSS utility-first

### Backend
- 🐍 **Python** - Lenguaje de programación
- 📦 **uv** - Gestor de paquetes ultrarrápido para Python
- 🔧 **pyenv** - Gestor de versiones de Python

## 📁 Estructura del Proyecto

```
practicas-comunitarias-PAOII/
├── frontend/          # Aplicación React + Vite
│   ├── src/          # Código fuente
│   ├── public/       # Archivos estáticos
│   └── ...
├── backend/          # API Python
│   ├── .env.example  # Variables de entorno de ejemplo
│   ├── .python-version  # Versión de Python para pyenv
│   ├── requirements.txt
│   └── ...
└── README.md
```

## 🛠️ Instalación

### Prerequisitos
- Node.js v20.19.5 o superior
- [pyenv](https://github.com/pyenv/pyenv) - Gestor de versiones Python
- [uv](https://github.com/astral-sh/uv) - Gestor de paquetes Python
- pnpm

### Frontend

```bash
cd frontend
pnpm install
pnpm run dev
```

El frontend estará disponible en `http://localhost:5173`

### Backend

```bash
cd backend

# pyenv instalará automáticamente la versión correcta según .python-version
pyenv install

# Crear entorno virtual con uv
uv venv

# Activar entorno virtual
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias con uv
uv pip install -r requirements.txt

# Copiar y configurar variables de entorno
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
# Editar .env con tus configuraciones
```

## 📜 Scripts Disponibles

### Frontend

- `pnpm run dev` - Inicia servidor de desarrollo
- `pnpm run build` - Construye para producción
- `pnpm run preview` - Preview de la build de producción
- `pnpm run lint` - Ejecuta ESLint

### Backend

```bash
# Instalar una nueva dependencia
uv pip install nombre-paquete

# Actualizar requirements.txt
uv pip freeze > requirements.txt

# Sincronizar dependencias
uv pip sync requirements.txt
```

## 🔧 Configuración

### Variables de Entorno

#### Frontend
Crea un archivo `.env.local` en `/frontend`:
```env
VITE_API_URL=http://localhost:8000
```

#### Backend
Copia `.env.example` a `.env` en `/backend` y configura:
```env
# Agregar variables según necesites
DATABASE_URL=
SECRET_KEY=
```

## 🚀 Despliegue

### Frontend
```bash
cd frontend
npm run build
# Los archivos optimizados estarán en /frontend/dist
```

### Backend
```bash
cd backend
# Configurar según tu plataforma de despliegue
```

## 👥 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y está desarrollado con fines académicos.

## 👨‍💻 Autor

- **Tu Nombre** - [Tu GitHub]

---

⭐ Si este proyecto te fue útil, considera darle una estrella
