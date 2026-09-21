#!/usr/bin/env bash
# Instalador de EMGTRAINNER como programa (v1.0.0-beta.1).
#
# Uso:
#   ./install.sh            Instala dependencias, compila el frontend y
#                           registra el comando `emgtrainner`.
#   ./install.sh --udev     Además instala la regla udev del U2D2 (pide sudo).
#
# Requisitos: git, uv, Node 22 y pnpm (ver docs/reproducible-environment.md).
set -euo pipefail

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${EMGTRAINNER_BIN_DIR:-$HOME/.local/bin}"
LAUNCHER="$BIN_DIR/emgtrainner"

info() { echo "[install] $*"; }
fail() { echo "[install] ERROR: $*" >&2; exit 1; }

# --- 1. Verificación de toolchain -----------------------------------------
for cmd in git uv node pnpm make; do
    command -v "$cmd" >/dev/null 2>&1 || fail "no se encontró '$cmd' en el PATH"
done

node_major="$(node --version | sed 's/^v\([0-9]*\).*/\1/')"
[ "$node_major" = "22" ] || fail "se requiere Node 22 (encontrado: $(node --version))"

info "toolchain OK: $(uv --version), node $(node --version), pnpm $(pnpm --version)"

# --- 2. Config local + dependencias + build --------------------------------
cd "$INSTALL_DIR"
make init-local
make install-backend
make install-frontend
make build-frontend

# --- 3. Registro del comando `emgtrainner` ---------------------------------
mkdir -p "$BIN_DIR"
sed "s|__INSTALL_DIR__|$INSTALL_DIR|" \
    scripts/emgtrainner-launcher.sh > "$LAUNCHER"
chmod +x "$LAUNCHER"
info "comando instalado en $LAUNCHER"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) info "AVISO: $BIN_DIR no está en tu PATH. Agrega esta línea a tu ~/.bashrc o ~/.zshrc:"
       info "  export PATH=\"$BIN_DIR:\$PATH\""
       ;;
esac

# --- 4. Regla udev (opcional) ----------------------------------------------
if [ "${1:-}" = "--udev" ]; then
    make install-udev
fi

echo ""
echo "=========================================================="
echo " Instalación completa. Inicia el programa con:"
echo "   emgtrainner"
echo "=========================================================="
