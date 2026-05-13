// ============ CONFIGURACIÓN DE PRÓTESIS ============
const MOTOR_TYPES = [
  { id: "bldc", name: "BLDC", full: "Brushless DC", torque: "1.2 Nm", power: "12W", efficient: "Alta", noise: "Bajo", desc: "Sin escobillas. Mayor vida útil y respuesta limpia. Recomendado para pinza fina." },
  { id: "dc",   name: "DC con escobillas", full: "Brushed DC", torque: "0.8 Nm", power: "8W", efficient: "Media", noise: "Medio", desc: "Construcción simple, control directo. Más asequible." },
  { id: "step", name: "Paso a paso", full: "Stepper", torque: "1.0 Nm", power: "10W", efficient: "Media", noise: "Alto", desc: "Posicionamiento preciso sin encoder. Útil para flexión por grados discretos." },
  { id: "servo",name: "Servomotor", full: "Servo (PWM)", torque: "1.5 Nm", power: "14W", efficient: "Alta", noise: "Bajo", desc: "Lazo cerrado interno. Ideal para articulación de muñeca y pulgar." },
];

const DOF_OPTIONS = [
  { dof: 1, label: "Apertura simple", desc: "Solo apertura/cierre coordinado de los 4 dedos." },
  { dof: 3, label: "Pinza + cierre", desc: "Pulgar, apertura, cierre por grupos." },
  { dof: 6, label: "Multifuncional", desc: "Cada dedo + rotación de pulgar. Estándar clínico." },
  { dof: 10, label: "Multiarticular", desc: "Falanges independientes + muñeca. Investigación." },
];

const PROSTHESIS_PRESETS = [
  { id: "bebionic",  brand: "Ottobock", model: "bebionic",   dof: 6,  motor: "bldc" },
  { id: "michelangelo", brand: "Ottobock", model: "Michelangelo", dof: 4, motor: "servo" },
  { id: "iLimb",     brand: "Össur",    model: "i-Limb Quantum", dof: 6, motor: "bldc" },
  { id: "vincent",   brand: "Vincent",  model: "Evolution 4",   dof: 10, motor: "bldc" },
  { id: "custom",    brand: "Custom",   model: "Prototipo local", dof: 3, motor: "dc" },
];

