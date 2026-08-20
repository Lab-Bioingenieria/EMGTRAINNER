# Motion table — right hand (Eleven_DOF_Right)

Authoritative record of which Dynamixel drives which joint, and how far that
joint can actually travel. Every row was produced by moving **one motor at a
time** on the assembled hand and reading the encoder back — not by reading the
profile, which was wrong until this table existed.

`backend/app/schemas/hand_profiles.py` is the executable source of truth for
the mapping. This document is the evidence behind it.

## The chain runs backwards

The four-finger daisy chain is wired from the **pinky inward**, the reverse of
the anatomical order the original profile assumed:

```
ID:      4  5      6  7      8  9     10 11
actual:  pinky     ring      middle   index
profile: index     middle    ring     pinky    <- WRONG, corrected 2026-08-20
```

Both `Eleven_DOF_Right` and `Six_DOF_Right` were corrected. Only the
`motor_id` values were swapped: `min_deg`, `max_deg` and `default_deg` stay
with the finger, because they describe the joint, not the motor.

## Table

Travel is the measured peak-to-peak excursion, not the declared range.

| ID | Finger | Joint | Measured travel | Mapping evidence | State |
| ---: | --- | --- | ---: | --- | --- |
| 1 | thumb | `MCP_FE` | 34.5° | inferred | OK |
| 2 | thumb | `CMC_AA` | 32.1° | inferred | OK |
| 3 | thumb | `CMC_FE` | **1.7°** | operator confirmed | **JAMMED** |
| 4 | pinky | `PIP` | 69.3° | operator confirmed | OK |
| 5 | pinky | `MCP` | 69.0° | operator confirmed | OK |
| 6 | ring | `PIP` | 68.9° | operator confirmed | OK |
| 7 | ring | `MCP` | 68.7° | operator confirmed | OK |
| 8 | middle | `PIP` | 69.7° | operator confirmed | OK |
| 9 | middle | `MCP` | not measured | operator confirmed | pending |
| 10 | index | `PIP` | 68.6° | inferred | OK |
| 11 | index | `MCP` | not measured | inferred | pending |

**Mapping evidence** is deliberately separate from travel. *Operator confirmed*
means a human watched that motor move alone and named the finger. *Inferred*
means the id follows from the reversed-chain pattern and was never contradicted,
but nobody has visually confirmed it. Treat inferred rows as unverified.

## Motor 3 is not a software problem

The thumb `CMC_FE` sits at the trapezium, embedded in the base of the hand
rather than on a free finger. Its measured behaviour:

- Usable travel: **-15.6° to -13.9°**, i.e. 1.7° total.
- Rest position: **-14.7°**, outside the 0-45° the profile declares.
- Springs back to -14.7° whenever torque is released.
- Advances roughly 0.3° per 2° commanded, in both directions.

The probe ran at a reduced 0.25 A current limit and stopped after three
non-advancing steps, so the force needed to overcome the obstruction was
never applied and remains unknown.

**Hazard.** `Eleven_DOF_Right` does not list motor 3 in `locked_motors`,
while `Six_DOF_Right` and `Two_DOF_Left` both do. `DynamixelInterface.lock_motor`
enables torque and writes a goal position with no current limit and no
monitoring, so locking motor 3 at its declared `default_deg` of 0° would hold
it stalled 14.7° away from anything it can reach. Fix the range before
locking it, or leave it out of `locked_motors`.

## Reproducing this table

The bus must be **exclusive**. With the backend running and holding
`/dev/ttyUSB0`, a concurrent scan returned only 5 of 11 motors; with the port
free, all 11 answered. Stop the backend first.

```bash
cd backend

# identify one motor: prints what the profile claims, then wiggles it alone
PYTHONPATH=. .venv/bin/python -m tests.hand.identify_motors 4

# read-only inventory, one ping per id, never enables torque
make hand-inventory
```

`identify_motors` samples the encoder at **every waypoint**. A start-versus-end
delta cannot distinguish a completed round trip from a motor that never moved —
that mistake produced a false "moved: 11 ticks" reading for a motor whose real
excursion was 393 ticks.

## Open items

- Measure travel for motors 9 and 11.
- Visually confirm the finger for motors 1, 2, 10 and 11.
- Decide what to do with motor 3: free it mechanically and re-measure, or
  clamp its range to reality and lock it.
