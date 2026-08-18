#!/usr/bin/env bash
# Read-only executable contract for a reproducible EMGTRAINNER checkout.
set -u

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
fail=0

ok() { printf '[OK]   %s\n' "$1"; }
bad() { printf '[FAIL] %s\n' "$1"; fail=1; }

expect_exact() {
  local file="$1" expected="$2"
  if [ -f "$file" ] && [ "$(tr -d '[:space:]' < "$file")" = "$expected" ]; then
    ok "$file pins exactly $expected"
  else
    bad "$file must pin exactly $expected"
  fi
}

expect_contains() {
  local file="$1" needle="$2" message="$3"
  if [ -f "$file" ] && grep -qF -- "$needle" "$file"; then
    ok "$message"
  else
    bad "$file must contain: $needle"
  fi
}

PYTHON_VERSION="3.11.9"
NODE_VERSION="22.23.2"
PNPM_VERSION="11.17.0"
UV_VERSION="0.11.32"
CI_FILE=".github/workflows/ci.yml"
REPRO_DOC="docs/reproducible-environment.md"
HW_DOC="docs/hardware-inventory.md"

[ ! -f frontend/package-lock.json ] \
  && ok "pnpm-lock.yaml is the only frontend lockfile" \
  || bad "frontend/package-lock.json must be removed"
[ -f frontend/pnpm-lock.yaml ] || bad "frontend/pnpm-lock.yaml is missing"
[ ! -f frontend/yarn.lock ] || bad "frontend/yarn.lock must not coexist with pnpm-lock.yaml"

grep -q '"latest"' frontend/package.json \
  && bad 'frontend/package.json must not use "latest"' \
  || ok 'frontend/package.json has no "latest" specifiers'

expect_exact backend/.python-version "$PYTHON_VERSION"
expect_exact frontend/.node-version "$NODE_VERSION"
expect_contains frontend/package.json "\"packageManager\": \"pnpm@${PNPM_VERSION}\"" "packageManager pins pnpm $PNPM_VERSION"
expect_contains "$CI_FILE" "python-version: '$PYTHON_VERSION'" "CI pins Python $PYTHON_VERSION"
expect_contains "$CI_FILE" "node-version: '$NODE_VERSION'" "CI pins Node $NODE_VERSION"
expect_contains "$CI_FILE" "version: $PNPM_VERSION" "CI pins pnpm $PNPM_VERSION"

for fact in "$PYTHON_VERSION" "$NODE_VERSION" "$PNPM_VERSION" "$UV_VERSION" \
  "**not** relocatable" 'never `rsync`/copy `backend/.venv`' \
  "pip download" "--find-links" "pnpm fetch --frozen-lockfile" \
  "pnpm install --offline --frozen-lockfile"; do
  expect_contains "$REPRO_DOC" "$fact" "reproducibility guide includes $fact"
done

expect_contains Makefile "scripts/doctor.sh" "Makefile delegates doctor checks"
[ -f scripts/doctor.sh ] || bad "scripts/doctor.sh is missing"
grep -qiE 'if not exist|if exist' Makefile \
  && bad "Makefile contains Windows-only batch syntax" \
  || ok "Makefile uses POSIX-safe shell syntax"
expect_contains Makefile "docker compose" "infra supports Docker Compose plugin"
expect_contains Makefile "docker-compose" "infra supports legacy docker-compose"

phony_targets="$(awk '/^\.PHONY:/{flag=1} flag{print; if ($0 !~ /\\$/) flag=0}' Makefile | tr -d '\\' | tr -s ' \t\n' '\n' | sed '1d;/^$/d')"
duplicates="$(printf '%s\n' "$phony_targets" | sort | uniq -d)"
[ -z "$duplicates" ] \
  && ok "Makefile .PHONY has no duplicates" \
  || bad "Makefile .PHONY duplicates: $(printf '%s' "$duplicates" | tr '\n' ' ')"

for fact in "Protocol 2.0" "1,000,000" "XL330" "unverified" "dialout" \
  "by-id" "emanual.robotis.com" "MCP_FE" "CMC_AA" "CMC_FE" \
  "Software contract" "Physical hardware"; do
  expect_contains "$HW_DOC" "$fact" "hardware guide includes $fact"
done

grep -qi 'safe to run before hardware is fully wired' "$HW_DOC" \
  && bad "hardware guide overclaims electrical safety" \
  || ok "hardware guide separates motion and electrical safety"

printf '\n'
if [ "$fail" -ne 0 ]; then
  printf 'Repository contract check failed.\n'
  exit 1
fi
printf 'Repository contract check passed.\n'
