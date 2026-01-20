<script setup lang="ts">
import { ref } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import { 
  User, Calendar, Activity, FileText, ArrowLeft, 
  TrendingUp, Clock, AlertCircle, Edit, Download
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()

// Mock Patient Data
const patient = ref({
    id: "P-2341",
    name: "María González",
    age: 45,
    gender: "Femenino",
    diagnosis: "Amputación Radial Derecha",
    onsetDate: "15 Oct 2023",
    status: "Activo",
    email: "maria.gonzalez@email.com",
    phone: "+593 99 123 4567",
    notes: "Paciente motivada. Presenta buena adaptación al socket. Sensibilidad fantasma moderada."
})

const stats = ref([
    { label: "Sesiones Completadas", value: "12", icon: Calendar, color: "text-blue-600", bg: "bg-blue-50" },
    { label: "Precisión Media", value: "89%", icon: Activity, color: "text-emerald-600", bg: "bg-emerald-50" },
    { label: "Tiempo Total", value: "4h 30m", icon: Clock, color: "text-amber-600", bg: "bg-amber-50" },
    { label: "Tendencia", value: "+15%", icon: TrendingUp, color: "text-indigo-600", bg: "bg-indigo-50" },
])

const recentSessions = ref([
    { id: "S-12", date: "10 Ene 2024", duration: "15 min", score: 92, gestures: 5, notes: "Muy buen control de apertura." },
    { id: "S-11", date: "08 Ene 2024", duration: "20 min", score: 85, gestures: 6, notes: "Fatiga muscular leve." },
    { id: "S-10", date: "05 Ene 2024", duration: "18 min", score: 88, gestures: 5, notes: "Calibración inicial requerida." },
])

const activeTab = ref('overview')
const goBack = () => router.back()
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Detalle de Paciente" subtitle="Expediente clínico individual" />
    
    <div class="content">
        <div class="container-xl">
             <!-- Back Button & Header -->
             <div class="mb-6">
                <button class="btn-ghost mb-2" @click="goBack">
                    <ArrowLeft class="icon-sm mr-2" /> Volver al listado
                </button>
                <div class="flex-row-between">
                    <div class="flex items-center gap-4">
                         <div class="avatar-lg">{{ patient.name.charAt(0) }}</div>
                         <div>
                             <h1 class="text-2xl font-bold text-slate-900">{{ patient.name }}</h1>
                             <div class="flex items-center gap-2 text-muted text-sm">
                                 <span>{{ patient.id }}</span>
                                 <span>•</span>
                                 <span>{{ patient.age }} años</span>
                                 <span class="badge badge-active ml-2">Activo</span>
                             </div>
                         </div>
                    </div>
                    <div class="flex gap-2">
                         <button class="btn btn-outline"><Download class="icon-sm mr-2" /> Exportar</button>
                         <button class="btn btn-primary"><Edit class="icon-sm mr-2" /> Editar</button>
                    </div>
                </div>
             </div>

             <!-- Grid Layout -->
             <div class="grid-dashboard gap-6">
                 <!-- Left Column -->
                 <div class="col-main flex flex-col gap-6">
                      <!-- Stats Grid -->
                      <div class="grid-4 gap-4">
                          <div v-for="(stat, i) in stats" :key="i" class="card p-4">
                               <div class="flex items-start justify-between mb-2">
                                   <div class="icon-box" :class="stat.bg">
                                        <component :is="stat.icon" class="icon-sm" :class="stat.color" />
                                   </div>
                               </div>
                               <div class="text-2xl font-bold text-slate-900">{{ stat.value }}</div>
                               <div class="text-xs text-muted">{{ stat.label }}</div>
                          </div>
                      </div>

                      <!-- History Table -->
                      <div class="card">
                           <div class="card-header border-b border-slate-100 p-4 flex-row-between">
                                <h3 class="font-semibold text-slate-900">Historial de Sesiones</h3>
                                <button class="text-sm text-blue-600 hover:underline">Ver todas</button>
                           </div>
                           <table class="w-full text-sm text-left">
                               <thead class="bg-slate-50 text-slate-500">
                                   <tr>
                                       <th class="p-3 font-medium">Fecha</th>
                                       <th class="p-3 font-medium">Duración</th>
                                       <th class="p-3 font-medium">Gestos</th>
                                       <th class="p-3 font-medium">Puntaje</th>
                                       <th class="p-3 font-medium">Notas</th>
                                   </tr>
                               </thead>
                               <tbody class="divide-y divide-slate-100">
                                   <tr v-for="s in recentSessions" :key="s.id" class="hover:bg-slate-50">
                                       <td class="p-3 text-slate-900 font-medium">{{ s.date }}</td>
                                       <td class="p-3 text-slate-600">{{ s.duration }}</td>
                                       <td class="p-3 text-slate-600">{{ s.gestures }}</td>
                                       <td class="p-3">
                                            <span class="font-semibold" :class="s.score >= 90 ? 'text-green-600' : 'text-blue-600'">{{ s.score }}%</span>
                                       </td>
                                       <td class="p-3 text-slate-500 truncate max-w-xs">{{ s.notes }}</td>
                                   </tr>
                               </tbody>
                           </table>
                      </div>
                 </div>

                 <!-- Right Column -->
                 <div class="col-side flex flex-col gap-6">
                      <!-- Patient Info Card -->
                      <div class="card p-5">
                           <h3 class="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                               <User class="icon-sm text-slate-400" /> Información Personal
                           </h3>
                           <div class="space-y-4 text-sm">
                               <div>
                                   <div class="text-muted text-xs mb-1">Diagnóstico</div>
                                   <div class="font-medium text-slate-900">{{ patient.diagnosis }}</div>
                               </div>
                               <div>
                                   <div class="text-muted text-xs mb-1">Fecha de Inicio</div>
                                   <div class="text-slate-900">{{ patient.onsetDate }}</div>
                               </div>
                               <div class="grid-2 gap-2">
                                    <div>
                                        <div class="text-muted text-xs mb-1">Teléfono</div>
                                        <div class="text-slate-900">{{ patient.phone }}</div>
                                    </div>
                                    <div>
                                        <div class="text-muted text-xs mb-1">Email</div>
                                        <div class="text-slate-900 underline decoration-dotted">{{ patient.email }}</div>
                                    </div>
                               </div>
                           </div>
                      </div>

                      <!-- Notes Card -->
                      <div class="card p-5 bg-amber-50 border-amber-100">
                           <h3 class="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                               <FileText class="icon-sm" /> Notas Clínicas
                           </h3>
                           <p class="text-sm text-amber-800 leading-relaxed">
                               {{ patient.notes }}
                           </p>
                      </div>

                       <div class="card p-5">
                           <h3 class="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                               <AlertCircle class="icon-sm text-slate-400" /> Configuración
                           </h3>
                           <div class="flex flex-col gap-2">
                               <button class="btn-outline w-full justify-center">Calibrar Sensores</button>
                               <button class="btn-outline w-full justify-center text-red-600 border-red-100 hover:bg-red-50">Dar de Baja</button>
                           </div>
                       </div>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Reuse Standard Base */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1280px; margin: 0 auto; width: 100%; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); overflow: hidden; }
