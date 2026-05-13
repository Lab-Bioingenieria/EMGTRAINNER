// ============ CHARTS ============
// Custom SVG data viz — no libraries

// Animated EMG-style waveform background
function EMGWave({ height = 60, color = "var(--ink)", opacity = 0.5, speed = 1, seed = 1 }) {
  const [t, setT] = React.useState(0);
  React.useEffect(() => {
    let raf;
    const tick = (ts) => { setT(ts / 1000); raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);
  const W = 600, H = height;
  const N = 240;
  const pts = [];
  for (let i = 0; i < N; i++) {
    const x = (i / (N - 1)) * W;
    const phase = (i / N) * Math.PI * 8 + t * speed + seed;
    // EMG-like: noisy bursts within slow envelope
    const env = 0.5 + 0.5 * Math.sin(phase * 0.4 + seed);
    const burst = Math.sin(phase * 3.2) * 0.6 + Math.sin(phase * 5.7 + 1.3) * 0.3 + (Math.sin(phase * 11.1 + 2) * 0.2);
    const y = H / 2 + burst * env * (H / 2.4);
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return (
    <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" style={{ display: "block", opacity }}>
      <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth="1.2" />
    </svg>
  );
}

// Static decorative wave for cards
function WaveStill({ color = "currentColor", opacity = 0.18, height = 80, seed = 0 }) {
  const W = 400, H = height;
  const N = 180;
  const pts = [];
  for (let i = 0; i < N; i++) {
    const x = (i / (N - 1)) * W;
    const p = (i / N) * Math.PI * 6 + seed;
    const env = 0.4 + 0.6 * Math.sin(p * 0.5 + seed);
    const v = Math.sin(p * 3) * 0.5 + Math.sin(p * 7.3 + 1) * 0.3 + Math.sin(p * 13 + 2) * 0.15;
    pts.push(`${x.toFixed(1)},${(H/2 + v * env * (H/2.2)).toFixed(1)}`);
  }
  return (
    <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" style={{ opacity }}>
      <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth="1" />
    </svg>
  );
}

// KPI sparkline (small line behind a number)
function Sparkline({ values, width = 140, height = 40, color = "var(--ink-3)" }) {
  const max = Math.max(...values), min = Math.min(...values);
  const range = (max - min) || 1;
  const pts = values.map((v, i) => {
    const x = (i / (values.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return (
    <svg width={width} height={height}>
      <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth="1.4" />
    </svg>
  );
}

// Bar chart (Model performance over epochs/months)
function BarChart({ data, height = 280, accent = "var(--ink)" }) {
  const W = 880, H = height;
  const padL = 36, padR = 12, padT = 14, padB = 30;
  const innerW = W - padL - padR, innerH = H - padT - padB;
  const max = Math.max(...data.map(d => d.v));
  const min = 0;
  const yTicks = 5;
  const bw = innerW / data.length * 0.62;
  const step = innerW / data.length;
  return (
    <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      {/* grid */}
      {Array.from({ length: yTicks + 1 }).map((_, i) => {
        const y = padT + (innerH * i) / yTicks;
        const val = max - ((max - min) * i) / yTicks;
        return (
          <g key={i}>
            <line x1={padL} y1={y} x2={W - padR} y2={y} stroke="var(--bone-200)" strokeWidth="1" strokeDasharray={i === yTicks ? "0" : "2 3"} />
            <text x={padL - 6} y={y + 3} textAnchor="end" fontFamily="var(--font-mono)" fontSize="10" fill="var(--ink-4)">{val.toFixed(0)}</text>
          </g>
        );
      })}
      {/* bars */}
      {data.map((d, i) => {
        const h = ((d.v - min) / (max - min)) * innerH;
        const x = padL + step * i + (step - bw) / 2;
        const y = padT + innerH - h;
        return (
          <g key={i}>
            <rect x={x} y={y} width={bw} height={h} rx="2" fill={accent} opacity={d.highlight ? 1 : 0.78} />
            <text x={x + bw / 2} y={H - 10} textAnchor="middle" fontFamily="var(--font-mono)" fontSize="10.5" fill="var(--ink-4)" letterSpacing="0.08em">{d.label}</text>
            <text x={x + bw / 2} y={y - 6} textAnchor="middle" fontFamily="var(--font-mono)" fontSize="10.5" fill="var(--ink-3)" fontWeight="500">{d.v.toFixed(1)}</text>
          </g>
        );
      })}
    </svg>
  );
}

// Line chart (precision over epochs)
function LineChart({ series, height = 280, labels, yMin = 0, yMax = 100, yUnit = "%" }) {
  const W = 880, H = height;
  const padL = 40, padR = 12, padT = 12, padB = 30;
  const innerW = W - padL - padR, innerH = H - padT - padB;
  const yTicks = 5;
  const xPts = (i, n) => padL + (innerW * i) / (n - 1);
  const yPt = v => padT + innerH - ((v - yMin) / (yMax - yMin)) * innerH;
  return (
    <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      {Array.from({ length: yTicks + 1 }).map((_, i) => {
        const y = padT + (innerH * i) / yTicks;
        const val = yMax - ((yMax - yMin) * i) / yTicks;
        return (
          <g key={i}>
            <line x1={padL} y1={y} x2={W - padR} y2={y} stroke="var(--bone-200)" strokeDasharray={i === yTicks ? "0" : "2 3"} />
            <text x={padL - 6} y={y + 3} textAnchor="end" fontFamily="var(--font-mono)" fontSize="10" fill="var(--ink-4)">{val.toFixed(0)}{yUnit}</text>
          </g>
        );
      })}
      {labels && labels.map((l, i) => (
        <text key={i} x={xPts(i, labels.length)} y={H - 10} textAnchor="middle" fontFamily="var(--font-mono)" fontSize="10" fill="var(--ink-4)" letterSpacing="0.06em">{l}</text>
      ))}
      {series.map((s, si) => {
        const pts = s.values.map((v, i) => `${xPts(i, s.values.length)},${yPt(v)}`).join(" ");
        const area = `M ${xPts(0, s.values.length)},${padT + innerH} L ${pts.split(" ").join(" L ")} L ${xPts(s.values.length - 1, s.values.length)},${padT + innerH} Z`;
        return (
          <g key={si}>
            {s.fill && <path d={area} fill={s.color} opacity="0.08" />}
            <polyline points={pts} fill="none" stroke={s.color} strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
            {s.values.map((v, i) => (
              <circle key={i} cx={xPts(i, s.values.length)} cy={yPt(v)} r="3" fill="var(--paper)" stroke={s.color} strokeWidth="1.5" />
            ))}
          </g>
        );
      })}
    </svg>
  );
}

// Confusion matrix
function ConfusionMatrix({ classes, matrix }) {
  const n = classes.length;
  const cell = 52;
  const W = cell * n + 80, H = cell * n + 80;
  const max = Math.max(...matrix.flat());
  return (
    <svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`}>
      {/* Y labels */}
      {classes.map((c, i) => (
        <text key={"y" + i} x={70} y={70 + i * cell + cell / 2 + 4} textAnchor="end" fontFamily="var(--font-mono)" fontSize="11" fill="var(--ink-3)">{c}</text>
      ))}
      {/* X labels */}
      {classes.map((c, i) => (
        <text key={"x" + i} x={80 + i * cell + cell / 2} y={60} textAnchor="middle" fontFamily="var(--font-mono)" fontSize="11" fill="var(--ink-3)">{c}</text>
      ))}
      {/* Axis labels */}
      <text x={20} y={30} fontFamily="var(--font-mono)" fontSize="9.5" fill="var(--ink-4)" letterSpacing="0.1em">PREDICTED →</text>
      <text x={20} y={70 + (n * cell) / 2} fontFamily="var(--font-mono)" fontSize="9.5" fill="var(--ink-4)" letterSpacing="0.1em" transform={`rotate(-90 20 ${70 + (n * cell) / 2})`}>ACTUAL →</text>
      {/* Cells */}
      {matrix.map((row, i) =>
        row.map((v, j) => {
          const intensity = v / max;
          const isDiag = i === j;
          const color = isDiag
            ? `oklch(${0.96 - intensity * 0.45} 0.12 155 / ${0.35 + intensity * 0.65})`
            : `oklch(${0.97 - intensity * 0.25} 0.06 35 / ${0.25 + intensity * 0.5})`;
          return (
            <g key={`${i}-${j}`}>
              <rect x={80 + j * cell} y={70 + i * cell} width={cell - 2} height={cell - 2} rx="3" fill={color} />
              <text x={80 + j * cell + (cell - 2) / 2} y={70 + i * cell + (cell - 2) / 2 + 4} textAnchor="middle"
                fontFamily="var(--font-mono)" fontSize="11" fontWeight={isDiag ? "600" : "400"} fill={intensity > 0.6 ? "var(--ink)" : "var(--ink-3)"}>
                {v}
              </text>
            </g>
          );
        })
      )}
    </svg>
  );
}

// Radar chart
function RadarChart({ axes, series, size = 260 }) {
  const cx = size / 2, cy = size / 2 + 4, r = size / 2 - 36;
  const n = axes.length;
  const angle = i => (-Math.PI / 2) + (i * 2 * Math.PI) / n;
  const ringPoints = (k) =>
    axes.map((_, i) => {
      const x = cx + r * k * Math.cos(angle(i));
      const y = cy + r * k * Math.sin(angle(i));
      return `${x},${y}`;
    }).join(" ");
  return (
    <svg width={size} height={size + 30} viewBox={`0 0 ${size} ${size + 30}`}>
      {[0.25, 0.5, 0.75, 1].map(k => (
        <polygon key={k} points={ringPoints(k)} fill="none" stroke="var(--bone-200)" strokeWidth="1" />
      ))}
      {axes.map((_, i) => {
        const x = cx + r * Math.cos(angle(i));
        const y = cy + r * Math.sin(angle(i));
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="var(--bone-200)" strokeWidth="1" />;
      })}
      {series.map((s, si) => {
        const pts = s.values.map((v, i) => {
          const x = cx + r * v * Math.cos(angle(i));
          const y = cy + r * v * Math.sin(angle(i));
          return `${x},${y}`;
        }).join(" ");
        return (
          <g key={si}>
            <polygon points={pts} fill={s.color} fillOpacity="0.15" stroke={s.color} strokeWidth="1.6" />
            {s.values.map((v, i) => {
              const x = cx + r * v * Math.cos(angle(i));
              const y = cy + r * v * Math.sin(angle(i));
              return <circle key={i} cx={x} cy={y} r="3" fill="var(--paper)" stroke={s.color} strokeWidth="1.5" />;
            })}
          </g>
        );
      })}
      {axes.map((a, i) => {
        const lr = r + 18;
        const x = cx + lr * Math.cos(angle(i));
        const y = cy + lr * Math.sin(angle(i));
        return (
          <text key={i} x={x} y={y + 3} textAnchor="middle" fontFamily="var(--font-mono)" fontSize="10.5" fill="var(--ink-3)" letterSpacing="0.06em">{a.toUpperCase()}</text>
        );
      })}
    </svg>
  );
}

// Class distribution donut/bar
function DistroBars({ data }) {
  const max = Math.max(...data.map(d => d.v));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {data.map(d => (
        <div key={d.label} style={{ display: "grid", gridTemplateColumns: "80px 1fr 56px", gap: 12, alignItems: "center" }}>
          <span style={{ fontSize: 12.5, fontWeight: 500 }}>{d.label}</span>
          <div style={{ height: 14, background: "var(--bone-100)", borderRadius: 4, overflow: "hidden", position: "relative" }}>
            <div style={{ height: "100%", width: `${(d.v / max) * 100}%`, background: d.color || "var(--ink)" }} />
          </div>
          <span className="num" style={{ fontSize: 12, color: "var(--ink-3)", textAlign: "right" }}>{d.v.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}

// Live multi-channel EMG (animated)
function LiveEMG({ channels = 4, height = 220 }) {
  const [t, setT] = React.useState(0);
  React.useEffect(() => {
    let raf;
    const tick = (ts) => { setT(ts / 1000); raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);
  const W = 600;
  const channelH = (height - 20) / channels;
  const colors = ["var(--data)", "var(--signal)", "var(--pulse)", "var(--warn)"];
  return (
    <svg width="100%" height={height} viewBox={`0 0 ${W} ${height}`} preserveAspectRatio="none">
      {Array.from({ length: channels }).map((_, ch) => {
        const baseY = 12 + ch * channelH + channelH / 2;
        const N = 240;
        const pts = [];
        for (let i = 0; i < N; i++) {
          const x = (i / (N - 1)) * W;
          const phase = (i / N) * Math.PI * 10 + t * (1.3 + ch * 0.4) + ch * 1.7;
          const env = 0.3 + 0.7 * Math.abs(Math.sin(phase * 0.3 + ch));
          const v = Math.sin(phase * 4) * 0.5 + Math.sin(phase * 9.1 + 1) * 0.3 + (Math.sin(phase * 17 + 2) * 0.2);
          const y = baseY + v * env * (channelH / 2.6);
          pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
        }
        return (
          <g key={ch}>
            <line x1={0} y1={baseY} x2={W} y2={baseY} stroke="var(--bone-200)" strokeDasharray="2 4" />
            <text x={8} y={baseY - channelH / 2 + 14} fontFamily="var(--font-mono)" fontSize="10" fill="var(--ink-4)" letterSpacing="0.08em">CH{ch + 1}</text>
            <polyline points={pts.join(" ")} fill="none" stroke={colors[ch]} strokeWidth="1.3" />
          </g>
        );
      })}
    </svg>
  );
}

Object.assign(window, {
  EMGWave, WaveStill, Sparkline, BarChart, LineChart, ConfusionMatrix, RadarChart, DistroBars, LiveEMG,
});
