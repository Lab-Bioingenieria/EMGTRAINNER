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
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
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
            fill="currentColor" opacity="0.12"/>
          <path d="M0 220 L50 195 L80 240 L110 170 L140 260 L170 185 L200 220 L240 160 L280 250 L320 185 L360 220 L400 168 L440 240 L480 180 L520 225 L560 165 L600 240 L640 185 L680 220 L720 178 L760 230 L800 200 L800 400 L0 400Z"
            fill="currentColor" opacity="0.06"/>
        </svg>
      </div>
    </div>

    <!-- RIGHT: form panel -->
    <div class="login-form-panel">
      
      <div class="login-form-box">
        <!-- Mobile Header (Hidden on Desktop) -->
        <div class="mobile-brand-header">
           <div class="brand-mark-hero">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 12h3l2-7 4 14 3-9 2 5h4"/>
            </svg>
          </div>
          <div class="hero-brand-name">EMGtrainner</div>
        </div>

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
        <transition name="fade">
          <div v-if="error" class="login-error">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
            </svg>
            {{ error }}
          </div>
        </transition>

        <!-- Name (register only) -->
        <transition name="slide-up">
          <div v-if="isRegister" class="field">
            <label>Nombre completo <span class="req">*</span></label>
            <div class="input-wrap">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
              <input v-model="name" placeholder="Tu nombre" class="has-icon" />
            </div>
          </div>
        </transition>

        <!-- Email -->
        <div class="field">
          <label>{{ isRegister ? 'Correo electrónico' : 'Correo' }}</label>
          <div class="input-wrap">
            <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <input v-model="email" type="email" placeholder="tu@correo.com" class="has-icon" />
          </div>
        </div>

        <!-- Password -->
        <div class="field">
          <div class="field-label-row">
            <label>Contraseña</label>
            <a v-if="!isRegister" href="#" class="link-sm">Recuperar →</a>
          </div>
          <div class="input-wrap">
            <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input :type="show ? 'text' : 'password'" v-model="pwd"
              :placeholder="isRegister ? 'Mínimo 8 caracteres' : '••••••••'"
              class="has-icon has-icon-right" />
            <button class="eye-btn" @click="show = !show" type="button" aria-label="Mostrar/Ocultar contraseña">
              <svg v-if="!show" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/>
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
        <transition name="slide-up">
          <div v-if="isRegister" class="field">
            <label>Confirmar contraseña</label>
            <div class="input-wrap">
              <svg class="input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
              <input :type="show ? 'text' : 'password'" v-model="pwd2"
                placeholder="Repite la contraseña" class="has-icon" />
            </div>
            <span v-if="pwd2 && pwd !== pwd2" class="hint danger-text">
              Las contraseñas no coinciden.
            </span>
          </div>
        </transition>

        <!-- Remember me -->
        <label v-if="!isRegister" class="checkbox-label">
          <div class="custom-checkbox">
            <input type="checkbox" checked />
            <span class="checkmark"></span>
          </div>
          <span>Mantener sesión iniciada en este dispositivo</span>
        </label>

        <!-- Terms -->
        <label v-if="isRegister" class="checkbox-label terms-label">
          <div class="custom-checkbox">
            <input type="checkbox" />
            <span class="checkmark"></span>
          </div>
          <span class="terms-text">Acepto el almacenamiento local cifrado de mis datos sEMG e historial clínico.</span>
        </label>

        <!-- Submit -->
        <button class="btn-primary login-submit" :class="{ 'loading': loading }" :disabled="loading" @click="submit">
          <span class="btn-content">
            {{ isRegister ? 'Crear cuenta y continuar' : 'Acceder al sistema' }}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
            </svg>
          </span>
          <span class="spinner" v-if="loading"></span>
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
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:inline; margin-right:4px;">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          Almacenamiento local · AES-256
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Define a modern fallback color palette within the component */
* {
  box-sizing: border-box;
}