function ProsthesisScreen({ go }) {
  const [preset, setPreset]   = React.useState("bebionic");
  const [brand, setBrand]     = React.useState("Ottobock");
  const [model, setModel]     = React.useState("bebionic");
  const [serial, setSerial]   = React.useState("OB-7821-04N");
  const [motor, setMotor]     = React.useState("bldc");
  const [dof, setDof]         = React.useState(6);
  const [side, setSide]       = React.useState("right");
  const [photo, setPhoto]     = React.useState(null);
  const [photoName, setPhotoName] = React.useState("");
  const [openWidth, setOpenWidth] = React.useState(98);
  const [gripForce, setGripForce] = React.useState(140);
  const [latency, setLatency]     = React.useState(80);
  const fileRef = React.useRef(null);

  const onFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setPhotoName(f.name);
    const reader = new FileReader();
    reader.onload = () => setPhoto(reader.result);
    reader.readAsDataURL(f);
  };

  const applyPreset = (id) => {
    const p = PROSTHESIS_PRESETS.find(x => x.id === id);
    if (!p) return;
    setPreset(id); setBrand(p.brand); setModel(p.model); setMotor(p.motor); setDof(p.dof);
  };

  const motorObj = MOTOR_TYPES.find(m => m.id === motor);

  return (
    <>
      <Topbar crumb="MÓDULO · DISPOSITIVO" title="Configuración de Prótesis"
        actions={<><button className="btn btn-ghost">Cancelar</button><button className="btn btn-primary"><IcCheck size={14} /> Guardar configuración</button></>} />
      <div className="content">
        <div className="grid-2-3">
          {/* LEFT: form */}
          <div className="col">
            {/* Preset selector */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">STEP 1 · MODELO</div>
                  <h3 style={{ marginTop: 4 }}>Seleccionar prótesis</h3>
                  <p>Elija un modelo conocido o configure uno personalizado.</p>
                </div>
                <span className="step-num">01</span>
              </div>
              <div className="card-body">
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
                  {PROSTHESIS_PRESETS.map(p => (
                    <button key={p.id} onClick={() => applyPreset(p.id)} className={`mode-card ${preset === p.id ? "selected" : ""}`} style={{ padding: 14, minHeight: 0 }}>
                      <div className="kicker">{p.brand.toUpperCase()}</div>
                      <div style={{ fontWeight: 600, fontSize: 14, marginTop: 2 }}>{p.model}</div>
                      <div className="row" style={{ gap: 6, marginTop: 4 }}>
                        <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)" }}>{p.dof} DOF</span>
                        <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)" }}>· {p.motor.toUpperCase()}</span>
                      </div>
                    </button>
                  ))}
                </div>
                <div className="divider" style={{ margin: "16px 0" }} />
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                  <div className="field">
                    <label>Fabricante</label>
                    <input value={brand} onChange={e => setBrand(e.target.value)} />
                  </div>
                  <div className="field">
                    <label>Modelo</label>
                    <input value={model} onChange={e => setModel(e.target.value)} />
                  </div>
                  <div className="field">
                    <label>Número de serie</label>
                    <input className="mono" value={serial} onChange={e => setSerial(e.target.value)} />
                  </div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
                  <div className="field">
                    <label>Mano</label>
                    <div className="toggle" style={{ width: "100%" }}>
                      <button className={side === "right" ? "active" : ""} onClick={() => setSide("right")} style={{ flex: 1, padding: 8 }}>Derecha</button>
                      <button className={side === "left" ? "active" : ""} onClick={() => setSide("left")} style={{ flex: 1, padding: 8 }}>Izquierda</button>
                    </div>
                  </div>
                  <div className="field">
                    <label>Talla del socket</label>
                    <select><option>M (palma 80–85 mm)</option><option>S</option><option>L</option></select>
                  </div>
                </div>
              </div>
            </div>

            {/* Motor type */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">STEP 2 · ACTUADORES</div>
                  <h3 style={{ marginTop: 4 }}>Tipo de motor</h3>
                  <p>Determina el comportamiento de respuesta, torque y consumo.</p>
                </div>
                <span className="step-num">02</span>
              </div>
              <div className="card-body" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {MOTOR_TYPES.map(m => (
                  <button key={m.id} className={`mode-card ${motor === m.id ? "selected" : ""}`} onClick={() => setMotor(m.id)} style={{ padding: 16, minHeight: 0 }}>
                    <div className="row" style={{ justifyContent: "space-between" }}>
                      <div className="mode-icon tone-ink" style={{ width: 36, height: 36 }}><IcZap size={18} /></div>
                      {motor === m.id && <span className="pill data">Seleccionado</span>}
                    </div>
                    <div>
                      <h4 style={{ fontSize: 14 }}>{m.name}</h4>
                      <span className="mode-tag">{m.full.toUpperCase()}</span>
                    </div>
                    <p style={{ fontSize: 12.5 }}>{m.desc}</p>
                    <div className="row" style={{ marginTop: 4, gap: 10, flexWrap: "wrap" }}>
                      <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)" }}>Torque · <strong style={{ color: "var(--ink-2)" }}>{m.torque}</strong></span>
                      <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)" }}>P · <strong style={{ color: "var(--ink-2)" }}>{m.power}</strong></span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* DOF */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">STEP 3 · CINEMÁTICA</div>
                  <h3 style={{ marginTop: 4 }}>Grados de libertad (DOF)</h3>
                  <p>Articulaciones controlables independientemente.</p>
                </div>
                <span className="step-num">03</span>
              </div>
              <div className="card-body">
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                  {DOF_OPTIONS.map(d => (
                    <button key={d.dof} onClick={() => setDof(d.dof)} className={`mode-card ${dof === d.dof ? "selected" : ""}`} style={{ padding: 14, alignItems: "flex-start", minHeight: 0 }}>
                      <div className="serif" style={{ fontSize: 38, fontStyle: "italic", lineHeight: 1, color: dof === d.dof ? "var(--signal)" : "var(--ink-3)" }}>{d.dof}</div>
                      <div className="kicker" style={{ marginTop: 4 }}>DOF</div>
                      <div style={{ fontWeight: 600, fontSize: 13, marginTop: 4 }}>{d.label}</div>
                      <div className="muted" style={{ fontSize: 11.5 }}>{d.desc}</div>
                    </button>
                  ))}
                </div>

                <div className="divider" style={{ margin: "18px 0" }} />

                <div className="kicker">PARÁMETROS DEL ACTUADOR</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 18, marginTop: 10 }}>
                  <RangeField label="Apertura máxima" value={openWidth} setValue={setOpenWidth} min={40} max={120} unit="mm" />
                  <RangeField label="Fuerza de agarre" value={gripForce} setValue={setGripForce} min={20} max={200} unit="N" />
                  <RangeField label="Latencia objetivo" value={latency} setValue={setLatency} min={20} max={250} unit="ms" />
                </div>
              </div>
            </div>

            {/* Photo upload */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">STEP 4 · IDENTIFICACIÓN VISUAL</div>
                  <h3 style={{ marginTop: 4 }}>Foto de la prótesis</h3>
                  <p>Imagen del dispositivo del paciente. Aparece en el historial clínico.</p>
                </div>
                <span className="step-num">04</span>
              </div>
              <div className="card-body" style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 18 }}>
                <button
                  onClick={() => fileRef.current?.click()}
                  style={{
                    position: "relative",
                    border: photo ? "1px solid var(--bone-200)" : "1.5px dashed var(--bone-300)",
                    borderRadius: 8,
                    padding: photo ? 0 : "32px 18px",
                    minHeight: 220,
                    background: photo ? "var(--bone-100)" : "var(--bone-50)",
                    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10,
                    cursor: "pointer", textAlign: "center", overflow: "hidden",
                  }}
                >
                  <input ref={fileRef} type="file" accept="image/*" onChange={onFile} style={{ display: "none" }} />
                  {photo ? (
                    <img src={photo} alt="Prótesis" style={{ width: "100%", height: "100%", minHeight: 220, objectFit: "cover" }} />
                  ) : (
                    <>
                      <div className="module-icon tone-signal" style={{ width: 44, height: 44 }}><IcCamera size={20} /></div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>Subir foto del dispositivo</div>
                      <div className="muted" style={{ fontSize: 12.5, maxWidth: "32ch" }}>Arrastre o haga clic. JPG / PNG, máx. 5 MB. Idealmente con escala de referencia.</div>
                      <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)", letterSpacing: "0.08em", marginTop: 8 }}>O ARRASTRAR ARCHIVO AQUÍ</span>
                    </>
                  )}
                </button>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {photo && (
                    <div className="row" style={{ padding: 12, background: "var(--bone-50)", borderRadius: 6, justifyContent: "space-between" }}>
                      <div>
                        <div className="mono" style={{ fontSize: 12 }}>{photoName}</div>
                        <div className="muted" style={{ fontSize: 11 }}>Cargado correctamente</div>
                      </div>
                      <button onClick={() => { setPhoto(null); setPhotoName(""); }} className="icon-btn"><IcMinus size={14} /></button>
                    </div>
                  )}
                  <div className="kicker">CHECKLIST DE LA FOTO</div>
                  {[
                    "Toda la prótesis visible en una sola toma",
                    "Iluminación uniforme, sin reflejos",
                    "Fondo neutro (recomendado)",
                    "Incluir lado palmar y dorsal si es posible",
                  ].map(t => (
                    <div key={t} className="row" style={{ gap: 8 }}>
                      <IcCheckCircle size={16} color="var(--pulse)" />
                      <span style={{ fontSize: 12.5 }}>{t}</span>
                    </div>
                  ))}
                  <button className="btn btn-ghost" style={{ marginTop: 8 }}><IcCamera size={14} /> Capturar desde cámara</button>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT: summary */}
          <div className="col" style={{ position: "sticky", top: 80, alignSelf: "start" }}>
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">RESUMEN DE CONFIGURACIÓN</div>
                  <h3 style={{ marginTop: 4 }}>{brand} <span className="serif" style={{ fontStyle: "italic" }}>{model}</span></h3>
                  <p>Vista previa de cómo se guardará el dispositivo.</p>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {/* Photo preview or placeholder */}
                <div style={{ aspectRatio: "16 / 9", borderRadius: 6, overflow: "hidden", background: "var(--bone-100)", display: "grid", placeItems: "center", position: "relative" }}>
                  {photo ? (
                    <img src={photo} alt="Prótesis" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    <div style={{ textAlign: "center", color: "var(--ink-4)" }}>
                      <IcCamera size={24} />
                      <div className="mono" style={{ fontSize: 10.5, letterSpacing: "0.1em", marginTop: 4 }}>SIN FOTO</div>
                    </div>
                  )}
                  <div style={{ position: "absolute", top: 10, left: 10, display: "flex", gap: 6 }}>
                    <span className="pill data">{dof} DOF</span>
                    <span className="pill">{motorObj.name}</span>
                  </div>
                </div>

                {/* Specs */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <SummaryRow label="Serial" value={<span className="mono">{serial}</span>} />
                  <SummaryRow label="Mano" value={side === "right" ? "Derecha" : "Izquierda"} />
                  <SummaryRow label="Motor" value={motorObj.full} />
                  <SummaryRow label="DOF" value={`${dof} grados`} />
                  <SummaryRow label="Apertura" value={`${openWidth} mm`} />
                  <SummaryRow label="Fuerza" value={`${gripForce} N`} />
                  <SummaryRow label="Latencia" value={`${latency} ms`} />
                  <SummaryRow label="Torque" value={motorObj.torque} />
                </div>
              </div>
            </div>

            {/* Connection */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">CONEXIÓN</div>
                  <h3 style={{ marginTop: 4 }}>Diagnóstico</h3>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {[
                  ["Bluetooth", "Pareado", "live"],
                  ["Firmware", "v3.1.7 (al día)", "live"],
                  ["Batería", "82%", "live"],
                  ["Calibración", "Hace 2 días", "warn"],
                ].map(([l, v, t]) => (
                  <div key={l} className="row" style={{ justifyContent: "space-between" }}>
                    <span style={{ fontSize: 13 }}>{l}</span>
                    <span className={`pill ${t}`}>{v}</span>
                  </div>
                ))}
                <button className="btn btn-ghost btn-block" style={{ marginTop: 4 }}><IcRefresh size={14} /> Calibrar ahora</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function RangeField({ label, value, setValue, min, max, unit }) {
  return (
    <div className="field">
      <div className="row" style={{ justifyContent: "space-between" }}>
        <label>{label}</label>
        <span className="num" style={{ fontSize: 13 }}>{value} <span className="muted">{unit}</span></span>
      </div>
      <input type="range" min={min} max={max} value={value} onChange={e => setValue(+e.target.value)}
        style={{ width: "100%", accentColor: "var(--ink)" }} />
      <div className="row mono" style={{ justifyContent: "space-between", fontSize: 10.5, color: "var(--ink-4)" }}>
        <span>{min} {unit}</span><span>{max} {unit}</span>
      </div>
    </div>
  );
}

function SummaryRow({ label, value }) {
  return (
    <div>
      <div className="kicker">{label}</div>
      <div style={{ fontSize: 13.5, fontWeight: 500, marginTop: 2 }}>{value}</div>
    </div>
  );
}

Object.assign(window, { ProsthesisScreen });
