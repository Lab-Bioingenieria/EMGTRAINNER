#!/usr/bin/env bash
# Read-only environment diagnostics; never opens the Dynamixel bus.
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
fail=0

REQUIRED_UV="0.11.32"
REQUIRED_PYTHON="3.11.9"
REQUIRED_NODE="v22.23.2"
REQUIRED_PNPM="11.17.0"

check_command_version() {
  local command_name="$1" expected="$2" version_command="$3"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    printf '[FAIL] %s not found\n' "$command_name"
    fail=1
    return
  fi

  local actual
  actual="$(sh -c "$version_command")"
  if [ "$actual" = "$expected" ]; then
    printf '[OK]   %s -> %s\n' "$command_name" "$actual"
  else
    printf '[FAIL] %s -> %s (expected %s)\n' "$command_name" "$actual" "$expected"
    fail=1
  fi
}

printf '=== EMGTRAINNER environment doctor ===\n'
check_command_version uv "$REQUIRED_UV" "uv --version | awk '{print \$2}'"
check_command_version node "$REQUIRED_NODE" "node --version"
check_command_version pnpm "$REQUIRED_PNPM" "pnpm --version"

if command -v uv >/dev/null 2>&1 \
    && python_path="$(cd backend && uv python find "$REQUIRED_PYTHON" 2>/dev/null)"; then
  printf '[OK]   python %s -> %s\n' "$REQUIRED_PYTHON" "$python_path"
else
  printf '[FAIL] Python %s unavailable (run: uv python install %s)\n' "$REQUIRED_PYTHON" "$REQUIRED_PYTHON"
  fail=1
fi

[ -f backend/.env ] \
  && printf '[OK]   backend/.env present\n' \
  || printf '[WARN] backend/.env missing (run: make init-local)\n'

if [ -x backend/.venv/bin/python ]; then
  venv_version="$(backend/.venv/bin/python --version 2>&1 | awk '{print $2}')"
  if [ "$venv_version" = "$REQUIRED_PYTHON" ]; then
    printf '[OK]   backend/.venv uses Python %s\n' "$venv_version"
  else
    printf '[FAIL] backend/.venv uses Python %s (expected %s; recreate it)\n' "$venv_version" "$REQUIRED_PYTHON"
    fail=1
  fi
else
  printf '[WARN] backend/.venv missing (run: make install-backend)\n'
fi

[ -d frontend/node_modules ] \
  && printf '[OK]   frontend/node_modules present\n' \
  || printf '[WARN] frontend/node_modules missing (run: make install-frontend)\n'

ls /dev/serial/by-id/*FTDI* >/dev/null 2>&1 \
  && printf '[OK]   FTDI (U2D2) serial device detected\n' \
  || printf '[INFO] no FTDI serial device detected\n'
groups 2>/dev/null | grep -q dialout \
  && printf "[OK]   current user belongs to 'dialout'\n" \
  || printf "[WARN] current user is not in 'dialout'\n"

printf '\n'
if [ "$fail" -ne 0 ]; then
  printf 'Doctor found required toolchain mismatches.\n'
  exit 1
fi
printf 'Doctor: toolchain OK.\n'
