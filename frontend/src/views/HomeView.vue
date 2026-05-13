<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const modules = [
  {
    id: 'ai', path: '/ai-console',
    tone: 'tone-data',
    title: 'AI Model', italic: 'Console',
    audience: 'Investigadores · Ingenieros',
    desc: 'Métricas, confusion matrix, distribución por clase y versionado de los modelos sEMG.',
    stat: 'v2.4.1 · 91.4%',
    icon: 'brain',
  },
  {
    id: 'doctor', path: '/doctor',
    tone: 'tone-pulse',
    title: 'Sesión', italic: 'Doctor',
    audience: 'Médicos · Fisioterapeutas',
    desc: 'Panel guiado con señales sEMG en vivo, predicción y fatiga muscular.',
    stat: '18 sesiones hoy',
    icon: 'steth',
  },
  {
    id: 'patient', path: '/patient',
    tone: 'tone-signal',
    title: 'Sesión', italic: 'Paciente',
    audience: 'Pacientes',
    desc: 'Interfaz simplificada para uso autónomo, telerehabilitación y feedback visual.',
    stat: '5 conectados ahora',
    icon: 'hand',
  },
  {
    id: 'dashboard', path: '/dashboard',
    tone: 'tone-warn',
    title: 'Panel de', italic: 'Pacientes',
    audience: 'Administración · Clínica',
    desc: 'Vista global del historial, evolución longitudinal y exportación clínica.',
    stat: '124 totales · 89 activos',
    icon: 'users',
  },
]

const iconPaths: Record<string, string> = {
  brain:  '<path d="M9 4a3 3 0 0 0-3 3v.5A2.5 2.5 0 0 0 4 10v.5A2.5 2.5 0 0 0 4 15v.5A2.5 2.5 0 0 0 6 18v.5A2.5 2.5 0 0 0 9 21V4Z"/><path d="M15 4a3 3 0 0 1 3 3v.5A2.5 2.5 0 0 1 20 10v.5A2.5 2.5 0 0 1 20 15v.5A2.5 2.5 0 0 1 18 18v.5A2.5 2.5 0 0 1 15 21V4Z"/>',
  steth:  '<path d="M5 3v6a5 5 0 0 0 10 0V3"/><path d="M5 3h2"/><path d="M13 3h2"/><path d="M10 14v3a4 4 0 0 0 8 0v-1"/><circle cx="18" cy="11" r="2"/>',
  hand:   '<path d="M9 11V5a1.5 1.5 0 0 1 3 0v6"/><path d="M12 11V4a1.5 1.5 0 0 1 3 0v7"/><path d="M15 11V5.5a1.5 1.5 0 0 1 3 0V14"/><path d="M9 11V7a1.5 1.5 0 0 0-3 0v7c0 4 3 7 6 7h1c3 0 5-2.5 5-5"/>',
  users:  '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="8.5" r="3"/><path d="M16 14a5 5 0 0 1 5.5 6"/>',
  db:     '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
  shield: '<path d="M12 3 4 6v6c0 5 4 8 8 9 4-1 8-4 8-9V6l-8-3Z"/>',
  cpu:    '<rect x="5" y="5" width="14" height="14" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
  arrow:  '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
}
</script>

