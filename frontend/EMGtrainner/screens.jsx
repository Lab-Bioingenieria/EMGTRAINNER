// ============ SHARED UI BITS ============
function Topbar({ crumb, title, actions }) {
  return (
    <div className="topbar">
      <div className="topbar-title">
        <div className="crumb">{crumb}</div>
        <h1>{title}</h1>
      </div>
      <div className="topbar-actions">
        {actions}
        <span className="tag live"><span className="dot live" />Sensors · 4ch · 1 kHz</span>
        <button className="icon-btn" aria-label="settings"><IcSettings /></button>
        <button className="icon-btn" aria-label="user"><IcUser /></button>
      </div>
    </div>
  );
}

function KPI({ kicker, value, unit, delta, deltaDir, meta, spark, sparkColor, accent = "var(--ink)" }) {
  return (
    <div className="kpi">
      <div className="kpi-label">
        <span className="kicker">{kicker}</span>
        <span className="dot" style={{ background: accent }} />
      </div>
      <div className="kpi-value">{value}{unit && <span className="unit">{unit}</span>}</div>
      <div className="kpi-meta">
        {delta && <span className={`delta ${deltaDir === "down" ? "down" : "up"}`}>
          {deltaDir === "down" ? "↓" : "↑"} {delta}
        </span>}
        <span>{meta}</span>
      </div>
      {spark && <div className="kpi-spark"><Sparkline values={spark} color={sparkColor || accent} /></div>}
    </div>
  );
}

