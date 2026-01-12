<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import GestureProgress from '../../components/patient/GestureProgress.vue'
import RadialTimer from '../../components/patient/RadialTimer.vue'
import PatientHandVisualization from '../../components/patient/PatientHandVisualization.vue'
import { ALL_GESTURES } from '../../lib/constants'
import type { Gesture } from '../../lib/constants'
import { ChevronRight, Play, ArrowLeft } from 'lucide-vue-next'

const emgSignals = ref([
    { id: 1, status: 'active' }, { id: 2, status: 'active' }, { id: 3, status: 'active' }
])

const step = ref<'setup' | 'training' | 'completed'>('setup')
const patientName = ref('')
const patientAge = ref('')
const selectedGestures = ref<Gesture[]>([])

const gestures = ref<Gesture[]>([])
const currentStep = ref(0)
const isExecuting = ref(false)
const timer = ref(5)
const completedSteps = ref<number[]>([])

const activeSignals = computed(() => emgSignals.value.filter(s => s.status === 'active').length)
const currentGesture = computed(() => gestures.value[currentStep.value])

const toggleGesture = (g: Gesture) => {
    if (selectedGestures.value.find(sel => sel.id === g.id)) {
        selectedGestures.value = selectedGestures.value.filter(sel => sel.id !== g.id)
    } else {
        selectedGestures.value.push(g)
    }
}

const startTraining = () => {
    gestures.value = [...selectedGestures.value]
    step.value = 'training'
    currentStep.value = 0
    completedSteps.value = []
}

let intervalId: number
const startTimer = () => {
    isExecuting.value = true
    timer.value = 5
    intervalId = window.setInterval(() => {
        timer.value--
        if (timer.value <= 0) {
            completeGesture()
        }
    }, 1000)
}

const completeGesture = () => {
    clearInterval(intervalId)
    isExecuting.value = false
    if (!completedSteps.value.includes(currentStep.value)) {
        completedSteps.value.push(currentStep.value)
    }
    
    if (currentStep.value < gestures.value.length - 1) {
        currentStep.value++
        timer.value = 5
    } else {
        step.value = 'completed'
    }
}

const resetSession = () => {
    step.value = 'setup'
    selectedGestures.value = []
    patientName.value = ''
    patientAge.value = ''
}