.p-4 { padding: 1rem; }
.p-5 { padding: 1.25rem; }

/* Grid System */
.grid-dashboard { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media(min-width: 1024px) {
    .grid-dashboard { grid-template-columns: 2fr 1fr; }
}
.grid-4 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
@media(min-width: 768px) { .grid-4 { grid-template-columns: repeat(4, 1fr); } }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; }

/* Components */
.avatar-lg { width: 64px; height: 64px; background-color: #eff6ff; color: #2563eb; font-size: 1.5rem; font-weight: 700; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 4px solid white; box-shadow: 0 0 0 1px #e2e8f0; }
.btn { padding: 0.5rem 1rem; border-radius: 8px; font-weight: 500; font-size: 0.875rem; cursor: pointer; border: none; display: flex; align-items: center; transition: all 0.2s; }
.btn-ghost { background: transparent; color: #64748b; padding: 0.5rem 0; font-size: 0.9rem; border: none; cursor: pointer; display: flex; align-items: center; }
.btn-ghost:hover { color: #0f172a; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-outline:hover { background-color: #f8fafc; border-color: #cbd5e1; }
.btn-primary { background-color: #0f172a; color: white; }
.btn-primary:hover { background-color: #1e293b; }

.icon-box { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.badge { display: inline-flex; padding: 2px 8px; border-radius: 99px; font-size: 0.75rem; font-weight: 600; }
.badge-active { background-color: #dcfce7; color: #166534; }

/* Typography & Colors */
.text-slate-900 { color: #0f172a; }
.text-slate-500 { color: #64748b; }
.text-slate-400 { color: #94a3b8; }
.text-muted { color: #64748b; }
.bg-amber-50 { background-color: #fffbeb; }
.border-amber-100 { border-color: #fef3c7; }
.text-amber-900 { color: #78350f; }
.text-amber-800 { color: #92400e; }

/* Utils */
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.mr-2 { margin-right: 0.5rem; }
.mb-6 { margin-bottom: 1.5rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.underline { text-decoration: underline; }
.leading-relaxed { line-height: 1.625; }

/* Icons Colors */
.text-blue-600 { color: #2563eb; } .bg-blue-50 { background-color: #eff6ff; }
.text-emerald-600 { color: #059669; } .bg-emerald-50 { background-color: #ecfdf5; }
.text-amber-600 { color: #d97706; }
.text-indigo-600 { color: #4f46e5; } .bg-indigo-50 { background-color: #eef2ff; }

.icon-sm { width: 1.25rem; height: 1.25rem; }
</style>