<template>
  <div class="home-page">
    <!-- Topbar -->
    <div class="topbar">
      <div class="topbar-title">
        <div class="crumb">EMGTRAINNER · INICIO</div>
        <h1>Sistema de Entrenamiento sEMG</h1>
      </div>
      <div class="topbar-actions">
        <span class="tag live">
          <span class="dot live" />Sensors · 4ch · 1 kHz
        </span>
      </div>
    </div>

    <!-- Content -->
    <div class="content">
      <!-- Hero strip -->
      <div class="card hero-card">
        <div class="hero-wave-bg">
          <svg viewBox="0 0 1200 180" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M0 90 L60 75 L90 110 L130 55 L170 125 L210 80 L250 100 L290 55 L340 120 L390 75 L440 100 L490 60 L550 115 L610 78 L670 100 L730 55 L790 115 L850 75 L910 100 L970 60 L1030 110 L1090 72 L1150 95 L1200 85 L1200 180 L0 180Z"
              fill="currentColor" opacity="0.06"/>
            <path d="M0 110 L80 85 L120 125 L160 80 L200 120 L250 90 L310 118 L370 82 L430 115 L490 85 L560 118 L630 80 L700 115 L760 88 L830 118 L900 82 L960 118 L1020 85 L1080 118 L1140 82 L1200 105 L1200 180 L0 180Z"
              fill="currentColor" opacity="0.04"/>
          </svg>
        </div>
        <div class="hero-content">
          <div class="kicker">Plataforma clínica</div>
          <h2 class="hero-title">
            Entrenamiento y evaluación de
            <em class="serif">prótesis mioeléctricas</em>.
          </h2>
          <div class="hero-meta">
            <div>
              <span class="kicker">Sensor</span>
              <div class="hero-meta-val">Delsys Trigno · 4 canales</div>
            </div>
            <div>
              <span class="kicker">Modelo activo</span>
              <div class="hero-meta-val">CNN-LSTM v2.4.1</div>
            </div>
            <div>
              <span class="kicker">Última calibración</span>
              <div class="hero-meta-val">Hace 2 días</div>
            </div>
            <div>
              <span class="kicker">Estado</span>
              <div class="hero-meta-val" style="color: oklch(0.42 0.14 155)">● Operativo</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Module grid -->
      <div class="module-grid" style="margin-top: 18px">
        <button
          v-for="m in modules"
          :key="m.id"
          class="module"
          @click="router.push(m.path)"
        >
          <div class="module-head">
            <div :class="['module-icon', m.tone]">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" v-html="iconPaths[m.icon]" />
            </div>
            <span class="pill">{{ m.audience }}</span>
          </div>
          <h2>
            {{ m.title }}
            <em class="serif" style="font-style:italic; color:var(--ink-3)">{{ m.italic }}</em>
          </h2>
          <p class="module-desc">{{ m.desc }}</p>
          <div class="module-foot">
            <span class="module-stat">{{ m.stat }}</span>
            <span class="module-cta">
              Acceder
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" v-html="iconPaths.arrow" />
            </span>
          </div>
        </button>
      </div>

      <!-- Secondary row -->
      <div class="sec-row" style="margin-top: 18px">
        <button class="card sec-card" @click="router.push('/storage')">
          <div class="module-icon tone-data"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" v-html="iconPaths.db" /></div>
          <div>
            <div class="sec-title">Almacenamiento de sesiones</div>
            <div class="muted" style="font-size:12.5px">Historial CSV · 1,247 archivos guardados.</div>
          </div>
        </button>
        <button class="card sec-card" @click="router.push('/login')">
          <div class="module-icon tone-ink"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" v-html="iconPaths.shield" /></div>
          <div>
            <div class="sec-title">Consentimiento y privacidad</div>
            <div class="muted" style="font-size:12.5px">HIPAA + ISO 13485 · Acceso auditable.</div>
          </div>
        </button>
        <button class="card sec-card">
          <div class="module-icon tone-pulse"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" v-html="iconPaths.cpu" /></div>
          <div>
            <div class="sec-title">Configurar prótesis</div>
            <div class="muted" style="font-size:12.5px">Motor, grados de libertad, foto del dispositivo.</div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page { display: flex; flex-direction: column; min-height: 100vh; }
.content { margin: 0 auto; width: 100%; }

.hero-card {
  position: relative;
  padding: 32px 36px 36px;
  overflow: hidden;
  border-radius: 10px;
}

.hero-wave-bg {
  position: absolute;
  inset: 0;
  color: var(--ink-4);
  pointer-events: none;
}
.hero-wave-bg svg { width: 100%; height: 100%; }

.hero-content { position: relative; }

.hero-title {
  font-size: 34px;
  line-height: 1.1;
  letter-spacing: -0.022em;
  font-weight: 400;
  max-width: 20ch;
  margin-top: 6px;
  color: var(--ink);
}

.hero-title em { color: var(--ink-3); }

.hero-meta {
  margin-top: 22px;
  display: flex;
  gap: 28px;
  flex-wrap: wrap;
}
.hero-meta-val { font-weight: 500; margin-top: 2px; font-size: 13.5px; }

.sec-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

.sec-card {
  padding: 18px;
  text-align: left;
  display: flex;
  gap: 14px;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.12s;
}
.sec-card:hover { border-color: var(--ink-3); }

.sec-title { font-weight: 600; font-size: 14px; }
</style>
