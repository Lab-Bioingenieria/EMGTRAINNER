# Reproducible / disposable environments

EMGTRAINNER is meant to be buildable from a clean, disposable Linux box or
a recycled Jetson with no prior state — no manually-installed packages,
no hand-edited config beyond `backend/.env`, no assumptions about what
was on the machine before. This page is the setup + reset path; for the
hardware bus contract see
[docs/hardware-inventory.md](hardware-inventory.md).

## Pinned toolchain

| Tool | Version | Pinned in |
| --- | --- | --- |
| Python | **3.11.9** exactly | `backend/.python-version` |
| Node.js | **22.23.2** exactly | `frontend/.node-version` |
| pnpm | **11.17.0** exactly | `frontend/package.json` (`packageManager`) |
| uv | **0.11.32** (documented/tested CLI contract) | not managed by a lockfile — install it yourself, see below |

`scripts/check-repo-contract.sh` (`make check-contract`) fails the build
if any of these drift out of sync with what's documented here, or if CI
(`.github/workflows/ci.yml`) pins a different value. `make doctor`
(`scripts/doctor.sh`) checks the same exact versions on your machine and
exits nonzero on a mismatch.

`uv` itself is not a project dependency and is not controlled by any
lockfile in this repo (there is no `uv.lock` / `pyproject.toml`) — it's
the bootstrap tool you install once, the same way you'd install Python or
Node. `0.11.32` is the version this contract is documented and tested
against; newer `uv` releases are usually fine, but if `make doctor`
starts failing after a `uv` upgrade, pin back to `0.11.32` or update this
table deliberately.

## Toolchain bootstrap (exact commands)

On a clean machine, install each tool explicitly and at the pinned
version — don't pipe an unversioned "install latest" script.

```bash
# 1. uv 0.11.32 (installs into ~/.local/bin). Download first so the script
#    can be inspected before execution; see https://github.com/astral-sh/uv.
uv_installer="$(mktemp)"
curl --proto '=https' --tlsv1.2 -LsSf \
  -o "$uv_installer" https://astral.sh/uv/0.11.32/install.sh
less "$uv_installer"
sh "$uv_installer"
rm -f "$uv_installer"

# 2. Python 3.11.9, managed by uv (reads backend/.python-version automatically)
uv python install 3.11.9

# 3. Node.js 22.23.2 — use your team's version manager (nvm, fnm, mise, asdf)
#    or the official installer/package for your OS from https://nodejs.org.
#    Example with nvm:
nvm install 22.23.2
nvm use 22.23.2

# 4. pnpm 11.17.0, activated via Node's built-in Corepack (no separate install)
corepack enable
corepack prepare pnpm@11.17.0 --activate
```

## Bootstrap from zero

```bash
git clone <repo-url> EMGTRAINNER && cd EMGTRAINNER
make install-all   # backend: uv venv + requirements-dev.txt
                    # frontend: pnpm install --frozen-lockfile
make init-local     # copies backend/.env.example -> backend/.env
                     # only if backend/.env doesn't already exist
```

`make install-all` does not require Docker. It only needs `uv`, Python
3.11.9, and pnpm 11.17.0 on `PATH` (see bootstrap commands above). Docker
Compose (`make infra`) is optional — only needed if you want the backend
to run against real Postgres/Redis/RabbitMQ instead of the SQLite/
no-broker local defaults.

## What gets downloaded, and what's safe to delete

| Path | What it is | Safe to delete? |
| --- | --- | --- |
| `backend/.venv/` | Python virtualenv + installed packages | Yes — recreate with `make install-backend` |
| `frontend/node_modules/` | pnpm-installed JS packages | Yes — recreate with `make install-frontend` |
| `frontend/dist/` | production build output | Yes — recreate with `make build-frontend` |
| `backend/test.db` | SQLite file created by `pytest` runs | Yes — recreated on next test run |
| `backend/.env` | your local config (not tracked) | **No** — not reproducible from source; back it up if it has real secrets, otherwise just re-run `make init-local` |
| `backend/storage/` | real patient/session data (git-ignored) | **No** — see [docs/data-governance.md](data-governance.md) |

Nothing under version control is regenerated data; everything regenerated
lives in one of the paths above and is excluded via `.gitignore`.

## Local verification before CI

```bash
make verify
```

This runs, in order: the environment doctor, repository contract check, full
backend pytest suite (SQLite, no external services required), and frontend
production build (`vue-tsc` type-check + `vite build`). CI enforces the same
quality gates in isolated jobs, but provisions Python dependencies with `pip`
instead of reusing the local uv environment. A clean local run is therefore a
strong preflight signal, not a guarantee that CI will be green.

Individual steps:

```bash
make check-contract   # dependency/toolchain contract only
make test-backend      # backend pytest only
make build-frontend    # frontend build only
make doctor             # environment diagnostics (see below)
```

## `make doctor`

Read-only environment diagnostics (`scripts/doctor.sh`) — checks that
`uv`, Python 3.11.9, Node 22.23.2, and pnpm 11.17.0 exactly match the
pinned toolchain above, exiting nonzero if any required tool is missing
or at the wrong version. It also reports, as non-failing warnings/info,
whether `backend/.env` and the two dependency directories exist, whether
an FTDI (U2D2) serial device is currently visible, and whether the
current user is in the `dialout` group — those three are expected to be
absent on a fresh clone or a software-only machine with no hand
attached. It never opens the Dynamixel bus, writes a register, or moves
hardware.

