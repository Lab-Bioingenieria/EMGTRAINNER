# Hardware inventory: U2D2 + Dynamixel hand

This is the software and operating contract for the robotic hand. Read it before
connecting the bus or moving any joint.

## Evidence boundary

**Software contract verified by tests:**

- ROBOTIS U2D2/FTDI adapter;
- Dynamixel Protocol 2.0 at **1,000,000 bps**;
- scanned IDs **1–15**, covering every ID declared by supported profiles;
- XL330 model resolution and read-only inventory behavior.

**Physical hardware unverified:** the installed servo SKU. Tests use a mocked
bus; they do not prove whether the hand contains `XL330-M077-T`,
`XL330-M288-T`, a mixture, or another model. Only a scan of the real hand can
resolve this. The Jetson was offline during this audit.

## Electrical safety before scanning

The inventory is motion-safe and read-only, not electrically safe by itself.
Before powering or opening the bus:

- verify U2D2 TTL pinout and connector orientation;
- use regulated power appropriate for the installed motors; never power the
  motor bus directly from USB;
- establish a common ground between host, adapter and motor supply;
- seat strain-free connectors while power is **off**;
- power off again before rewiring.

## Read-only inventory

After wiring and power are verified, run this before any movement:

```bash
make hand-inventory
# equivalent:
cd backend && PYTHONPATH=. .venv/bin/python -m tests.hand.inventory_scan
```

The command performs one `ping()` per ID. It never enables torque or writes a
register. It reports the port, protocol, baudrate, ID, raw model number and
resolved name.

| Raw model number | Resolved model | Official reference |
| --- | --- | --- |
| `1190` | `XL330-M077-T` | [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m077/) |
| `1200` | `XL330-M288-T` | [ROBOTIS e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xl330-m288/) |
| other | `UNKNOWN` | verify against the e-Manual; never guess |

Record the output for every responding ID before updating the BOM or claiming
an installed model. Physical verification remains **unverified** until then.

## Serial port resolution

`find_u2d2_port()` resolves, in order:

1. `hardware_config.main_port`;
2. `DYNAMIXEL_PORT`;
3. sorted `/dev/serial/by-id/*FTDI*` entries on Linux;
4. sorted `/dev/ttyUSB*` as an unstable fallback.

Prefer a stable `by-id` path, for example:

```bash
export DYNAMIXEL_PORT=/dev/serial/by-id/usb-FTDI_...-if00-port0
```

On Debian/Ubuntu/Jetson, grant serial access through `dialout`, not root:

```bash
sudo usermod -aG dialout $USER
# log out/in, or use newgrp dialout
```

`make doctor` checks tool versions, FTDI visibility and `dialout` membership
without opening the bus.

## Eleven_DOF_Right mapping

`backend/app/schemas/hand_profiles.py` is authoritative. Other profiles may
map or lock IDs differently.

| ID | Finger | Joint |
| ---: | --- | --- |
| 1 | thumb | `MCP_FE` |
| 2 | thumb | `CMC_AA` |
| 3 | thumb | `CMC_FE` |
| 4 | index | `PIP` |
| 5 | index | `MCP` |
| 6 | middle | `PIP` |
| 7 | middle | `MCP` |
| 8 | ring | `PIP` |
| 9 | ring | `MCP` |
| 10 | pinky | `PIP` |
| 11 | pinky | `MCP` |
| 12–13 | profile-dependent | locked/reserved in supported profiles |
| 14–15 | `Two_Motors` | independently controlled phalanx motors |

## Motion safety contract

- Scan and compare IDs with the selected profile before motion.
- `move_motor_safe` and `move_motors_sync_safe` require three consecutive
  over-limit samples before disabling torque and raising `RuntimeError`.
- Current telemetry fails closed: a read error disables the single motor or
  every synchronized target before raising.
- Overcurrent is a hard stop. Inspect binding, wiring, power and limits before
  retrying; never catch-and-retry it in a loop.
- Inventory never enables torque. Explicit motion/configuration methods do.
- If process state is uncertain, power off the hand before inspection.

## Related

- [Reproducible and recycled environments](reproducible-environment.md)
- [Data governance](data-governance.md)
