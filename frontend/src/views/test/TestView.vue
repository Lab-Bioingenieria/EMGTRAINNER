<script setup lang="ts">
import TopHeader from '../../components/common/TopHeader.vue'
import { ref } from 'vue'
import { 
    Cpu, Activity, Zap, CheckCircle2, AlertTriangle, 
    RefreshCcw, Settings, Terminal
} from 'lucide-vue-next'

const systemStatus = ref([
    { name: "MyoArm Band Device", status: "online", ping: "24ms", version: "v2.1.0" },
    { name: "sEMG Signal Processor", status: "online", ping: "12ms", version: "v1.4.2" },
    { name: "WebSocket Server", status: "online", ping: "45ms", version: "v3.0.1" },
    { name: "ML Inference Engine", status: "idle", load: "0%", version: "v2.4.1" },
])

const calibrationSteps = ref([
    { id: 1, name: "Noise Check", status: "completed", log: "Baseline noise < 5uV" },
    { id: 2, name: "MVC Calibration", status: "completed", log: "Max thresholds updated" },
    { id: 3, name: "Crosstalk Analysis", status: "warning", log: "Detecting channel 3 bleed" },
    { id: 4, name: "System Ready", status: "pending", log: "Waiting for check..." },
])

const isRunningTest = ref(false)

const startTest = () => {
    isRunningTest.value = true
    setTimeout(() => isRunningTest.value = false, 2000)
}
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Pruebas de Sistema" subtitle="Diagnóstico de hardware y software" />
    
    <div class="content">
        <div class="container-xl">
             <div class="grid-dashboard gap-6">
                 <!-- Status Panel -->
                 <div class="col-main">
                      <div class="card p-6 mb-6">
                           <div class="flex-row-between mb-6">
                                <div>
                                    <h2 class="text-lg font-bold text-slate-900">Estado de Componentes</h2>
                                    <p class="text-slate-500 text-sm">Monitoreo en tiempo real de subsistemas</p>
                                </div>
                                <button class="btn btn-primary" @click="startTest" :disabled="isRunningTest">
                                    <RefreshCcw class="icon-sm mr-2" :class="{ 'spin': isRunningTest }" />
                                    {{ isRunningTest ? 'Ejecutando...' : 'Ejecutar Diagnóstico' }}
                                </button>
                           </div>

                           <div class="status-grid">
                                <div v-for="(item, i) in systemStatus" :key="i" class="status-item">
                                     <div class="flex items-center gap-3">
                                          <div class="icon-circle" :class="item.status === 'online' ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-500'">
                                               <Cpu class="icon-sm" />
                                          </div>
                                          <div>
                                              <div class="font-medium text-slate-900">{{ item.name }}</div>
                                              <div class="text-xs text-muted font-mono">{{ item.version }}</div>
                                          </div>
                                     </div>
                                     <div class="flex items-center gap-3">
                                          <span class="badge" :class="item.status === 'online' ? 'badge-success' : 'badge-neutral'">{{ item.status.toUpperCase() }}</span>
                                          <span class="text-xs font-mono text-muted w-12 text-right">{{ item.ping || item.load }}</span>
                                     </div>
                                </div>
                           </div>
                      </div>

                      <div class="card p-6">
                           <h3 class="font-bold text-slate-900 mb-4 flex items-center gap-2">
                               <Activity class="icon-sm text-blue-600" /> Live Signal Preview (Test)
                           </h3>
                           <div class="h-48 bg-slate-50 rounded-lg border border-slate-200 flex-center flex-col text-slate-400">
                                <Activity class="h-8 w-8 mb-2 opacity-50" />
                                <span class="text-sm">Signal canvas would render here</span>
                           </div>
                      </div>
                 </div>

                 <!-- Side Panel -->
                 <div class="col-side flex flex-col gap-6">
                      <!-- Calibration Logs -->
                      <div class="card p-0 overflow-hidden">
                           <div class="p-4 border-b border-slate-100 bg-slate-50/50">
                               <h3 class="font-semibold text-slate-900 flex items-center gap-2">
                                   <Terminal class="icon-sm" /> Logs de Calibración
                               </h3>
                           </div>
                           <div class="divide-y divide-slate-100">
                                <div v-for="step in calibrationSteps" :key="step.id" class="p-4 flex gap-3">
                                     <div class="mt-1">
                                          <CheckCircle2 v-if="step.status === 'completed'" class="icon-sm text-green-500" />
                                          <AlertTriangle v-else-if="step.status === 'warning'" class="icon-sm text-amber-500" />
                                          <div v-else class="w-4 h-4 rounded-full border-2 border-slate-300"></div>
                                     </div>
                                     <div class="flex-1">
                                          <div class="text-sm font-medium text-slate-900">{{ step.name }}</div>
                                          <div class="text-xs text-slate-500 font-mono">{{ step.log }}</div>
                                     </div>
                                </div>
                           </div>
                           <div class="p-3 bg-slate-50 text-center border-t border-slate-100">
                               <button class="text-xs text-blue-600 font-medium hover:underline">Ver logs completos</button>
                           </div>
                      </div>

                      <!-- Control Panel -->
                      <div class="card p-5">
                           <h3 class="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                               <Settings class="icon-sm" /> Configuración Rápida
                           </h3>
                           <div class="space-y-3">
                                <div class="flex items-center justify-between">
                                     <span class="text-sm text-slate-700">Modo Debug</span>
                                     <div class="toggle bg-slate-200 w-10 h-6 rounded-full relative cursor-pointer">
                                         <div class="dot bg-white w-4 h-4 rounded-full absolute top-1 left-1 shadow-sm"></div>
                                     </div>
                                </div>
                                <div class="flex items-center justify-between">
                                     <span class="text-sm text-slate-700">Log Verboso</span>
                                     <div class="toggle bg-blue-600 w-10 h-6 rounded-full relative cursor-pointer">
                                         <div class="dot bg-white w-4 h-4 rounded-full absolute top-1 right-1 shadow-sm"></div>
                                     </div>
                                </div>
                           </div>
                      </div>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.grid-dashboard { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) {
    .grid-dashboard { grid-template-columns: 2fr 1fr; }
}

.status-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; }
@media(min-width: 768px) { .status-grid { grid-template-columns: 1fr 1fr; } }

.status-item { padding: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; background-color: #fcfcfc; }

/* Components */
.icon-circle { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.bg-green-100 { background-color: #dcfce7; }
.text-green-600 { color: #16a34a; }
.text-green-500 { color: #22c55e; }
.text-amber-500 { color: #f59e0b; }
.icon-sm { width: 1.25rem; height: 1.25rem; }
.spin { animation: spin 1s linear infinite; }

.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 500; font-size: 0.9rem; cursor: pointer; border: none; display: flex; align-items: center; transition: all 0.2s; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:disabled { opacity: 0.7; cursor: wait; }

.badge { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; }
.badge-success { background-color: #dcfce7; color: #166534; }
.badge-neutral { background-color: #f1f5f9; color: #64748b; }

.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-center { display: flex; justify-content: center; align-items: center; }
.flex-col { flex-direction: column; }
.mr-2 { margin-right: 0.5rem; }
.mb-6 { margin-bottom: 1.5rem; }
.mt-1 { margin-top: 0.25rem; }

@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