```bash
make doctor
```

## Resetting a disposable box

To confirm the environment is genuinely reproducible — not just "works on
my machine" — delete the regenerable paths and rebuild from source:

```bash
rm -rf backend/.venv frontend/node_modules frontend/dist
make install-all
make verify
```

If this doesn't reproduce a green `make verify`, the repository's
reproducibility contract is broken and `scripts/check-repo-contract.sh`
or the pinned versions above should be the first place to look.

## Troubleshooting

**`make check-contract` fails on a fresh clone.**
Read the `[FAIL]` lines it prints — each one names the exact file and
fact it expected (e.g. a pinned `packageManager`, a missing
`docs/hardware-inventory.md` fact). Fix the named file; the script is the
executable spec.

**`pnpm install --frozen-lockfile` fails with "lockfile is not up to
date".**
Someone changed a dependency in `frontend/package.json` without updating
`frontend/pnpm-lock.yaml`. Don't run a broad `pnpm install` to "fix" it —
that can silently upgrade unrelated transitive packages. Update only the
lockfile entries for the dependency that actually changed.

**`ModuleNotFoundError` when running `pytest` or `python main.py`
directly.**
You're not using the project virtualenv. Use `make test-backend` /
`make run-backend`, or activate it yourself:
`source backend/.venv/bin/activate`. Do not rely on `uv run` here — this
project has no `pyproject.toml`, so `uv run` creates an unrelated
ephemeral environment instead of using `backend/.venv`.

**U2D2 not detected (`find_u2d2_port()` returns `None`).**
See the "Serial permissions" and "Adapter and port strategy" sections in
[docs/hardware-inventory.md](hardware-inventory.md). Most often this is
either a `dialout` group/permission issue, or the adapter genuinely isn't
plugged in — `make doctor` reports both.

**Backend needs Redis/RabbitMQ but you don't have Docker on the
Jetson.**
The default local `.env` and `make test-backend` path don't require
either — Celery/Redis are only exercised by background-task code paths,
not by the test suite. Only run `make infra` if you specifically need
those services.

**Jetson is offline / has no internet access, or you're recycling a
previously-imaged Jetson.**
`backend/.venv` and `frontend/node_modules` are **not** relocatable
artifacts — Python virtualenvs embed absolute paths and interpreter
metadata that don't reliably survive being copied to another machine,
and both directories can contain architecture-specific native
extensions (compiled Python C extensions, prebuilt Node native addons).
Copying either directory from an x86_64 dev machine onto Jetson's ARM64
(`aarch64`) will silently produce a broken environment, not a working
one — never `rsync`/copy `backend/.venv` or `frontend/node_modules`
between machines with different architectures, and don't rely on it even
between two same-architecture machines.

What *is* safe to move to an offline/recycled Jetson:

**Backend (Python), on a machine with matching architecture (ARM64) and
internet access** — another Jetson, or an ARM64 CI runner/VM:

```bash
# Download the resolved wheels for this exact requirements file — a pure
# fetch, no install, no venv created or touched.
python -m pip download -r backend/requirements-dev.txt -d wheelhouse
```

Transfer the `wheelhouse/` directory (not `backend/.venv`) to the offline
Jetson — `rsync`, a tarball, or a disk image all work, since it's just a
folder of downloaded `.whl` files. On the Jetson:

```bash
cd backend && uv venv --python 3.11.9   # or: make env-backend
uv pip install --offline --find-links ../wheelhouse -r requirements-dev.txt
```

`--offline` makes `uv` refuse to reach the network and resolve strictly
from `wheelhouse/`, so a stale or incomplete wheelhouse fails loudly
instead of silently falling back to a fresh download.

**Frontend (pnpm), on the same matching-architecture online machine:**

```bash
cd frontend && pnpm fetch --frozen-lockfile
```

This populates pnpm's content-addressable store
(`~/.local/share/pnpm/store` by default — confirm with `pnpm store
path`) without creating `node_modules`. Transfer that store directory to
the Jetson, then on the Jetson:

```bash
cd frontend && pnpm install --offline --frozen-lockfile
```

`--offline` likewise refuses the network and installs strictly from the
transferred store.

In both cases the Jetson **recreates** `backend/.venv` and
`frontend/node_modules` fresh, from ARM64 wheels/packages — which is
what makes them correct for its architecture; nothing built on another
machine is ever copied in directly.

The supported path is still running `make install-all` on a machine with
connectivity whenever possible; the wheelhouse/store transfer above is
the offline fallback, not a shortcut around rebuilding the venv/
node_modules.

**On reproducibility, precisely:** `backend/requirements-dev.txt` pins
exact versions (`==`) for every direct dependency, and
`frontend/pnpm-lock.yaml` pins the full resolved dependency tree with
integrity hashes. That's enough for deterministic *resolution* — the
same input files always resolve to the same package versions — but it is
not the same guarantee on both sides. The frontend lockfile's hashes
give byte-for-byte supply-chain verification of what pnpm installs; the
backend requirements file has **no hashes**, so `uv`/`pip` verify only
that the version number matches, not that the downloaded wheel's bytes
are what was originally vetted. Don't describe the backend install as
byte-for-byte reproducible — it's version-pinned, not hash-locked.
