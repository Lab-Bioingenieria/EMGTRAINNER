// ============ APP SHELL ============
const SCREENS = [
  { id: "home",        label: "Inicio",            sub: "Panel general",       icon: <IcLayers size={16} />, section: "main" },
  { id: "ai",          label: "AI Model Console",  sub: "Análisis del modelo", icon: <IcBrain size={16} />,  section: "main" },
  { id: "patients",    label: "Panel de Pacientes",sub: "Gestión y monitoreo", icon: <IcUsers size={16} />,  section: "main" },
  { id: "storage",     label: "Almacenamiento",    sub: "Historial CSV",       icon: <IcDB size={16} />,     section: "main" },

  { id: "doctor",      label: "Sesión Doctor",     sub: "Crear protocolos",    icon: <IcSteth size={16} />,  section: "session" },
  { id: "patient",     label: "Sesión Paciente",   sub: "Entrenamiento",       icon: <IcHand size={16} />,   section: "session" },
  { id: "session-config", label: "Configuración",  sub: "TLC · Teacher-Led",   icon: <IcAdjust size={16} />, section: "session" },

  { id: "prosthesis",  label: "Prótesis",          sub: "Motor · DOF · Foto",  icon: <IcCpu size={16} />,    section: "device" },
];

function Sidebar({ current, go, onLogout }) {
  const main    = SCREENS.filter(s => s.section === "main");
  const session = SCREENS.filter(s => s.section === "session");
  const device  = SCREENS.filter(s => s.section === "device");
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark"><IcPulse size={15} color="var(--bone-50)" /></div>
        <div>
          <div className="brand-name">EMGtrainner</div>
          <div className="brand-sub">sEMG · v2.4.1</div>
        </div>
      </div>

      <div className="nav-section">Workspace</div>
      <div className="nav">
        {main.map(s => (
          <button key={s.id} className={`nav-item ${current === s.id ? "active" : ""}`} onClick={() => go(s.id)}>
            <span className="nav-icon">{s.icon}</span>
            <span className="nav-text"><span>{s.label}</span><span className="nav-sub">{s.sub}</span></span>
          </button>
        ))}
      </div>

      <div className="nav-section">Sesión</div>
      <div className="nav">
        {session.map(s => (
          <button key={s.id} className={`nav-item ${current === s.id ? "active" : ""}`} onClick={() => go(s.id)}>
            <span className="nav-icon">{s.icon}</span>
            <span className="nav-text"><span>{s.label}</span><span className="nav-sub">{s.sub}</span></span>
          </button>
        ))}
      </div>

      <div className="nav-section">Dispositivo</div>
      <div className="nav">
        {device.map(s => (
          <button key={s.id} className={`nav-item ${current === s.id ? "active" : ""}`} onClick={() => go(s.id)}>
            <span className="nav-icon">{s.icon}</span>
            <span className="nav-text"><span>{s.label}</span><span className="nav-sub">{s.sub}</span></span>
          </button>
        ))}
      </div>

      <div className="sidebar-foot">
        <div className="device-card">
          <div className="device-row">
            <span className="device-name">Ottobock bebionic</span>
            <span className="dot live" />
          </div>
          <div className="row" style={{ justifyContent: "space-between", fontSize: 11 }}>
            <span className="mono" style={{ color: "var(--ink-4)", letterSpacing: "0.04em" }}>BLDC · 6 DOF</span>
            <span className="mono" style={{ color: "var(--ink-4)" }}>82%</span>
          </div>
          <div className="bar pulse" style={{ height: 4 }}><span style={{ width: "82%" }} /></div>
        </div>
        <button className="nav-item" onClick={onLogout}>
          <span className="nav-icon"><IcLogout size={16} /></span>
          <span className="nav-text"><span>Cerrar sesión</span><span className="nav-sub">Dra. C. Morales</span></span>
        </button>
      </div>
    </aside>
  );
}

function App() {
  const [authed, setAuthed] = React.useState(false);
  const [current, setCurrent] = React.useState("home");

  // tiny URL hash sync
  React.useEffect(() => {
    const onHash = () => {
      const h = location.hash.replace("#", "");
      if (h === "login") setAuthed(false);
      else if (h && SCREENS.find(s => s.id === h)) { setAuthed(true); setCurrent(h); }
    };
    onHash();
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  const go = (id) => {
    setCurrent(id);
    location.hash = id;
  };

  if (!authed) return <LoginScreen onLogin={() => { setAuthed(true); location.hash = "home"; }} />;

  return (
    <div className="shell" data-screen-label={`EMGtrainner · ${current}`}>
      <Sidebar current={current} go={go} onLogout={() => { setAuthed(false); location.hash = "login"; }} />
      <main className="main">
        {current === "home"       && <HomeScreen go={go} />}
        {current === "ai"         && <AIConsoleScreen />}
        {current === "patients"   && <PatientsScreen />}
        {current === "storage"    && <StorageScreen />}
        {current === "doctor"     && <DoctorSessionScreen go={go} />}
        {current === "patient"    && <PatientSessionScreen go={go} />}
        {current === "session-config" && <SessionConfigScreen go={go} />}
        {current === "prosthesis" && <ProsthesisScreen go={go} />}
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
