// ============ PANEL DE PACIENTES ============
function PatientsScreen() {
  const patients = [
    { id: "P-2341", name: "María González",   age: 45, sessions: 12, last: "2026-05-10", progress: 89, status: "active",    avatar: "MG" },
    { id: "P-1892", name: "Carlos Rodríguez", age: 38, sessions: 8,  last: "2026-05-10", progress: 76, status: "active",    avatar: "CR" },
    { id: "P-3021", name: "Ana Martínez",     age: 52, sessions: 15, last: "2026-05-09", progress: 94, status: "active",    avatar: "AM" },
    { id: "P-4156", name: "Luis Fernández",   age: 41, sessions: 5,  last: "2026-05-08", progress: 62, status: "inactive",  avatar: "LF" },
    { id: "P-5234", name: "Elena Sánchez",    age: 35, sessions: 20, last: "2026-05-07", progress: 97, status: "completed", avatar: "ES" },
    { id: "P-6789", name: "Roberto López",    age: 48, sessions: 3,  last: "2026-05-05", progress: 45, status: "active",    avatar: "RL" },
  ];
  const statusMap = { active: ["live", "Activo"], inactive: ["off", "Inactivo"], completed: ["data", "Completado"] };
  return (
    <>
      <Topbar crumb="MÓDULO · PANEL DE PACIENTES" title="Panel de Pacientes"
        actions={<><button className="btn btn-ghost"><IcDl size={14} /> Exportar</button><button className="btn btn-primary"><IcPlus size={14} /> Nuevo paciente</button></>} />
      <div className="content">
        <div className="grid-4">
          <KPI kicker="PACIENTES TOTALES" value="124" delta="+8" deltaDir="up" meta="este mes" spark={[110,113,116,118,121,124]} />
          <KPI kicker="SESIONES HOY"     value="18" meta="5 en progreso" accent="var(--pulse)" spark={[12,16,18,14,18,18]} sparkColor="var(--pulse)" />
          <KPI kicker="PROGRESO PROMEDIO" value="78" unit="%" delta="+5" deltaDir="up" meta="vs. mes anterior" accent="var(--data)" spark={[72,73,75,74,76,78]} sparkColor="var(--data)" />
          <KPI kicker="PACIENTES ACTIVOS" value="89" meta="72% del total" accent="var(--signal)" spark={[81,83,85,87,88,89]} sparkColor="var(--signal)" />
        </div>

        <div className="grid-2-3" style={{ marginTop: 18 }}>
          <div className="card">
            <div className="card-head">
              <div>
                <div className="kicker">PATIENT REGISTRY</div>
                <h3 style={{ marginTop: 4 }}>Listado de pacientes</h3>
                <p>Gestión y seguimiento de todos los pacientes activos.</p>
              </div>
              <div className="row">
                <div className="search" style={{ width: 220 }}>
                  <IcSearch size={14} />
                  <input placeholder="Buscar paciente…" />
                </div>
                <select style={{ padding: "8px 12px", border: "1px solid var(--bone-200)", borderRadius: 6, fontSize: 13, background: "var(--paper)" }}>
                  <option>Todos</option><option>Activos</option><option>Inactivos</option>
                </select>
              </div>
            </div>
            <div className="card-body flush">
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Paciente</th><th>Sesiones</th><th>Última sesión</th><th>Progreso</th><th>Estado</th><th />
                  </tr>
                </thead>
                <tbody>
                  {patients.map(p => {
                    const [tone, label] = statusMap[p.status];
                    return (
                      <tr key={p.id}>
                        <td>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <div className="avatar">{p.avatar}</div>
                            <div>
                              <div style={{ fontWeight: 600 }}>{p.name}</div>
                              <div className="mono muted" style={{ fontSize: 11 }}>{p.id} · {p.age} años</div>
                            </div>
                          </div>
                        </td>
                        <td className="num">{p.sessions}</td>
                        <td className="mono muted" style={{ fontSize: 12 }}>{p.last}</td>
                        <td>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <div className="bar signal" style={{ width: 90 }}><span style={{ width: `${p.progress}%` }} /></div>
                            <span className="num" style={{ fontSize: 12 }}>{p.progress}%</span>
                          </div>
                        </td>
                        <td><span className={`pill ${tone}`}>{label}</span></td>
                        <td style={{ textAlign: "right" }}><IcChev size={14} color="var(--ink-4)" /></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="col">
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">GESTURE RADAR</div>
                  <h3 style={{ marginTop: 4 }}>Comparativa de gestos</h3>
                  <p>Cohorte actual vs. promedio histórico.</p>
                </div>
              </div>
              <div className="card-body" style={{ display: "grid", placeItems: "center" }}>
                <RadarChart
                  axes={["Open", "Close", "Pinch", "Cyl", "Sphere", "Wave", "Point"]}
                  series={[
                    { color: "var(--ink)",  values: [0.95, 0.92, 0.81, 0.86, 0.88, 0.74, 0.91] },
                    { color: "var(--bone-400)", values: [0.78, 0.76, 0.70, 0.72, 0.74, 0.65, 0.79] },
                  ]}
                />
                <div className="row" style={{ gap: 18, marginTop: 6, fontSize: 12 }}>
                  <span><span style={{ display: "inline-block", width: 9, height: 9, background: "var(--ink)", borderRadius: 2, marginRight: 6 }} />Cohorte actual</span>
                  <span className="muted"><span style={{ display: "inline-block", width: 9, height: 9, background: "var(--bone-400)", borderRadius: 2, marginRight: 6 }} />Promedio</span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">DATA EXPORT</div>
                  <h3 style={{ marginTop: 4 }}>Exportación clínica</h3>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <button className="btn btn-ghost btn-block" style={{ justifyContent: "flex-start", padding: 12 }}>
                  <IcDl size={14} /> Datos de sesiones (.csv)
                </button>
                <button className="btn btn-ghost btn-block" style={{ justifyContent: "flex-start", padding: 12 }}>
                  <IcDl size={14} /> Métricas de progreso (.xlsx)
                </button>
                <button className="btn btn-ghost btn-block" style={{ justifyContent: "flex-start", padding: 12 }}>
                  <IcFile size={14} /> Informe clínico (.pdf)
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="card" style={{ marginTop: 18 }}>
          <div className="card-head">
            <div>
              <div className="kicker">LONGITUDINAL TREND</div>
              <h3 style={{ marginTop: 4 }}>Progreso del paciente · María González</h3>
              <p>Precisión motora por semana de rehabilitación.</p>
            </div>
            <select style={{ padding: "8px 12px", border: "1px solid var(--bone-200)", borderRadius: 6, fontSize: 13, background: "var(--paper)" }}>
              <option>Últimas 9 semanas</option>
              <option>Últimos 30 días</option>
              <option>Histórico completo</option>
            </select>
          </div>
          <div className="card-body">
            <LineChart
              labels={["S1","S2","S3","S4","S5","S6","S7","S8","S9"]}
              yMin={50} yMax={100} yUnit="%"
              series={[
                { color: "var(--ink)", fill: true, values: [55, 61, 70, 68, 78, 85, 81, 88, 92] },
              ]}
            />
          </div>
        </div>
      </div>
    </>
  );
}

// ============ ALMACENAMIENTO ============
function StorageScreen() {
  const files = [
    ["session_2026-05-12_142233_p2341.csv", "12 May 2026 · 14:22", "2.4 MB"],
    ["session_2026-05-12_110815_p1892.csv", "12 May 2026 · 11:08", "3.1 MB"],
    ["session_2026-05-11_164002_p3021.csv", "11 May 2026 · 16:40", "1.8 MB"],
    ["session_2026-05-11_091543_p4156.csv", "11 May 2026 · 09:15", "4.2 MB"],
    ["session_2026-05-10_180322_p5234.csv", "10 May 2026 · 18:03", "2.9 MB"],
    ["session_2026-05-10_145511_p6789.csv", "10 May 2026 · 14:55", "1.2 MB"],
    ["session_2026-05-09_113207_p2341.csv", "09 May 2026 · 11:32", "2.7 MB"],
    ["session_2026-05-08_165840_p1892.csv", "08 May 2026 · 16:58", "3.4 MB"],
  ];
  return (
    <>
      <Topbar crumb="MÓDULO · ALMACENAMIENTO" title="Almacenamiento de Sesiones"
        actions={<><button className="btn btn-ghost"><IcRefresh size={14} /> Actualizar</button><button className="btn btn-primary"><IcDl size={14} /> Exportar todo</button></>} />
      <div className="content">
        <div className="grid-4">
          <KPI kicker="ARCHIVOS TOTALES" value="1,247" delta="+18" deltaDir="up" meta="esta semana" accent="var(--data)" />
          <KPI kicker="TAMAÑO TOTAL" value="3.42" unit="GB" meta="de 50 GB asignados" accent="var(--ink)" />
          <KPI kicker="ÚLTIMA SESIÓN" value="14:22" meta="hoy · P-2341" accent="var(--pulse)" />
          <KPI kicker="RETENCIÓN" value="2y" meta="política HIPAA activa" accent="var(--signal)" />
        </div>

        <div className="card" style={{ marginTop: 18 }}>
          <div className="card-head">
            <div>
              <div className="kicker">CSV ARCHIVE</div>
              <h3 style={{ marginTop: 4 }}>Historial de grabaciones</h3>
              <p>Datos sEMG sin procesar de cada sesión, con metadatos clínicos.</p>
            </div>
            <div className="row">
              <div className="search" style={{ width: 280 }}>
                <IcSearch size={14} />
                <input placeholder="Buscar por nombre, ID paciente, fecha…" />
              </div>
              <button className="btn btn-ghost"><IcAdjust size={14} /> Filtros</button>
            </div>
          </div>
          <div className="card-body flush">
            <table className="tbl">
              <thead>
                <tr><th>Nombre del archivo</th><th>Fecha de creación</th><th>Tamaño</th><th>Estado</th><th style={{ textAlign: "right" }}>Acciones</th></tr>
              </thead>
              <tbody>
                {files.map(f => (
                  <tr key={f[0]}>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div className="module-icon tone-data" style={{ width: 32, height: 32, borderRadius: 6 }}><IcFile size={15} /></div>
                        <span className="mono" style={{ fontSize: 12.5 }}>{f[0]}</span>
                      </div>
                    </td>
                    <td className="muted">{f[1]}</td>
                    <td className="mono">{f[2]}</td>
                    <td><span className="pill live">Encriptado</span></td>
                    <td style={{ textAlign: "right" }}>
                      <div style={{ display: "inline-flex", gap: 4 }}>
                        <button className="icon-btn"><IcEye size={15} /></button>
                        <button className="icon-btn"><IcDl size={15} /></button>
                        <button className="icon-btn"><IcMore size={15} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}

// ============ SESIÓN DOCTOR (Protocol) ============
function DoctorSessionScreen({ go }) {
  const [mode, setMode] = React.useState(null);
  const [name, setName] = React.useState("");
  return (
    <>
      <Topbar crumb="MÓDULO · SESIÓN DOCTOR" title="Crear protocolo de entrenamiento" />
      <div className="content" style={{ maxWidth: 1080 }}>
        <div className="card">
          <div className="card-head">
            <div>
              <div className="kicker">STEP 1 OF 3</div>
              <h3 style={{ marginTop: 4 }}>Definir protocolo</h3>
              <p>Asigne un nombre y elija el modo de control para esta sesión.</p>
            </div>
            <span className="step-num">01</span>
          </div>
          <div className="card-body">
            <div className="field">
              <label>Nombre del protocolo <span className="muted">(opcional)</span></label>
              <input value={name} onChange={e => setName(e.target.value)} placeholder="Ej. Rehabilitación inicial — semana 2" />
              <span className="hint">Aparecerá en el historial clínico del paciente.</span>
            </div>
          </div>
        </div>

        <div className="card" style={{ marginTop: 18 }}>
          <div className="card-head">
            <div>
              <div className="kicker">STEP 2 OF 3</div>
              <h3 style={{ marginTop: 4 }}>Seleccionar modo de entrenamiento</h3>
              <p>El modo determina quién controla el flujo de la sesión.</p>
            </div>
            <span className="step-num">02</span>
          </div>
          <div className="card-body" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            {[
              {
                id: "tlc",
                title: "Modo Guiado",
                code: "TLC · Teacher-Led Control",
                desc: "Usted define gestos, repeticiones y tiempos. Ideal para sesiones supervisadas y evaluación clínica.",
                icon: <IcSteth size={20} />,
                tone: "tone-pulse",
                meta: "Promedio: 4-6 min",
              },
              {
                id: "llc",
                title: "Modo Autónomo",
                code: "LLC · Learner-Led Control",
                desc: "El sistema presenta gestos de forma adaptativa. El paciente controla el flujo y el ritmo.",
                icon: <IcRefresh size={20} />,
                tone: "tone-signal",
                meta: "Promedio: 6-12 min",
              },
            ].map(m => (
              <button key={m.id} className={`mode-card ${mode === m.id ? "selected" : ""}`} onClick={() => setMode(m.id)}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div className={`mode-icon ${m.tone}`} style={{ width: 40, height: 40 }}>{m.icon}</div>
                  {mode === m.id && <div style={{ width: 22, height: 22, borderRadius: "50%", background: "var(--ink)", color: "var(--bone-50)", display: "grid", placeItems: "center" }}><IcCheck size={12} /></div>}
                </div>
                <div>
                  <h4>{m.title}</h4>
                  <span className="mode-tag">{m.code}</span>
                </div>
                <p>{m.desc}</p>
                <div className="row" style={{ marginTop: "auto", paddingTop: 12, borderTop: "1px solid var(--bone-200)", justifyContent: "space-between" }}>
                  <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)", letterSpacing: "0.06em" }}>{m.meta}</span>
                  <IcArrow size={14} />
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="card" style={{ marginTop: 18, opacity: mode ? 1 : 0.55 }}>
          <div className="card-head">
            <div>
              <div className="kicker">STEP 3 OF 3</div>
              <h3 style={{ marginTop: 4 }}>Asignar paciente y dispositivo</h3>
              <p>Verifique la prótesis configurada antes de iniciar la sesión.</p>
            </div>
            <span className="step-num">03</span>
          </div>
          <div className="card-body" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
            <div className="field">
              <label>Paciente</label>
              <select disabled={!mode}>
                <option>María González · P-2341 · 45 años</option>
                <option>Carlos Rodríguez · P-1892 · 38 años</option>
                <option>Ana Martínez · P-3021 · 52 años</option>
              </select>
            </div>
            <div className="field">
              <label>Prótesis configurada</label>
              <div style={{ padding: "9px 12px", border: "1px solid var(--bone-200)", borderRadius: 6, fontSize: 13, background: "var(--bone-50)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span><strong>Ottobock bebionic</strong> · 6 DOF · BLDC</span>
                <button onClick={() => go("prosthesis")} style={{ fontSize: 12, color: "var(--ink-4)", textDecoration: "underline" }}>cambiar</button>
              </div>
            </div>
          </div>
          <div className="card-body" style={{ borderTop: "1px solid var(--bone-200)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div className="muted" style={{ fontSize: 12.5 }}>El paciente recibirá una notificación cuando el protocolo esté listo.</div>
            <div className="row">
              <button className="btn btn-ghost">Guardar borrador</button>
              <button className="btn btn-primary" disabled={!mode} onClick={() => mode && go("session-config")}>
                Continuar a configuración <IcArrow size={14} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

// ============ SESIÓN PACIENTE (mode select) ============
function PatientSessionScreen({ go }) {
  return (
    <>
      <Topbar crumb="MÓDULO · SESIÓN PACIENTE" title="Iniciar sesión de entrenamiento" />
      <div className="content" style={{ maxWidth: 1080 }}>
        <div className="card" style={{ position: "relative", overflow: "hidden", padding: "32px 36px" }}>
          <div style={{ position: "absolute", inset: 0, opacity: 0.15 }}>
            <EMGWave height={220} color="var(--ink)" speed={0.5} />
          </div>
          <div style={{ position: "relative" }}>
            <div className="kicker">Bienvenida, María</div>
            <h2 style={{ fontSize: 32, lineHeight: 1.1, letterSpacing: "-0.02em", fontWeight: 400, marginTop: 6 }}>
              ¿Cómo desea <span className="serif" style={{ fontStyle: "italic" }}>entrenar hoy</span>?
            </h2>
            <p className="muted" style={{ marginTop: 8, maxWidth: "48ch" }}>
              Puede conectarse con su terapeuta para una sesión guiada, o practicar libremente y visualizar sus señales sEMG.
            </p>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: 18 }}>
          {[
            {
              id: "supervised",
              icon: <IcWifi size={22} />, tone: "tone-pulse",
              title: "Sesión supervisada",
              tag: "Requiere código de médico",
              desc: "Conéctese con su terapeuta para una sesión guiada en tiempo real. Su progreso se registra automáticamente.",
              foot: "Próxima cita: hoy · 16:00 · Dra. Morales",
              accent: "Recomendado",
              go: "session-config",
            },
            {
              id: "free",
              icon: <IcHand size={22} />, tone: "tone-signal",
              title: "Entrenamiento libre",
              tag: "Sin supervisión",
              desc: "Practique gestos libremente y visualice las señales sEMG en tiempo real. Útil para mantener tono muscular.",
              foot: "Última práctica libre: hace 2 días",
              accent: null,
              go: "session-config",
            },
          ].map(c => (
            <button key={c.id} className="mode-card" onClick={() => go(c.go)} style={{ minHeight: 240 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div className={`mode-icon ${c.tone}`} style={{ width: 44, height: 44 }}>{c.icon}</div>
                {c.accent && <span className="pill signal">★ {c.accent}</span>}
              </div>
              <div>
                <h4 style={{ fontSize: 18 }}>{c.title}</h4>
                <span className="mode-tag">{c.tag}</span>
              </div>
              <p>{c.desc}</p>
              <div className="row" style={{ marginTop: "auto", paddingTop: 16, borderTop: "1px solid var(--bone-200)", justifyContent: "space-between" }}>
                <span className="mono" style={{ fontSize: 11, color: "var(--ink-4)", letterSpacing: "0.04em" }}>{c.foot}</span>
                <IcArrow size={14} />
              </div>
            </button>
          ))}
        </div>

        {/* Connection status strip */}
        <div className="card" style={{ marginTop: 14, padding: "16px 18px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div className="row" style={{ gap: 16 }}>
            <div className="row" style={{ gap: 8 }}>
              <span className="dot live" />
              <div>
                <div style={{ fontSize: 12.5, fontWeight: 500 }}>Sensores sEMG conectados</div>
                <div className="mono muted" style={{ fontSize: 11, letterSpacing: "0.04em" }}>4 canales · 1000 Hz · señal estable</div>
              </div>
            </div>
            <div className="divider" style={{ width: 1, height: 30 }} />
            <div className="row" style={{ gap: 8 }}>
              <span className="dot live" />
              <div>
                <div style={{ fontSize: 12.5, fontWeight: 500 }}>Prótesis Ottobock bebionic</div>
                <div className="mono muted" style={{ fontSize: 11, letterSpacing: "0.04em" }}>BLDC · 6 DOF · Batería 82%</div>
              </div>
            </div>
          </div>
          <button className="btn btn-ghost" onClick={() => go("prosthesis")}><IcCpu size={14} /> Configurar dispositivo</button>
        </div>
      </div>
    </>
  );
}

// ============ CONFIGURACIÓN DE SESIÓN (TLC) ============
const GESTURES = [
  { id: "open",   es: "Abrir",      en: "Open",        emoji: "open" },
  { id: "close",  es: "Cerrar",     en: "Close",       emoji: "close" },
  { id: "like",   es: "Like",       en: "Thumbs up",   emoji: "like" },
  { id: "point",  es: "Apuntar",    en: "Point",       emoji: "point" },
  { id: "pinch",  es: "Pinza",      en: "Pinch",       emoji: "pinch" },
  { id: "cyl",    es: "Cilíndrico", en: "Cylindrical", emoji: "cyl" },
  { id: "sphere", es: "Esférico",   en: "Spherical",   emoji: "sphere" },
];

function GestureGlyph({ id, size = 28 }) {
  // Simple abstract glyph (NOT a hand drawing — pure geometry per gesture)
  const styles = {
    open:   <g><circle cx="14" cy="14" r="9" fill="none" stroke="currentColor" strokeWidth="1.6" /><circle cx="14" cy="14" r="3" fill="currentColor" /></g>,
    close:  <g><circle cx="14" cy="14" r="9" fill="currentColor" /></g>,
    like:   <g><rect x="9" y="13" width="10" height="10" rx="2" fill="currentColor" /><rect x="11" y="5" width="6" height="8" rx="1.5" fill="currentColor" /></g>,
    point:  <g><circle cx="14" cy="14" r="2" fill="currentColor" /><path d="M14 2v8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" /></g>,
    pinch:  <g><path d="M9 9c2 2 8 2 10 0" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" /><path d="M9 19c2-2 8-2 10 0" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" /></g>,
    cyl:    <g><rect x="9" y="5" width="10" height="18" rx="5" fill="none" stroke="currentColor" strokeWidth="1.6" /><line x1="9" y1="14" x2="19" y2="14" stroke="currentColor" strokeWidth="1.6" strokeDasharray="2 2" /></g>,
    sphere: <g><circle cx="14" cy="14" r="9" fill="none" stroke="currentColor" strokeWidth="1.6" /><ellipse cx="14" cy="14" rx="9" ry="3.5" fill="none" stroke="currentColor" strokeWidth="1.2" /><ellipse cx="14" cy="14" rx="3.5" ry="9" fill="none" stroke="currentColor" strokeWidth="1.2" /></g>,
  };
  return <svg width={size} height={size} viewBox="0 0 28 28">{styles[id]}</svg>;
}

function SessionConfigScreen({ go }) {
  const [selected, setSelected] = React.useState(new Set(["open", "close", "pinch"]));
  const [duration, setDuration] = React.useState(5);
  const [reps, setReps] = React.useState(3);
  const [name, setName] = React.useState("");
  const [age, setAge] = React.useState("");
  const toggle = (id) => {
    const n = new Set(selected);
    n.has(id) ? n.delete(id) : n.add(id);
    setSelected(n);
  };
  const sensorsOk = true;
  const canStart = sensorsOk && selected.size >= 2 && name;
  const estDuration = (selected.size * duration * reps + reps * 3);

  return (
    <>
      <Topbar crumb="SESIÓN PACIENTE · CONFIGURACIÓN" title="Configuración de sesión"
        actions={<button className="btn btn-ghost" onClick={() => go("doctor")}><IcArrowL size={14} /> Cambiar modo</button>} />
      <div className="content" style={{ maxWidth: 1280 }}>
        <div className="grid-2-3">
          <div className="col">
            {/* Patient + params */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">PATIENT & PARAMETERS</div>
                  <h3 style={{ marginTop: 4 }}>Datos del paciente</h3>
                </div>
                <span className="pill data">Mode · Teacher-Led</span>
              </div>
              <div className="card-body" style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 14 }}>
                <div className="field">
                  <label>Nombre del paciente <span className="req">*</span></label>
                  <input value={name} onChange={e => setName(e.target.value)} placeholder="Requerido" />
                </div>
                <div className="field">
                  <label>Edad</label>
                  <input value={age} onChange={e => setAge(e.target.value)} placeholder="Opcional" />
                </div>
                <div className="field">
                  <label>Duración por gesto</label>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <button className="icon-btn" style={{ border: "1px solid var(--bone-200)" }} onClick={() => setDuration(Math.max(1, duration - 1))}><IcMinus size={14} /></button>
                    <input value={duration} onChange={e => setDuration(+e.target.value || 1)} style={{ textAlign: "center" }} />
                    <button className="icon-btn" style={{ border: "1px solid var(--bone-200)" }} onClick={() => setDuration(duration + 1)}><IcPlus size={14} /></button>
                    <span className="mono muted" style={{ fontSize: 12 }}>seg</span>
                  </div>
                </div>
                <div className="field">
                  <label>Repeticiones del circuito</label>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <button className="icon-btn" style={{ border: "1px solid var(--bone-200)" }} onClick={() => setReps(Math.max(1, reps - 1))}><IcMinus size={14} /></button>
                    <input value={reps} onChange={e => setReps(+e.target.value || 1)} style={{ textAlign: "center" }} />
                    <button className="icon-btn" style={{ border: "1px solid var(--bone-200)" }} onClick={() => setReps(reps + 1)}><IcPlus size={14} /></button>
                    <span className="mono muted" style={{ fontSize: 12 }}>× ciclos</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Gestures */}
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">GESTURE LIBRARY</div>
                  <h3 style={{ marginTop: 4 }}>Selección de gestos</h3>
                  <p>Elija los gestos a entrenar. Mínimo 2 para sesiones supervisadas.</p>
                </div>
                <span className="pill">{selected.size} / {GESTURES.length} seleccionados</span>
              </div>
              <div className="card-body">
                <div className="gestures">
                  {GESTURES.map(g => (
                    <button key={g.id} className={`gesture ${selected.has(g.id) ? "active" : ""}`} onClick={() => toggle(g.id)}>
                      <div className="g-icon"><GestureGlyph id={g.emoji} /></div>
                      <div className="g-name">{g.es}</div>
                      <div className="g-sub">{g.en.toUpperCase()}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Right column */}
          <div className="col">
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">PRE-FLIGHT CHECK</div>
                  <h3 style={{ marginTop: 4 }}>Estado del sistema</h3>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {[
                  ["Sensor CH1 — Flexor digit.", "ok"],
                  ["Sensor CH2 — Extensor digit.", "ok"],
                  ["Sensor CH3 — Flexor carpi rad.", "ok"],
                  ["Sensor CH4 — Extensor carpi uln.", "ok"],
                ].map(([l, s]) => (
                  <div key={l} className="row" style={{ justifyContent: "space-between" }}>
                    <div className="row" style={{ gap: 10 }}>
                      <div className={`sensor-pip ${s}`} />
                      <span style={{ fontSize: 13 }}>{l}</span>
                    </div>
                    <span className="mono muted" style={{ fontSize: 11 }}>—42 µV RMS</span>
                  </div>
                ))}
                <div className="divider" style={{ margin: "4px 0" }} />
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>Prótesis · Ottobock bebionic</span>
                  <span className="pill live">Conectada</span>
                </div>
                <div className="row" style={{ justifyContent: "space-between" }}>
                  <span style={{ fontSize: 13, fontWeight: 500 }}>Modelo IA · v2.4.1</span>
                  <span className="pill live">Cargado</span>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">SESSION PREVIEW</div>
                  <h3 style={{ marginTop: 4 }}>Resumen</h3>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  <div style={{ padding: 12, background: "var(--bone-50)", borderRadius: 6 }}>
                    <div className="kicker">DURACIÓN EST.</div>
                    <div className="num" style={{ fontSize: 22, marginTop: 2 }}>{Math.floor(estDuration / 60)}<span className="muted" style={{ fontSize: 13 }}>m</span> {estDuration % 60}<span className="muted" style={{ fontSize: 13 }}>s</span></div>
                  </div>
                  <div style={{ padding: 12, background: "var(--bone-50)", borderRadius: 6 }}>
                    <div className="kicker">MUESTRAS</div>
                    <div className="num" style={{ fontSize: 22, marginTop: 2 }}>{(selected.size * duration * reps * 1000).toLocaleString()}</div>
                  </div>
                </div>
                <div className="muted" style={{ fontSize: 12.5 }}>
                  {selected.size} gestos × {duration}s × {reps} ciclos. Datos guardados en CSV al finalizar.
                </div>
              </div>
              <div style={{ padding: 14, borderTop: "1px solid var(--bone-200)" }}>
                <button className="btn btn-primary btn-block" disabled={!canStart} style={{ padding: "12px 16px", fontSize: 14 }}>
                  <IcPlay size={14} /> Iniciar entrenamiento
                </button>
                {!canStart && <div className="muted" style={{ fontSize: 11.5, marginTop: 8, textAlign: "center" }}>Complete nombre del paciente y seleccione al menos 2 gestos.</div>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

Object.assign(window, { PatientsScreen, StorageScreen, DoctorSessionScreen, PatientSessionScreen, SessionConfigScreen, GestureGlyph });