// ============ LOGIN ============
function LoginScreen({ onLogin }) {
  // Single-user device: first launch = registro, después = login.
  // Simulamos un "ya registrado" en localStorage para mostrar ambos estados.
  const hasOwner = typeof localStorage !== "undefined" && localStorage.getItem("emgt_owner") === "1";
  const [mode, setMode] = React.useState(hasOwner ? "login" : "register");
  const [name, setName]   = React.useState("");
  const [email, setEmail] = React.useState("");
  const [pwd, setPwd]     = React.useState("");
  const [pwd2, setPwd2]   = React.useState("");
  const [show, setShow]   = React.useState(false);

  const isRegister = mode === "register";

  const submit = () => {
    if (isRegister) {
      try { localStorage.setItem("emgt_owner", "1"); } catch {}
    }
    onLogin();
  };

  // password strength (registration only)
  const strength = (() => {
    let s = 0;
    if (pwd.length >= 8) s++;
    if (/[A-Z]/.test(pwd)) s++;
    if (/[0-9]/.test(pwd)) s++;
    if (/[^A-Za-z0-9]/.test(pwd)) s++;
    return s;
  })();
  const strengthLabel = ["—", "Débil", "Aceptable", "Buena", "Excelente"][strength];
  const strengthColor = ["var(--bone-300)", "var(--danger)", "var(--warn)", "var(--data)", "var(--pulse)"][strength];

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1.05fr 1fr", height: "100vh" }}>
      {/* Left: hero */}
      <div style={{ position: "relative", background: "var(--ink)", color: "var(--bone-50)", overflow: "hidden", display: "flex", flexDirection: "column", padding: "40px 48px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, position: "relative", zIndex: 1 }}>
          <div className="brand-mark" style={{ background: "var(--bone-50)", color: "var(--ink)" }}><IcPulse size={16} /></div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15 }}>EMGtrainner</div>
            <div className="mono" style={{ fontSize: 10.5, color: "var(--bone-400)", letterSpacing: "0.1em", textTransform: "uppercase" }}>sEMG · Personal Device</div>
          </div>
        </div>

        <div style={{ position: "absolute", inset: 0, opacity: 0.18 }}>
          <EMGWave height={window.innerHeight} color="var(--bone-50)" opacity={0.5} speed={0.6} />
        </div>

        <div style={{ marginTop: "auto", position: "relative" }}>
          <div className="mono" style={{ fontSize: 11, letterSpacing: "0.16em", color: "var(--bone-400)", textTransform: "uppercase", marginBottom: 18 }}>v2.4.1 — Release “Cortez”</div>
          <h1 style={{ fontSize: 56, lineHeight: 1.04, letterSpacing: "-0.025em", fontWeight: 400, maxWidth: "14ch" }}>
            Entrenamiento <span className="serif" style={{ fontStyle: "italic", color: "var(--bone-200)" }}>mioeléctrico</span> para tu prótesis de mano.
          </h1>
          <p style={{ marginTop: 18, color: "var(--bone-300)", fontSize: 15, maxWidth: "46ch", lineHeight: 1.55 }}>
            Dispositivo personal de un solo usuario. Tus señales sEMG, tu modelo, tu historial — todo guardado localmente.
          </p>
          <div style={{ marginTop: 36, display: "grid", gridTemplateColumns: "repeat(3, auto)", gap: 36 }}>
            <div>
              <div className="mono" style={{ fontSize: 32, fontWeight: 500, letterSpacing: "-0.02em" }}>91.4<span style={{ fontSize: 16, color: "var(--bone-400)" }}>%</span></div>
              <div className="kicker" style={{ color: "var(--bone-400)" }}>Precisión modelo</div>
            </div>
            <div>
              <div className="mono" style={{ fontSize: 32, fontWeight: 500, letterSpacing: "-0.02em" }}>7</div>
              <div className="kicker" style={{ color: "var(--bone-400)" }}>Gestos clasificados</div>
            </div>
            <div>
              <div className="mono" style={{ fontSize: 32, fontWeight: 500, letterSpacing: "-0.02em" }}>4ch</div>
              <div className="kicker" style={{ color: "var(--bone-400)" }}>Sensores sEMG</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right: form */}
      <div style={{ display: "grid", placeItems: "center", padding: 40, background: "var(--bone-50)" }}>
        <div style={{ width: "100%", maxWidth: 380, display: "flex", flexDirection: "column", gap: 20 }}>
          <div>
            <div className="kicker">{isRegister ? "Configuración inicial" : "Acceso al dispositivo"}</div>
            <h2 style={{ fontSize: 28, fontWeight: 500, letterSpacing: "-0.02em", marginTop: 6 }}>
              {isRegister ? "Registrar dueño del dispositivo" : "Iniciar sesión"}
            </h2>
            <p className="muted" style={{ fontSize: 13.5, marginTop: 4 }}>
              {isRegister
                ? "Este dispositivo es de uso personal — solo se registra un usuario."
                : "Bienvenido de nuevo a tu EMGtrainner."}
            </p>
          </div>

          {/* Single-user notice */}
          <div className="row" style={{ gap: 10, padding: "10px 12px", background: "var(--bone-100)", borderRadius: 6 }}>
            <IcUser size={15} color="var(--ink-3)" />
            <div style={{ fontSize: 12.5, color: "var(--ink-3)" }}>
              Un solo usuario por dispositivo. {hasOwner && <span className="muted">Dueño registrado.</span>}
            </div>
          </div>

          {isRegister && (
            <div className="field">
              <label>Nombre completo <span className="req">*</span></label>
              <div style={{ position: "relative" }}>
                <IcUser size={15} style={{ position: "absolute", left: 12, top: 11, color: "var(--ink-4)" }} />
                <input value={name} onChange={e => setName(e.target.value)} placeholder="Tu nombre" style={{ paddingLeft: 36, width: "100%" }} />
              </div>
            </div>
          )}

          <div className="field">
            <label>{isRegister ? "Correo electrónico" : "Correo"}</label>
            <div style={{ position: "relative" }}>
              <IcMail size={15} style={{ position: "absolute", left: 12, top: 11, color: "var(--ink-4)" }} />
              <input value={email} onChange={e => setEmail(e.target.value)} placeholder="tu@correo.com" style={{ paddingLeft: 36, width: "100%" }} />
            </div>
          </div>

          <div className="field">
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <label>Contraseña</label>
              {!isRegister && <a href="#" style={{ fontSize: 12, color: "var(--ink-4)" }}>Recuperar →</a>}
            </div>
            <div style={{ position: "relative" }}>
              <IcLock size={15} style={{ position: "absolute", left: 12, top: 11, color: "var(--ink-4)" }} />
              <input type={show ? "text" : "password"} value={pwd} onChange={e => setPwd(e.target.value)} placeholder={isRegister ? "Mínimo 8 caracteres" : "••••••••"} style={{ paddingLeft: 36, paddingRight: 36, width: "100%" }} />
              <button onClick={() => setShow(!show)} style={{ position: "absolute", right: 8, top: 8, padding: 4, color: "var(--ink-4)" }}><IcEye size={15} /></button>
            </div>
            {isRegister && pwd && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                <div style={{ flex: 1, height: 4, background: "var(--bone-200)", borderRadius: 100, overflow: "hidden", display: "flex", gap: 2 }}>
                  {[0,1,2,3].map(i => (
                    <div key={i} style={{ flex: 1, background: i < strength ? strengthColor : "transparent" }} />
                  ))}
                </div>
                <span className="mono" style={{ fontSize: 10.5, color: strengthColor, letterSpacing: "0.06em", textTransform: "uppercase" }}>{strengthLabel}</span>
              </div>
            )}
          </div>

          {isRegister && (
            <div className="field">
              <label>Confirmar contraseña</label>
              <div style={{ position: "relative" }}>
                <IcLock size={15} style={{ position: "absolute", left: 12, top: 11, color: "var(--ink-4)" }} />
                <input type={show ? "text" : "password"} value={pwd2} onChange={e => setPwd2(e.target.value)} placeholder="Repite la contraseña" style={{ paddingLeft: 36, width: "100%" }} />
              </div>
              {pwd2 && pwd !== pwd2 && (
                <span className="hint" style={{ color: "var(--danger)" }}>Las contraseñas no coinciden.</span>
              )}
            </div>
          )}

          {!isRegister && (
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12.5, color: "var(--ink-3)" }}>
              <input type="checkbox" defaultChecked /> Mantener sesión iniciada en este dispositivo
            </label>
          )}

          {isRegister && (
            <label style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: 12.5, color: "var(--ink-3)" }}>
              <input type="checkbox" style={{ marginTop: 3 }} />
              <span>Acepto el almacenamiento local cifrado de mis datos sEMG e historial clínico.</span>
            </label>
          )}

          <button className="btn btn-primary btn-block" onClick={submit} style={{ padding: "12px 16px", fontSize: 13.5 }}>
            {isRegister ? "Crear cuenta y continuar" : "Acceder al sistema"} <IcArrow size={15} />
          </button>

          {/* Toggle (no roles, no SSO) */}
          <div style={{ fontSize: 12.5, color: "var(--ink-4)", textAlign: "center" }}>
            {isRegister ? (
              <>¿Ya configuraste este dispositivo? <button onClick={() => setMode("login")} style={{ color: "var(--ink)", fontWeight: 500, textDecoration: "underline" }}>Iniciar sesión</button></>
            ) : (
              !hasOwner && <>¿Primera vez? <button onClick={() => setMode("register")} style={{ color: "var(--ink)", fontWeight: 500, textDecoration: "underline" }}>Registrar dueño</button></>
            )}
          </div>

          <div className="mono" style={{ fontSize: 10.5, color: "var(--ink-4)", letterSpacing: "0.08em", textTransform: "uppercase", textAlign: "center", marginTop: 2 }}>
            Almacenamiento local · AES-256
          </div>
        </div>
      </div>
    </div>
  );
}

