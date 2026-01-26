# Desarrollo realtime / pruebas sin hardware

Comandos básicos (desde la raíz del repo):

1. Levantar servicios (frontend + backend) en Docker:

```bash
docker-compose up -d --build
```

2. Abrir la UI: apuntar a `http://localhost:5173` (o el puerto expuesto por `frontend` en `docker-compose.yml`).

3. Probar WebSocket mediante UDP test sender (sin hardware):

En el contenedor local o en tu máquina, ejecutar:

```bash
python backend/scripts/send_udp_test.py --host 127.0.0.1 --port 8765 --gesture CLOSE --conf 0.95
```

El manager del backend por defecto escucha `JOINT_SOURCE=mock` o `udp` (ver variables de entorno). Si usas `udp` y ejecutas el sender, deberías ver eventos llegar al frontend.

4. Probar re-emisión desde REST (curl / Postman):

```bash
curl -X POST http://localhost:8000/v1/dev/joint-state -H 'Content-Type: application/json' -d '{"gesture":"PINCH","conf":0.92}'
```

Esto reemitirá el JointState recibido a los clientes WebSocket registrados.

Notas:
- Para cambiar la fuente realtime sin modificar código, exporta la variable `JOINT_SOURCE=mock|udp|serial` en el entorno del backend.
- Para puerto UDP, usa `UDP_PORT` (por defecto 8765).
- Si no hay puerto serial disponible al iniciar en `serial` mode, el backend hará fallback a mock y logueará una advertencia, no fallará.
