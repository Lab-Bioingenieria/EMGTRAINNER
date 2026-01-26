# End-to-end Debug Checklist

Follow these steps to run end-to-end tests and debug the realtime pipeline (no hardware required).

**1) Build & start services (Docker)**

```powershell
# build and start in background
docker-compose up -d --build

# show running containers
docker-compose ps
```

**View logs**

```powershell
# follow backend logs (use this to verify source startup and UDP messages)
docker-compose logs -f backend

# follow frontend logs
docker-compose logs -f frontend

# or: docker logs -f backend
```

---

**2) POST a valid JointState to the dev endpoint**

Example `curl` (sends payload that the backend will re-broadcast to WS clients):

```bash
curl -v -X POST http://localhost:8000/v1/dev/joint-state \
  -H "Content-Type: application/json" \
  -d '{
    "ts": 1700000000.0,
    "gesture": "CLOSE",
    "conf": 0.95,
    "mode": "manual",
    "joints": { "thumb_mcp": 0.9, "index_mcp": 1.0, "index_pip": 0.6 }
  }'
```

- Expected: backend returns `{ "status": "ok" }` and the payload is broadcast to connected WebSocket clients. The frontend debug panel (in `HandViewer`) will show the last payload and timestamp.

---

**3) Run UDP test sender (for realtime UDP source)**

Default host/port: `127.0.0.1:8765` (matches `UDP_PORT` default).

```powershell
# from repo root (uses python on your system)
python .\backend\scripts\send_udp_test.py --host 127.0.0.1 --port 8765 --gesture CLOSE --conf 0.95
```

- Verify reception: watch backend logs (`docker-compose logs -f backend`) for lines like:

```
[udp_source] recv from ('127.0.0.1', 54321): CLOSE
```

and the frontend `HandViewer` overlay will show the last payload.

---

**4) Frontend debug panel (UI + console)**

- Where: The `HandViewer` component now shows an overlay with:
  - `WS`: connected / disconnected
  - `LastMsg`: timestamp of last received WS message
  - `Payload`: pretty-printed last payload (JointState or gesture payload)

- How to view: open the patient/session screen where the hand viewer is used (the same view you used earlier). The overlay appears in the top-right of the viewer.

- Console logs: open browser devtools (Console) and look for:
  - `[HandViewer] cached bones:` (how many bones were found in the GLB)
  - `[HandViewer] bone sample:` (sample list of bone names)
  - `[HandViewer] missing bones for payload:` (list of bone names not found when a JointState arrives)

These help diagnose rig/bone name mismatches.

---

**5) If the rig fails / troubleshooting**

- Backend
  - Check `docker-compose logs -f backend` for messages from `realtime.manager` (source start, serial open fallback) and `udp_source` message receipts.
  - If the serial port isn't available, the manager falls back to `mock` (you'll see a message like: `serial source failed opening: ... Falling back to mock.`)

- Frontend
  - Use the `HandViewer` overlay and browser console. The overlay shows the last raw payload and timestamp; console warns about missing bones if the JointState uses bone names not present in the GLB.

---

If you want, I can also:
- Add a small backend log line when the manager broadcasts a planned gesture (helpful to correlate backend->frontend), or
- Add a simple frontend button to manually call the `/v1/dev/joint-state` curl equivalent.

Tell me which additional quick helper you'd like next.
