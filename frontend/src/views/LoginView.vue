<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/auth.service'

const router = useRouter()

const mode  = ref(authService.isLoggedIn() ? 'login' : 'register')
const name  = ref('')
const email = ref('')
const pwd   = ref('')
const pwd2  = ref('')
const show  = ref(false)
const error = ref('')
const loading = ref(false)

const isRegister = computed(() => mode.value === 'register')

const strength = computed(() => {
  let s = 0
  if (pwd.value.length >= 8)           s++
  if (/[A-Z]/.test(pwd.value))         s++
  if (/[0-9]/.test(pwd.value))         s++
  if (/[^A-Za-z0-9]/.test(pwd.value))  s++
  return s
})

const strengthLabel = computed(() => ['—', 'Débil', 'Aceptable', 'Buena', 'Excelente'][strength.value])
const strengthColor = computed(() => [
  'var(--bone-300)', 'var(--danger)', 'var(--warn)', 'var(--data)', 'var(--pulse)'
][strength.value])

async function submit() {
  error.value = ''
  if (isRegister.value && pwd.value !== pwd2.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }
  loading.value = true
  try {
    if (isRegister.value) {
      const username = name.value.trim() || email.value.split('@')[0]
      await authService.register(email.value, pwd.value, username)
    } else {
      await authService.login(email.value, pwd.value)
    }
    router.push('/')
  } catch (e: any) {
    error.value = e.message || 'Error al conectar con el servidor.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-shell">
    <!-- LEFT: hero dark panel -->
    <div class="login-hero">
      <div class="hero-brand">
        <div class="brand-mark-hero">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12h3l2-7 4 14 3-9 2 5h4"/>
          </svg>
        </div>
        <div>
          <div class="hero-brand-name">EMGtrainner</div>
          <div class="hero-brand-sub">sEMG · Personal Device</div>
        </div>
      </div>

      <div class="hero-body">
        <div class="hero-version">v2.4.1 — Release "Cortez"</div>
        <h1 class="hero-heading">
          Entrenamiento <em>mioeléctrico</em> para tu prótesis de mano.
        </h1>
        <p class="hero-sub">
          Dispositivo personal de un solo usuario. Tus señales sEMG, tu modelo, tu historial — todo guardado localmente.
        </p>
        <div class="hero-stats">
          <div class="hero-stat">
            <div class="hero-stat-val">91.4<span class="hero-stat-unit">%</span></div>
            <div class="hero-stat-label">Precisión modelo</div>
          </div>
          <div class="hero-stat">
            <div class="hero-stat-val">7</div>
            <div class="hero-stat-label">Gestos clasificados</div>
          </div>
          <div class="hero-stat">
            <div class="hero-stat-val">4ch</div>
            <div class="hero-stat-label">Sensores sEMG</div>
          </div>
        </div>
      </div>

      <!-- background wave motif -->
      <div class="hero-wave">
        <svg viewBox="0 0 800 400" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 200 L40 180 L60 220 L90 140 L120 260 L150 160 L180 200 L210 130 L240 240 L270 170 L300 200 L330 150 L360 230 L390 160 L420 200 L450 140 L480 250 L510 170 L540 200 L570 145 L600 220 L630 160 L660 200 L690 180 L720 210 L750 165 L800 200 L800 400 L0 400Z"
            fill="currentColor" opacity="0.07"/>
          <path d="M0 220 L50 195 L80 240 L110 170 L140 260 L170 185 L200 220 L240 160 L280 250 L320 185 L360 220 L400 168 L440 240 L480 180 L520 225 L560 165 L600 240 L640 185 L680 220 L720 178 L760 230 L800 200 L800 400 L0 400Z"
            fill="currentColor" opacity="0.05"/>
        </svg>
      </div>
    </div>

    <!-- RIGHT: form panel -->
    <div class="login-form-panel">
      <div class="login-form-box">
        <div class="login-form-header">
          <div class="kicker">{{ isRegister ? 'Configuración inicial' : 'Acceso al dispositivo' }}</div>
          <h2 class="login-title">
            {{ isRegister ? 'Registrar dueño del dispositivo' : 'Iniciar sesión' }}
          </h2>
          <p class="login-desc">
            {{ isRegister
              ? 'Este dispositivo es de uso personal — solo se registra un usuario.'
              : 'Bienvenido de nuevo a tu EMGtrainner.' }}
          </p>
        </div>

        <!-- Error notice -->
        <div v-if="error" class="login-error">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16h.01"/>
          </svg>
          {{ error }}
        </div>

        <!-- Name (register only) -->
        <div v-if="isRegister" class="field">
          <label>Nombre completo <span class="req">*</span></label>
          <div class="input-wrap">
            <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>
            </svg>
            <input v-model="name" placeholder="Tu nombre" class="has-icon" />
          </div>
        </div>

        <!-- Email -->
        <div class="field">
          <label>{{ isRegister ? 'Correo electrónico' : 'Correo' }}</label>
          <div class="input-wrap">
            <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>
            </svg>
            <input v-model="email" placeholder="tu@correo.com" class="has-icon" />
          </div>
        </div>

        <!-- Password -->
        <div class="field">
          <div class="field-label-row">
            <label>Contraseña</label>
            <a v-if="!isRegister" href="#" class="link-sm">Recuperar →</a>
          </div>
          <div class="input-wrap">
            <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 1 1 8 0v4"/>
            </svg>
            <input :type="show ? 'text' : 'password'" v-model="pwd"
              :placeholder="isRegister ? 'Mínimo 8 caracteres' : '••••••••'"
              class="has-icon has-icon-right" />
            <button class="eye-btn" @click="show = !show">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>
          <!-- strength meter -->
          <div v-if="isRegister && pwd" class="strength-row">
            <div class="strength-track">
              <div v-for="i in 4" :key="i" class="strength-seg"
                :style="{ background: i <= strength ? strengthColor : 'var(--bone-200)' }" />
            </div>
            <span class="strength-label mono" :style="{ color: strengthColor }">{{ strengthLabel }}</span>
          </div>
        </div>

        <!-- Confirm password -->
        <div v-if="isRegister" class="field">
          <label>Confirmar contraseña</label>
          <div class="input-wrap">
            <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 1 1 8 0v4"/>
            </svg>
            <input :type="show ? 'text' : 'password'" v-model="pwd2"
              placeholder="Repite la contraseña" class="has-icon" />
          </div>
          <span v-if="pwd2 && pwd !== pwd2" class="hint" style="color: var(--danger)">
            Las contraseñas no coinciden.
          </span>
        </div>

        <!-- Remember me -->
        <label v-if="!isRegister" class="checkbox-label">
          <input type="checkbox" checked />
          Mantener sesión iniciada en este dispositivo
        </label>

        <!-- Terms -->
        <label v-if="isRegister" class="checkbox-label" style="align-items: flex-start;">
          <input type="checkbox" style="margin-top: 3px" />
          <span>Acepto el almacenamiento local cifrado de mis datos sEMG e historial clínico.</span>
        </label>

        <!-- Submit -->
        <button class="btn btn-primary btn-block login-submit" :disabled="loading" @click="submit">
          <span v-if="loading">Conectando…</span>
          <template v-else>
            {{ isRegister ? 'Crear cuenta y continuar' : 'Acceder al sistema' }}
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>
            </svg>
          </template>
        </button>

        <!-- Toggle -->
        <div class="login-toggle">
          <template v-if="isRegister">
            ¿Ya tienes cuenta?
            <button @click="mode = 'login'; error = ''" class="link-btn">Iniciar sesión</button>
          </template>
          <template v-else>
            ¿Primera vez?
            <button @click="mode = 'register'; error = ''" class="link-btn">Crear cuenta</button>
          </template>
        </div>

        <div class="login-footer-note mono">
          Almacenamiento local · AES-256
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-shell {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  height: 100vh;
  width: 100vw;
}

/* ---- HERO ---- */
.login-hero {
  position: relative;
  background: var(--ink);
  color: var(--bone-50);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 40px 48px;
}

.hero-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.brand-mark-hero {
  width: 30px; height: 30px;
  display: grid; place-items: center;
  background: var(--bone-50);
  color: var(--ink);
  border-radius: 6px;
}

.hero-brand-name { font-weight: 600; font-size: 15px; }
.hero-brand-sub {
  font-family: var(--font-mono);
  font-size: 10.5px;
  color: var(--bone-400);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.hero-wave {
  position: absolute;
  inset: 0;
  color: var(--bone-50);
  pointer-events: none;
}
.hero-wave svg { width: 100%; height: 100%; }

.hero-body {
  margin-top: auto;
  position: relative;
  z-index: 1;
}

.hero-version {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.16em;
  color: var(--bone-400);
  text-transform: uppercase;
  margin-bottom: 18px;
}

.hero-heading {
  font-size: 50px;
  line-height: 1.06;
  letter-spacing: -0.024em;
  font-weight: 400;
  max-width: 14ch;
  color: var(--bone-50);
}

.hero-heading em {
  font-family: var(--font-serif);
  font-style: italic;
  font-weight: 400;
  color: var(--bone-200);
}

.hero-sub {
  margin-top: 18px;
  color: var(--bone-300);
  font-size: 15px;
  max-width: 46ch;
  line-height: 1.55;
}

.hero-stats {
  margin-top: 36px;
  display: grid;
  grid-template-columns: repeat(3, auto);
  gap: 36px;
}

.hero-stat-val {
  font-family: var(--font-mono);
  font-size: 30px;
  font-weight: 500;
  letter-spacing: -0.02em;
}

.hero-stat-unit { font-size: 16px; color: var(--bone-400); }
.hero-stat-label {
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--bone-400);
  font-weight: 500;
  margin-top: 2px;
}

/* ---- FORM PANEL ---- */
.login-form-panel {
  display: grid;
  place-items: center;
  padding: 40px;
  background: var(--bone-50);
}

.login-form-box {
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.login-form-header { display: flex; flex-direction: column; gap: 4px; }

.login-title {
  font-size: 26px;
  font-weight: 500;
  letter-spacing: -0.02em;
  margin-top: 6px;
  color: var(--ink);
}

.login-desc { font-size: 13.5px; color: var(--ink-4); }

.login-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bone-100);
  border-radius: 6px;
  font-size: 12.5px;
  color: var(--ink-3);
}

/* Input wrappers */
.input-wrap { position: relative; display: flex; align-items: center; }

.input-icon {
  position: absolute;
  left: 12px;
  color: var(--ink-4);
  pointer-events: none;
}

input.has-icon { padding-left: 36px; width: 100%; }
input.has-icon-right { padding-right: 36px; }

input {
  padding: 9px 12px;
  background: var(--paper);
  border: 1px solid var(--bone-200);
  border-radius: var(--radius);
  font-size: 13px;
  transition: border-color 0.12s, box-shadow 0.12s;
  outline: none;
  font-family: inherit;
  width: 100%;
}

input:focus {
  border-color: var(--ink-3);
  box-shadow: 0 0 0 3px var(--bone-100);
}

.eye-btn {
  position: absolute;
  right: 8px;
  padding: 4px;
  color: var(--ink-4);
  background: none;
  border: none;
  cursor: pointer;
}

.field-label-row { display: flex; justify-content: space-between; align-items: center; }

.link-sm { font-size: 12px; color: var(--ink-4); text-decoration: none; }
.link-sm:hover { color: var(--ink); }

/* strength meter */
.strength-row { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.strength-track { flex: 1; display: flex; gap: 3px; }
.strength-seg { flex: 1; height: 4px; border-radius: 100px; transition: background 0.2s; }
.strength-label { font-size: 10.5px; letter-spacing: 0.06em; text-transform: uppercase; }

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--ink-3);
  cursor: pointer;
}
.checkbox-label input[type="checkbox"] { accent-color: var(--ink); }

.login-submit {
  padding: 12px 16px;
  font-size: 13.5px;
}

.login-toggle {
  font-size: 12.5px;
  color: var(--ink-4);
  text-align: center;
}

.link-btn {
  color: var(--ink);
  font-weight: 500;
  text-decoration: underline;
  background: none;
  border: none;
  cursor: pointer;
  font-size: inherit;
  font-family: inherit;
  padding: 0;
  margin-left: 2px;
}

.login-footer-note {
  font-size: 10.5px;
  color: var(--ink-4);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-align: center;
}

.req { color: var(--signal); }
.hint { font-size: 11px; color: var(--ink-4); font-family: var(--font-mono); }

.login-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--danger) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--danger) 30%, transparent);
  border-radius: 6px;
  font-size: 12.5px;
  color: var(--danger);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .login-shell { grid-template-columns: 1fr; }
  .login-hero  { display: none; }
}
</style>