.login-shell {
  --primary: #0f172a; /* Slate 900 */
  --primary-hover: #1e293b;
  --focus-ring: rgba(15, 23, 42, 0.15);
  
  --ink: #0f172a;
  --ink-2: #1e293b;
  --ink-3: #334155;
  --ink-4: #64748b;
  
  --paper: #ffffff;
  --bone-50: #f8fafc;
  --bone-100: #f1f5f9;
  --bone-200: #e2e8f0;
  --bone-300: #cbd5e1;
  --bone-400: #94a3b8;
  
  --danger: #ef4444;
  --danger-bg: #fef2f2;
  --warn: #f59e0b;
  --data: #10b981;
  --pulse: #6366f1;
  
  --radius: 12px;
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-serif: 'Playfair Display', Georgia, serif;

  display: grid;
  grid-template-columns: 1fr 1.1fr;
  height: 100vh;
  width: 100vw;
  font-family: var(--font-sans);
  background-color: var(--bone-50);
}

/* ---- HERO ---- */
.login-hero {
  position: relative;
  background: linear-gradient(135deg, #090e17 0%, #1a202c 100%);
  color: #f8fafc;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 48px;
  box-shadow: inset -10px 0 30px rgba(0, 0, 0, 0.3);
}

/* Add a subtle mesh/noise texture overlay to the hero */
.login-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 0;
}

.hero-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  position: relative;
  z-index: 2;
}

.brand-mark-hero {
  width: 36px; height: 36px;
  display: grid; place-items: center;
  background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
  color: var(--ink);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hero-brand-name { font-weight: 700; font-size: 17px; letter-spacing: -0.01em; color: white; }
.hero-brand-sub {
  font-family: var(--font-mono);
  font-size: 10px;
  color: #94a3b8;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-top: 2px;
}

.hero-wave {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 50%;
  color: #f8fafc;
  pointer-events: none;
  z-index: 1;
}
.hero-wave svg { width: 100%; height: 100%; object-fit: cover; object-position: bottom; }

.hero-body {
  margin-top: auto;
  position: relative;
  z-index: 2;
  margin-bottom: 20px;
}

.hero-version {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.15em;
  color: #94a3b8;
  text-transform: uppercase;
  margin-bottom: 20px;
  padding: 4px 10px;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 100px;
  background: rgba(255,255,255,0.03);
}

.hero-heading {
  font-size: 52px;
  line-height: 1.08;
  letter-spacing: -0.02em;
  font-weight: 500;
  max-width: 14ch;
  color: #ffffff;
  margin: 0;
}

.hero-heading em {
  font-family: var(--font-serif);
  font-style: italic;
  font-weight: 400;
  color: #cbd5e1;
}

.hero-sub {
  margin-top: 20px;
  color: #cbd5e1;
  font-size: 16px;
  max-width: 44ch;
  line-height: 1.6;
  font-weight: 300;
}

.hero-stats {
  margin-top: 40px;
  display: flex;
  gap: 48px;
}

.hero-stat-val {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: #ffffff;
}

.hero-stat-unit { font-size: 16px; color: #94a3b8; margin-left: 2px;}
.hero-stat-label {
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 500;
  margin-top: 4px;
}

/* ---- FORM PANEL ---- */
.login-form-panel {
  display: flex;
  flex-direction: column;
  padding: 40px;
  background: var(--bone-50);
  position: relative;
  overflow-y: auto;
}

.mobile-brand-header {
  display: none;
}

.login-form-box {
  margin: auto;
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  background: var(--paper);
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05), 0 0 0 1px rgba(0,0,0,0.02);
}

.login-form-header { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
  margin-bottom: 8px;
}

.kicker {
  font-size: 12px;
  font-weight: 600;
  color: var(--pulse);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin: 0;
  color: var(--ink);
  line-height: 1.2;
}

.login-desc { 
  font-size: 14px; 
  color: var(--ink-4); 
  line-height: 1.5;
  margin: 0;
}

/* Fields */
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  font-size: 13px;
  font-weight: 500;
  color: var(--ink-2);
}

.req { color: var(--danger); }
.hint { font-size: 12px; color: var(--ink-4); margin-top: 4px; }
.danger-text { color: var(--danger); }

/* Input wrappers */
.input-wrap { 
  position: relative; 
  display: flex; 
  align-items: center; 
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--ink-4);
  pointer-events: none;
  transition: color 0.2s ease;
}

input.has-icon { padding-left: 42px; width: 100%; }
input.has-icon-right { padding-right: 42px; }

input {
  padding: 12px 14px;
  background: var(--bone-50);
  border: 1px solid var(--bone-200);
  border-radius: var(--radius);
  font-size: 14px;
  color: var(--ink);
  transition: all 0.2s ease;
  outline: none;
  font-family: inherit;
  width: 100%;
}