onUnmounted(() => clearInterval(intervalId))
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Sesión Libre" subtitle="Entrenamiento independiente y exploración" />
    
    <div class="content">
        <!-- SETUP PHASE -->
        <div v-if="step === 'setup'" class="container-sm">
             <div class="mb-6">
                <router-link to="/patient" class="btn-ghost mb-2">
                    <ArrowLeft class="icon-sm mr-2" /> Volver
                </router-link>
             </div>

             <div class="card p-6 mb-6">
                 <div class="flex-row-between mb-4">
                     <h3 class="card-title text-slate-900 font-bold">Configuración de Sesión</h3>
                     <span class="badge badge-neutral">Mode: Free Train</span>
                 </div>
                 <div class="grid-2 gap-4">
                     <div class="field">
                         <label class="label">Nombre del Paciente</label>
                         <input v-model="patientName" placeholder="Opcional" class="input" />
                     </div>
                     <div class="field">
                         <label class="label">Edad</label>
                         <input v-model="patientAge" type="number" placeholder="Opcional" class="input" />
                     </div>
                 </div>
             </div>

             <!-- Gestures -->
             <div class="card p-6 mb-6">
                 <div class="flex-row-between mb-4">
                     <span class="font-bold text-slate-900">Selección de Gestos</span>
                     <span class="badge" :class="selectedGestures.length > 0 ? 'badge-primary' : 'badge-neutral'">
                        {{ selectedGestures.length }} seleccionados
                     </span>
                 </div>
                 <div class="grid-gestures">
                     <div v-for="g in ALL_GESTURES" :key="g.id" 
                          class="gesture-card"
                          :class="{ selected: selectedGestures.find(sel => sel.id === g.id) }"
                          @click="toggleGesture(g)">
                          <span class="font-medium text-sm text-slate-900">{{ g.name }}</span>
                          <span class="text-xs text-slate-500">{{ g.nameEn }}</span>
                     </div>
                 </div>
             </div>

             <!-- Status -->
             <div class="card p-4 flex-row-between mb-6">
                 <div class="flex items-center gap-3">
                     <span class="font-medium text-sm text-slate-700">Estado de Señales</span>
                     <div class="flex gap-1">
                         <div v-for="s in emgSignals" :key="s.id" class="w-2.5 h-2.5 rounded-full" :class="s.status === 'active' ? 'bg-green-500' : 'bg-red-500'"></div>
                     </div>
                 </div>
                 <span class="badge" :class="activeSignals >=3 ? 'badge-success' : 'badge-error'">
                     {{ activeSignals >= 3 ? 'Listo para iniciar' : 'Verificar sensores' }}
                 </span>
             </div>

             <button class="btn btn-primary w-full py-3 justify-center" 
                     :disabled="selectedGestures.length === 0 || activeSignals < 3"
                     @click="startTraining">
                     Iniciar Entrenamiento <ChevronRight class="icon-sm ml-2" />
             </button>
        </div>

        <!-- TRAINING PHASE -->
        <div v-else-if="step === 'training'" class="container-xl w-full">
            <header class="flex-row-between mb-8">
                <div class="flex gap-2">
                    <span class="badge badge-primary">Sesión Libre</span>
                    <span class="badge badge-neutral">Manual</span>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-sm text-slate-500">{{ currentStep + 1 }} / {{ gestures.length }}</span>
                </div>
            </header>

            <GestureProgress :steps="gestures.length" :current-step="currentStep" :completed-steps="completedSteps" class="mb-8" />

            <div class="grid-layout gap-8">
                <div class="card col-main relative p-8 flex flex-col items-center justify-center min-h-[400px]">
                    <div class="text-center mb-8">
                        <h2 class="text-4xl font-bold text-slate-900 mb-2">{{ currentGesture?.name }}</h2>
                        <p class="text-xl text-slate-400">{{ currentGesture?.nameEn }}</p>
                    </div>

                    <div class="flex-center flex-col py-6" v-if="isExecuting">
                        <RadialTimer :time-remaining="timer" :total-time="5" :is-resting="false" />
                        <p class="mt-6 text-lg font-medium text-blue-600">Mantenga la contracción...</p>
                    </div>

                    <div class="flex-center py-6" v-else>
                         <button class="btn-play" @click="startTimer">
                             <Play class="icon-xl ml-1" />
                         </button>
                         <p class="mt-4 text-slate-500 font-medium">Ejecutar Gesto</p>
                    </div>
                </div>

                <div class="col-side card p-4 bg-slate-50 border-slate-200">
                    <PatientHandVisualization :gesture="currentGesture?.name || ''" :is-active="isExecuting" />
                </div>
            </div>
        </div>

        <!-- COMPLETED PHASE -->
        <div v-else class="container-xs">
            <div class="card p-10 text-center">
                 <div class="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                     <span class="text-2xl">✓</span>
                 </div>
                 <h2 class="text-2xl font-bold text-slate-900 mb-3">Sesión Completada</h2>
                 <p class="text-slate-500 mb-8">Ha completado toda la rutina seleccionada.</p>
                 <button class="btn btn-outline w-full" @click="resetSession">Nueva Sesión</button>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; display: flex; flex-direction: column; }
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }
.container-sm { max-width: 800px; margin: 0 auto; width: 100%; }
.container-xs { max-width: 440px; margin: 0 auto; width: 100%; margin-top: 4rem; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.p-6 { padding: 1.5rem; }
.p-8 { padding: 2rem; }
.p-10 { padding: 2.5rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mb-8 { margin-bottom: 2rem; }

/* Grid */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.grid-gestures { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
@media(min-width: 768px) { .grid-gestures { grid-template-columns: repeat(4, 1fr); } }
.grid-layout { display: grid; grid-template-columns: 1fr; }
@media(min-width: 1024px) { .grid-layout { grid-template-columns: 3fr 2fr; } }

/* Inputs & Labels */
.field { display: flex; flex-direction: column; gap: 0.5rem; }
.label { font-size: 0.875rem; font-weight: 500; color: #475569; }
.input { width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; transition: border-color 0.2s; }
.input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

/* Buttons */
.btn { padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; display: inline-flex; align-items: center; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #1e293b; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-ghost { background: transparent; color: #64748b; padding: 0.5rem 0.75rem; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: center; font-size: 0.9rem; }
.btn-ghost:hover { background-color: #f1f5f9; color: #0f172a; }

.btn-play { 
    width: 80px; height: 80px; border-radius: 50%; background-color: #2563eb; color: white; border: none; 
    display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    transition: all 0.2s;
}
.btn-play:hover { transform: scale(1.05); background-color: #1d4ed8; }
.icon-xl { width: 32px; height: 32px; }

/* Gestures */
.gesture-card { text-align: center; padding: 1rem; cursor: pointer; border: 2px solid transparent; background-color: #f8fafc; border-radius: 8px; transition: all 0.2s; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.25rem; }
.gesture-card:hover { background-color: #f1f5f9; }
.gesture-card.selected { border-color: #3b82f6; background-color: #eff6ff; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1); }

/* Badges */
.badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-primary { background-color: #eff6ff; color: #2563eb; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-error { background-color: #fee2e2; color: #dc2626; }

/* Utils */
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.text-slate-900 { color: #0f172a; }
.text-slate-700 { color: #334155; }
.text-slate-500 { color: #64748b; }
.text-blue-600 { color: #2563eb; }
.bg-green-500 { background-color: #22c55e; }
.bg-red-500 { background-color: #ef4444; }

.icon-sm { width: 1.25rem; height: 1.25rem; }
.ml-2 { margin-left: 0.5rem; }
.mr-2 { margin-right: 0.5rem; }
</style>
