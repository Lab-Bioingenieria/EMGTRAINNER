# Hardware inventory: U2D2 + Dynamixel hand

This is the software and operating contract for the robotic hand. Read it before
connecting the bus or moving any joint.

## Evidence boundary

**Software contract verified by tests:**

- ROBOTIS U2D2/FTDI adapter;
- Dynamixel Protocol 2.0 at **1,000,000 bps**;
- scanned IDs **1–15**, covering every ID declared by supported profiles;
- XL330 model resolution and read-only inventory behavior.

**Physical hardware verified (2026-08-20).** A read-only inventory over the
real bus answered on IDs **1-11**, every one reporting raw model number
`1200`, which resolves to **`XL330-M288-T`**. No mixture, no `XL330-M077-T`,
no unexpected or duplicate IDs. IDs 12-15 did not answer, matching the
supported profiles that lock or reserve them.

Adapter used, as a stable path without credentials:

```
/dev/serial/by-id/usb-FTDI_USB__-__Serial_Converter_FTAO520W-if00-port0
```

Per-joint travel measured after that scan is recorded in
[motion-table.md](motion-table.md), including the ID-to-finger correction the
scan exposed.

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

## Serial port resolution and per-OS latency

`find_u2d2_port()` (`backend/app/core/dynamixel_interface.py`) resolves the
U2D2, in order, and **fails closed** — it returns `None` instead of a guess
when nothing matches:

1. `hardware_config.main_port`, only if `_port_exists()` confirms it still
   exists;
2. `DYNAMIXEL_PORT` env var, same existence check;
3. `autodetect_u2d2_port()`: on Linux, the first sorted
   `/dev/serial/by-id/*FTDI*` path (survives replug/re-numbering); on every
   OS, the first serial port whose PySerial `vid` is `0x0403` (FTDI), or
   whose `description`/`manufacturer` contains `"FTDI"` when the driver
   hides the VID.

A stale configured port logs
`[WARN] - <source>=<port> no existe; autodetectando el adaptador` and falls
through, instead of failing with a bare `could not open port` and no hint
that autodetection existed.