input::placeholder {
  color: var(--bone-400);
}

input:hover {
  border-color: var(--bone-300);
}

input:focus {
  background: var(--paper);
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--focus-ring);
}

/* Change icon color on focus */
input:focus ~ .input-icon, 
.input-wrap:focus-within .input-icon {
  color: var(--primary);
}

.eye-btn {
  position: absolute;
  right: 10px;
  padding: 6px;
  color: var(--ink-4);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 6px;
  display: grid;
  place-items: center;
  transition: all 0.2s;
}

.eye-btn:hover {
  background: var(--bone-100);
  color: var(--ink);
}

.field-label-row { display: flex; justify-content: space-between; align-items: center; }

.link-sm { 
  font-size: 12px; 
  font-weight: 500;
  color: var(--primary); 
  text-decoration: none; 
  transition: opacity 0.2s;
}
.link-sm:hover { opacity: 0.8; }

/* strength meter */
.strength-row { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.strength-track { flex: 1; display: flex; gap: 4px; }
.strength-seg { flex: 1; height: 4px; border-radius: 10px; transition: background 0.3s ease; }
.strength-label { font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600;}

/* Checkbox styling */
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--ink-3);
  cursor: pointer;
  user-select: none;
}

.terms-label {
  align-items: flex-start;
}

.terms-text {
  line-height: 1.5;
  margin-top: 2px;
}

.custom-checkbox {
  position: relative;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  margin-top: 2px; /* Alignment fix for terms */
}

.custom-checkbox input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 18px;
  width: 18px;
  background-color: var(--bone-50);
  border: 1px solid var(--bone-300);
  border-radius: 4px;
  transition: all 0.2s;
}

.checkbox-label:hover input ~ .checkmark {
  border-color: var(--primary);
}

.custom-checkbox input:checked ~ .checkmark {
  background-color: var(--primary);
  border-color: var(--primary);
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 6px;
  top: 2px;
  width: 4px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-checkbox input:checked ~ .checkmark:after {
  display: block;
}

/* Submit Button */
.btn-primary {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 14px 20px;
  font-size: 15px;
  font-weight: 600;
  color: white;
  background: var(--ink);
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
  width: 100%;
  position: relative;
  overflow: hidden;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.25);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.15);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.btn-primary.loading .btn-content {
  opacity: 0;
}

/* Spinner */
.spinner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-toggle {
  font-size: 14px;
  color: var(--ink-4);
  text-align: center;
  margin-top: 4px;
}

.link-btn {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  font-size: inherit;
  font-family: inherit;
  padding: 0;
  margin-left: 4px;
  transition: color 0.2s;
}

.link-btn:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.login-footer-note {
  font-size: 11px;
  color: var(--bone-400);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
}

.login-error {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: var(--danger-bg);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  font-size: 13.5px;
  color: var(--danger);
  line-height: 1.4;
}

.login-error svg {
  flex-shrink: 0;
  margin-top: 2px;
}

/* Vue Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active {
  transition: all 0.3s ease;
  max-height: 100px;
  opacity: 1;
  overflow: hidden;
}
.slide-up-enter-from, .slide-up-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: -6px;
}

/* ---- RESPONSIVE DESIGN ---- */
@media (max-width: 992px) {
  .login-shell {
    grid-template-columns: 1fr 1fr;
  }
  .hero-heading {
    font-size: 42px;
  }
}

@media (max-width: 768px) {
  .login-shell { 
    grid-template-columns: 1fr; 
    background-color: var(--paper); /* Seamless background on mobile */
  }
  
  .login-hero { 
    display: none; 
  }
  
  .login-form-panel {
    padding: 24px;
    background: var(--paper);
    align-items: flex-start; /* Move to top on mobile */
    padding-top: 60px;
  }
  
  .login-form-box {
    box-shadow: none; /* Remove card shadow on mobile */
    padding: 0;
    max-width: 100%;
    background: transparent;
  }

  .mobile-brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
  }

  .mobile-brand-header .brand-mark-hero {
    background: var(--ink);
    color: white;
  }

  .mobile-brand-header .hero-brand-name {
    color: var(--ink);
    font-size: 20px;
    font-weight: 700;
  }

  .login-title {
    font-size: 24px;
  }
}
</style>
