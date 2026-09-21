#!/usr/bin/env bash
# Launcher del programa EMGTRAINNER (generado por install.sh).
# Arranca el backend (uvicorn en 127.0.0.1:8000) y sirve el frontend
# ya compilado (vite preview en 0.0.0.0:5173) con proxy de API.
set -uo pipefail

INSTALL_DIR="__INSTALL_DIR__"
BACKEND_PORT=8000
FRONTEND_PORT=5173

backend_pid=""
frontend_pid=""

shutdown() {
    echo ""
    echo "[emgtrainner] deteniendo servicios..."
    [ -n "$backend_pid" ]  && kill "$backend_pid"  2>/dev/null
    [ -n "$frontend_pid" ] && kill "$frontend_pid" 2>/dev/null
    wait 2>/dev/null
    exit 0
}
trap shutdown INT TERM

cd "$INSTALL_DIR/backend"
.venv/bin/python main.py &
backend_pid=$!

cd "$INSTALL_DIR/frontend"
pnpm run preview --host 0.0.0.0 --port "$FRONTEND_PORT" &
frontend_pid=$!

echo "=========================================================="
echo " EMGTRAINNER corriendo"
echo "   Web:      http://localhost:$FRONTEND_PORT"
echo "   API:      http://127.0.0.1:$BACKEND_PORT"
echo "   Ctrl+C para detener"
echo "=========================================================="

wait -n "$backend_pid" "$frontend_pid"
exit_code=$?
echo "[emgtrainner] un proceso terminó (exit $exit_code); cerrando el resto"
[ -n "$backend_pid" ]  && kill "$backend_pid"  2>/dev/null
[ -n "$frontend_pid" ] && kill "$frontend_pid" 2>/dev/null
exit "$exit_code"