**Why fail-closed matters**: this machine can also have an ESP32 EMG sensor
plugged in, and the two used to collide. Two symmetric bugs existed before
the rewrite (commit `1f03913`, PR #43):

- Windows: an unmatched search used to `return ports[0].device` — any COM
  port at all, including an empty legacy port or a Bluetooth virtual port.
- Linux: the first sorted `/dev/ttyUSB*` used to win, which can be the ESP32
  instead of the U2D2.

Both were replaced by the VID check above — the only signal that survives
Windows COM enumeration, Linux `ttyUSB*` re-numbering, and driver-text
differences across OSes.

**The mirror-image bug lived on the sensor side**
(`backend/core/serial/manager.py`): `SerialManager.find_device_port()`
excluded the hand's port with `"FTDI" in port.description or "FTDI" in
str(port.hwid)`. Neither field ever contains the string `"FTDI"` — PySerial
reports the U2D2's product string as `"USB <-> Serial Converter"` and its
`hwid` as `USB VID:PID=0403:6014 ...`; only `manufacturer` (never checked)
and the VID identify it. Result: the sensor's autodetect matched the U2D2
first, opened the Dynamixel bus at 921600 bps, and its streaming loop
consumed the motors' replies — current reads failed, torque disabled
fail-closed, the hand stopped moving, and nothing in the error pointed at
the real cause. Fixed the same way: VID first, text fallback second,
`exclude_ftdi=True` by default in `find_device_port()`.

### Per-OS behavior

| OS | U2D2 detection | Latency behavior | Status |
| --- | --- | --- | --- |
| **Windows** (Kevin's laptops) | Same VID/PID `0403:6014` scan through PySerial. No `by-id` path exists on Windows, so `_port_exists()` re-enumerates COM ports instead of using `os.path.exists()`. | The FTDI VCP driver also defaults its **Latency Timer to 16 ms**, set per-port in Device Manager → Ports → *(COM#)* → Advanced. `scripts/doctor.sh` is a Bash script and does not run on Windows. | Detection code is shared with Linux; the latency fix is **manual and has not been measured or automated on this repo** — set it by hand if motion feels sluggish. |
| **Linux (Kevin's laptop, amd64)** | Prefers `/dev/serial/by-id/*FTDI*`, else the VID scan. | `ftdi_sio` defaults `latency_timer` to **16 ms**, serializing every Dynamixel TxRx behind that timer instead of the ~0.2 ms the packet needs at 1 Mbps — measured 15.76 ms/read, 166 ms/11-motor sweep (6.0 Hz ceiling). | Fixed by the udev rule below. |
| **Linux/arm64 (Jetson Nano)** | Identical code path to amd64 — nothing ARM-specific in detection. | Same `ftdi_sio` default, same 16 ms, measured **15.61 ms/read, 164.58 ms/sweep (6.1 Hz)** — statistically identical to the laptop. | Fixed by the same udev rule. |

The Jetson measurement closed the original suspicion that "it doesn't work
on ARM either": it does, identically to x86. The bottleneck is the
`ftdi_sio` driver waiting on its timer, not the CPU computing — ARM changes
nothing about the bus. Where ARM *does* cost real time: the backend test
suite (24.8 s vs 9.4 s on the laptop) and the frontend build (9.7 s vs
6.3 s), both CPU-bound, unlike the bus.

### The latency_timer fix (Linux, amd64 and arm64)

`scripts/99-emgtrainner-u2d2.rules` sets `ATTR{latency_timer}="1"` for any
`ftdi_sio` USB-serial device:

```bash
make install-udev   # requires sudo once; applies live on replug
```

Measured improvement, same bus, same 11 motors (Jetson numbers shown; the
laptop started from the same 16 ms default):

| | latency_timer=16 ms | latency_timer=1 ms | improvement |
| --- | --- | --- | --- |
| READ present_position | 15.61 ms | 2.02 ms | 7.7x |
| WRITE profile_velocity | 16.00 ms | 2.08 ms | 7.7x |
| 11-motor sweep | 164.58 ms → 6.1 Hz | 22.30 ms → **44.8 Hz** | 7.4x |

Zero communication failures at either setting. `make doctor` reports
`[WARN] ttyUSB0 latency_timer = 16 ms (expected 1; run: make install-udev)`
until the rule is applied, then `[OK]`. The 44.8 Hz ceiling is also what
makes issue #44 (webcam teleoperation) viable: below 30 fps was impossible
at 6 Hz.

### Operational gotchas across all three systems

- The backend resolves the hand's port **once, at startup**
  (`EmgService.__init__` → `connect_hand()`). Plugging the U2D2 in after the
  backend is already running leaves `hand_interface = None` with no retry —
  restart the backend process, not just the cable.
- Grant serial access through the `dialout` group on Linux/Jetson, not root:

  ```bash
  sudo usermod -aG dialout $USER
  # log out/in, or use newgrp dialout
  ```

- Prefer a stable path over a raw device name on Linux:

  ```bash
  export DYNAMIXEL_PORT=/dev/serial/by-id/usb-FTDI_...-if00-port0
  ```

- `make doctor` (Linux/macOS only) checks tool versions, FTDI visibility,
  `latency_timer`, and `dialout` membership — all read-only, never opens the
  bus.

## Eleven_DOF_Right mapping

`backend/app/schemas/hand_profiles.py` is authoritative. Other profiles may
map or lock IDs differently.

| ID | Finger | Joint |
| ---: | --- | --- |
| 1 | thumb | `MCP_FE` |
| 2 | thumb | `CMC_AA` |
| 3 | thumb | `CMC_FE` |
| 4 | pinky | `PIP` |
| 5 | pinky | `MCP` |
| 6 | ring | `PIP` |
| 7 | ring | `MCP` |
| 8 | middle | `PIP` |
| 9 | middle | `MCP` |
| 10 | index | `PIP` |
| 11 | index | `MCP` |
| 12–13 | profile-dependent | locked/reserved in supported profiles |
| 14–15 | `Two_Motors` | independently controlled phalanx motors |

The four-finger block was fully reversed relative to the original profile:
the daisy chain runs from the pinky inward, so 4/5 drive the pinky, 6/7 the
ring, 8/9 the middle and 10/11 the index. Every one of those ids was
confirmed on the assembled hand, one motor at a time, with
`python -m tests.hand.identify_motors <id>`. Verify this mapping again on
any rebuilt hand: it reflects the physical daisy chain, not a convention.

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