// ============ HOME ============
function HomeScreen({ go }) {
  const modules = [
    { id: "ai",      icon: <IcBrain size={20} />, tone: "tone-data", title: "AI Model", italic: "Console",
      audience: "Investigadores · Ingenieros",
      desc: "Métricas, confusion matrix, distribución por clase y versionado de los modelos sEMG.",
      stat: "v2.4.1 · 91.4%", seed: 1 },
    { id: "doctor",  icon: <IcSteth size={20} />, tone: "tone-pulse", title: "Sesión", italic: "Doctor",
      audience: "Médicos · Fisioterapeutas",
      desc: "Panel guiado con señales sEMG en vivo, predicción y fatiga muscular.",
      stat: "18 sesiones hoy", seed: 2 },
    { id: "patient", icon: <IcHand size={20} />, tone: "tone-signal", title: "Sesión", italic: "Paciente",
      audience: "Pacientes",
      desc: "Interfaz simplificada para uso autónomo, telerehabilitación y feedback visual.",
      stat: "5 conectados ahora", seed: 3 },
    { id: "patients",icon: <IcUsers size={20} />, tone: "tone-warn", title: "Panel de", italic: "Pacientes",
      audience: "Administración · Clínica",
      desc: "Vista global del historial, evolución longitudinal y exportación clínica.",
      stat: "124 totales · 89 activos", seed: 4 },
  ];
  return (
    <>
      <Topbar crumb="EMGTRAINNER · INICIO" title="Sistema de Entrenamiento sEMG" />
      <div className="content">
        {/* Hero strip */}
        <div className="card" style={{ position: "relative", padding: "32px 36px 36px", overflow: "hidden", borderRadius: 10 }}>
          <div style={{ position: "absolute", inset: 0, opacity: 0.5 }}>
            <EMGWave height={260} color="var(--ink-4)" opacity={0.22} speed={0.4} />
          </div>
          <div style={{ position: "relative" }}>
            <div className="kicker">Plataforma clínica</div>
            <h2 style={{ fontSize: 36, lineHeight: 1.1, letterSpacing: "-0.022em", fontWeight: 400, maxWidth: "18ch", marginTop: 6 }}>
              Entrenamiento y evaluación de <span className="serif" style={{ fontStyle: "italic" }}>prótesis mioeléctricas</span>.
            </h2>
            <div style={{ marginTop: 22, display: "flex", gap: 28, flexWrap: "wrap" }}>
              <div><span className="kicker">Sensor</span><div style={{ fontWeight: 500, marginTop: 2 }}>Delsys Trigno · 4 canales</div></div>
              <div><span className="kicker">Modelo activo</span><div style={{ fontWeight: 500, marginTop: 2 }}>CNN-LSTM v2.4.1</div></div>
              <div><span className="kicker">Última calibración</span><div style={{ fontWeight: 500, marginTop: 2 }}>Hace 2 días</div></div>
              <div><span className="kicker">Estado</span><div style={{ fontWeight: 500, marginTop: 2, color: "oklch(0.42 0.14 155)" }}>● Operativo</div></div>
            </div>
          </div>
        </div>

        {/* Module grid */}
        <div className="module-grid" style={{ marginTop: 18 }}>
          {modules.map(m => (
            <button key={m.id} className="module" onClick={() => go(m.id)}>
              <div className="module-bg"><WaveStill color="currentColor" opacity={0.12} height={140} seed={m.seed} /></div>
              <div className="module-head">
                <div className={`module-icon ${m.tone}`}>{m.icon}</div>
                <span className="pill">{m.audience}</span>
              </div>
              <h2>{m.title} <span className="serif" style={{ fontStyle: "italic", color: "var(--ink-3)" }}>{m.italic}</span></h2>
              <p className="module-desc">{m.desc}</p>
              <div className="module-foot">
                <span className="module-stat">{m.stat}</span>
                <span className="module-cta">Acceder <IcArrow size={14} /></span>
              </div>
            </button>
          ))}
        </div>

        {/* Secondary row */}
        <div style={{ marginTop: 18, display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
          <button className="card" onClick={() => go("prosthesis")} style={{ padding: 18, textAlign: "left", display: "flex", gap: 14, alignItems: "center", cursor: "pointer" }}>
            <div className="module-icon tone-ink"><IcCpu size={18} /></div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>Configurar prótesis</div>
              <div className="muted" style={{ fontSize: 12.5 }}>Motor, grados de libertad, foto del dispositivo.</div>
            </div>
          </button>
          <button className="card" onClick={() => go("storage")} style={{ padding: 18, textAlign: "left", display: "flex", gap: 14, alignItems: "center", cursor: "pointer" }}>
            <div className="module-icon tone-data"><IcDB size={18} /></div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>Almacenamiento de sesiones</div>
              <div className="muted" style={{ fontSize: 12.5 }}>Historial CSV · 1,247 archivos guardados.</div>
            </div>
          </button>
          <button className="card" style={{ padding: 18, textAlign: "left", display: "flex", gap: 14, alignItems: "center", cursor: "pointer" }}>
            <div className="module-icon tone-pulse"><IcShield size={18} /></div>
            <div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>Consentimiento y privacidad</div>
              <div className="muted" style={{ fontSize: 12.5 }}>HIPAA + ISO 13485 · Acceso auditable.</div>
            </div>
          </button>
        </div>
      </div>
    </>
  );
}

// ============ AI MODEL CONSOLE ============
function AIConsoleScreen() {
  const [tab, setTab] = React.useState("metrics");
  const monthData = [
    { label: "ENE", v: 78.2 }, { label: "FEB", v: 81.0 }, { label: "MAR", v: 79.8 },
    { label: "ABR", v: 85.4 }, { label: "MAY", v: 88.7, highlight: false }, { label: "JUN", v: 87.1 }, { label: "JUL", v: 91.4, highlight: true },
  ];
  const classes = ["Open", "Close", "Pinch", "Cyl.", "Sphere", "Wave", "Point"];
  const matrix = [
    [428,  4,   2,   1,   3,   8,   2],
    [  3, 391,  6,   2,   1,   4,   9],
    [  2,   5, 372,  9,   4,   1,   2],
    [  1,   3,  11, 388,  7,   2,   1],
    [  4,   1,   3,   8, 401,  3,   2],
    [  9,   2,   1,   2,   3, 376,  4],
    [  3,   8,   2,   1,   2,   5, 412],
  ];
  return (
    <>
      <Topbar crumb="MÓDULO · AI MODEL CONSOLE" title="AI Model Console"
        actions={<button className="btn btn-ghost"><IcUp size={14} /> Importar dataset</button>} />
      <div className="content">
        <div className="grid-4">
          <KPI kicker="PRECISIÓN GLOBAL" value="91.4" unit="%" delta="+2.3" deltaDir="up"
            meta="vs. v2.4.0" spark={[78,81,79,85,88,87,91]} sparkColor="var(--ink)" />
          <KPI kicker="F1 PROMEDIO" value="0.92" delta="+0.04" deltaDir="up"
            meta="macro · 7 clases" spark={[0.82,0.84,0.83,0.86,0.88,0.89,0.92]} accent="var(--data)" sparkColor="var(--data)" />
          <KPI kicker="DATASET" value="52,891" delta="843" deltaDir="up"
            meta="muestras válidas" accent="var(--pulse)" />
          <KPI kicker="VERSIÓN ACTIVA" value="v2.4.1" meta="entrenado hace 3 días" accent="var(--signal)" />
        </div>

        <div className="tabs" style={{ marginTop: 22 }}>
          {[
            { id: "metrics", label: "Métricas" },
            { id: "confusion", label: "Confusion matrix" },
            { id: "distribution", label: "Distribución" },
            { id: "sessions", label: "Sesiones", count: "1,247" },
            { id: "versions", label: "Versiones", count: "8" },
          ].map(t => (
            <button key={t.id} className={`tab ${tab === t.id ? "active" : ""}`} onClick={() => setTab(t.id)}>
              {t.label} {t.count && <span className="count">· {t.count}</span>}
            </button>
          ))}
        </div>

        {tab === "metrics" && (
          <div className="grid-2-3" style={{ marginTop: 18 }}>
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">CHART · ACCURACY OVER TIME</div>
                  <h3 style={{ marginTop: 4 }}>Rendimiento del modelo</h3>
                  <p>Precisión global por mes de entrenamiento, validación cruzada 5-fold.</p>
                </div>
                <div className="toggle">
                  <button className="active">Precisión</button>
                  <button>Loss</button>
                  <button>F1</button>
                </div>
              </div>
              <div className="card-body">
                <BarChart data={monthData} />
              </div>
            </div>

            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">PER-CLASS</div>
                  <h3 style={{ marginTop: 4 }}>Métricas por gesto</h3>
                </div>
              </div>
              <div className="card-body">
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  {[
                    { g: "Open",   p: 96, c: "var(--pulse)" },
                    { g: "Close",  p: 94, c: "var(--pulse)" },
                    { g: "Pinch",  p: 89, c: "var(--data)" },
                    { g: "Cyl.",   p: 91, c: "var(--pulse)" },
                    { g: "Sphere", p: 93, c: "var(--pulse)" },
                    { g: "Wave",   p: 87, c: "var(--warn)" },
                    { g: "Point",  p: 95, c: "var(--pulse)" },
                  ].map(r => (
                    <div key={r.g} style={{ display: "grid", gridTemplateColumns: "70px 1fr 44px", gap: 10, alignItems: "center" }}>
                      <span style={{ fontWeight: 500, fontSize: 13 }}>{r.g}</span>
                      <div className="bar"><span style={{ width: `${r.p}%`, background: r.c }} /></div>
                      <span className="num" style={{ fontSize: 12, textAlign: "right" }}>{r.p}%</span>
                    </div>
                  ))}
                </div>
                <div className="divider" style={{ margin: "16px 0" }} />
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <div>
                    <div className="kicker">Inference latency</div>
                    <div className="num" style={{ fontSize: 22, marginTop: 2 }}>14.3 <span className="muted" style={{ fontSize: 13 }}>ms</span></div>
                  </div>
                  <div>
                    <div className="kicker">Model size</div>
                    <div className="num" style={{ fontSize: 22, marginTop: 2 }}>2.7 <span className="muted" style={{ fontSize: 13 }}>MB</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {tab === "confusion" && (
          <div className="grid-2-3" style={{ marginTop: 18 }}>
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">7×7 · NORMALIZED COUNTS</div>
                  <h3 style={{ marginTop: 4 }}>Confusion matrix</h3>
                  <p>Predicción vs. clase real, validation set 5,288 muestras.</p>
                </div>
              </div>
              <div className="card-body" style={{ overflow: "auto" }}>
                <ConfusionMatrix classes={classes} matrix={matrix} />
              </div>
            </div>
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">Insights</div>
                  <h3 style={{ marginTop: 4 }}>Confusiones notables</h3>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {[
                  { a: "Pinch → Cyl.", v: "2.4%", note: "Activación FDP similar entre presa fina y cilíndrica." },
                  { a: "Wave → Open", v: "2.3%", note: "Onda dorsal con extensión completa de dedos." },
                  { a: "Close → Point", v: "2.2%", note: "Flexión parcial del índice ambigua." },
                ].map(r => (
                  <div key={r.a} style={{ display: "flex", flexDirection: "column", gap: 4, padding: 12, background: "var(--bone-50)", borderRadius: 6 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span className="mono" style={{ fontSize: 12, fontWeight: 500 }}>{r.a}</span>
                      <span className="pill warn">{r.v}</span>
                    </div>
                    <span className="muted" style={{ fontSize: 12 }}>{r.note}</span>
                  </div>
                ))}
                <button className="btn btn-ghost btn-block" style={{ marginTop: 4 }}>
                  <IcRefresh size={14} /> Reentrenar con sesiones recientes (843)
                </button>
              </div>
            </div>
          </div>
        )}

        {tab === "distribution" && (
          <div className="grid-2-3" style={{ marginTop: 18 }}>
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">CLASS BALANCE</div>
                  <h3 style={{ marginTop: 4 }}>Distribución por gesto</h3>
                </div>
              </div>
              <div className="card-body">
                <DistroBars data={[
                  { label: "Open",   v: 8420, color: "var(--ink)" },
                  { label: "Close",  v: 8104, color: "var(--ink)" },
                  { label: "Pinch",  v: 6982, color: "var(--data)" },
                  { label: "Cyl.",   v: 7301, color: "var(--data)" },
                  { label: "Sphere", v: 7544, color: "var(--ink)" },
                  { label: "Wave",   v: 6810, color: "var(--warn)" },
                  { label: "Point",  v: 7730, color: "var(--ink)" },
                ]} />
                <div className="divider" style={{ margin: "16px 0" }} />
                <div className="row" style={{ gap: 16 }}>
                  <span className="mono" style={{ fontSize: 12 }}>Balance: <strong>0.94</strong></span>
                  <span className="mono" style={{ fontSize: 12, color: "var(--ink-4)" }}>Desviación máx: 9.5%</span>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="card-head">
                <div>
                  <div className="kicker">DATASET STRUCTURE</div>
                  <h3 style={{ marginTop: 4 }}>Composición</h3>
                </div>
              </div>
              <div className="card-body" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                {[
                  ["Train",       "70%", "37,024", "var(--ink)"],
                  ["Validation",  "15%", "7,933",  "var(--data)"],
                  ["Test",        "15%", "7,934",  "var(--signal)"],
                ].map(([l, p, n, c]) => (
                  <div key={l} style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 12, alignItems: "center" }}>
                    <span style={{ display: "inline-block", width: 8, height: 24, borderRadius: 2, background: c }} />
                    <div>
                      <div style={{ fontWeight: 500, fontSize: 13 }}>{l}</div>
                      <div className="muted" style={{ fontSize: 11.5 }}>{n} muestras</div>
                    </div>
                    <span className="num" style={{ fontSize: 18 }}>{p}</span>
                  </div>
                ))}
                <div className="divider" />
                <div className="muted" style={{ fontSize: 12 }}>Augmentation: jitter ±5%, time warp, channel dropout 10%.</div>
              </div>
            </div>
          </div>
        )}

        {tab === "sessions" && <SessionsTab />}
        {tab === "versions" && <VersionsTab />}
      </div>
    </>
  );
}

function SessionsTab() {
  const sessions = [
    ["S-1247", "María González",   "TLC",  "2026-05-12 14:22", "Open, Close, Pinch",       "4m 12s", "validated"],
    ["S-1246", "Carlos Rodríguez", "LLC",  "2026-05-12 11:08", "All 7 gestures",            "6m 02s", "validated"],
    ["S-1245", "Ana Martínez",     "TLC",  "2026-05-11 16:40", "Cylindrical, Spherical",    "3m 48s", "pending"],
    ["S-1244", "Luis Fernández",   "Free", "2026-05-11 09:15", "Wave, Point",               "8m 22s", "discarded"],
    ["S-1243", "Elena Sánchez",    "TLC",  "2026-05-10 18:03", "All 7 gestures",            "5m 31s", "validated"],
    ["S-1242", "Roberto López",    "LLC",  "2026-05-10 14:55", "Open, Close",               "2m 18s", "validated"],
  ];
  const statusMap = { validated: ["live", "Validada"], pending: ["warn", "Revisar"], discarded: ["off", "Descartada"] };
  return (
    <div className="card" style={{ marginTop: 18 }}>
      <div className="card-head">
        <div>
          <div className="kicker">RECENT SESSIONS</div>
          <h3 style={{ marginTop: 4 }}>Sesiones de entrenamiento</h3>
        </div>
        <div className="row">
          <div className="search" style={{ width: 240 }}>
            <IcSearch size={14} />
            <input placeholder="Buscar sesión, paciente, gesto…" />
          </div>
          <button className="btn btn-ghost"><IcDl size={14} /> CSV</button>
        </div>
      </div>
      <div className="card-body flush">
        <table className="tbl">
          <thead>
            <tr>
              <th>Session ID</th><th>Paciente</th><th>Modo</th><th>Timestamp</th><th>Gestos</th><th>Duración</th><th>Estado</th><th />
            </tr>
          </thead>
          <tbody>
            {sessions.map(s => {
              const [pillTone, pillLabel] = statusMap[s[6]];
              return (
                <tr key={s[0]}>
                  <td className="mono" style={{ fontSize: 12.5 }}>{s[0]}</td>
                  <td style={{ fontWeight: 500 }}>{s[1]}</td>
                  <td><span className="pill">{s[2]}</span></td>
                  <td className="mono muted" style={{ fontSize: 12 }}>{s[3]}</td>
                  <td className="muted">{s[4]}</td>
                  <td className="mono">{s[5]}</td>
                  <td><span className={`pill ${pillTone}`}>{pillLabel}</span></td>
                  <td style={{ textAlign: "right" }}><button className="icon-btn"><IcMore size={16} /></button></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function VersionsTab() {
  const versions = [
    ["v2.4.1", "Cortez",      "2026-05-09", "91.4%", "+843 sessions, regularization tuned", true],
    ["v2.4.0", "Bering",      "2026-04-22", "89.1%", "Channel dropout, augmentation pass",  false],
    ["v2.3.2", "Atacama",     "2026-03-30", "87.8%", "Pinch class rebalanced",              false],
    ["v2.3.0", "Patagonia",   "2026-03-04", "85.4%", "Switched to CNN-LSTM backbone",       false],
    ["v2.2.1", "Andes",       "2026-02-14", "82.1%", "Initial 7-class release",             false],
  ];
  return (
    <div className="card" style={{ marginTop: 18 }}>
      <div className="card-head">
        <div>
          <div className="kicker">VERSION HISTORY</div>
          <h3 style={{ marginTop: 4 }}>Modelos entrenados</h3>
        </div>
        <button className="btn btn-primary"><IcGit size={14} /> Crear nueva versión</button>
      </div>
      <div className="card-body flush">
        <table className="tbl">
          <thead>
            <tr><th>Versión</th><th>Codename</th><th>Fecha</th><th>Accuracy</th><th>Notas</th><th>Estado</th></tr>
          </thead>
          <tbody>
            {versions.map(v => (
              <tr key={v[0]}>
                <td className="mono" style={{ fontWeight: 600 }}>{v[0]}</td>
                <td className="serif" style={{ fontStyle: "italic", fontSize: 14 }}>{v[1]}</td>
                <td className="mono muted">{v[2]}</td>
                <td className="mono" style={{ fontWeight: 500 }}>{v[3]}</td>
                <td className="muted">{v[4]}</td>
                <td>{v[5] ? <span className="pill live">Activa</span> : <span className="pill">Archivada</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

Object.assign(window, { Topbar, KPI, LoginScreen, HomeScreen, AIConsoleScreen });
