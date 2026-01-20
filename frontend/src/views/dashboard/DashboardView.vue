<script setup lang="ts">
import { ref, computed } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import PatientProgressChart from '../../components/dashboard/PatientProgressChart.vue'
import GestureComparisonChart from '../../components/dashboard/GestureComparisonChart.vue'
import { 
  Users, TrendingUp, Calendar, Activity, Search, 
  Download, ChevronRight 
} from 'lucide-vue-next'
import type { Patient } from '../../types/patient'

// Data
const patients: Patient[] = [
  {
    id: "P-2341",
    name: "María González",
    age: 45,
    sessions: 12,
    lastSession: "2024-01-10",
    progress: 89,
    status: "active",
  },
  {
    id: "P-1892",
    name: "Carlos Rodríguez",
    age: 38,
    sessions: 8,
    lastSession: "2024-01-10",
    progress: 76,
    status: "active",
  },
  {
    id: "P-3021",
    name: "Ana Martínez",
    age: 52,
    sessions: 15,
    lastSession: "2024-01-09",
    progress: 94,
    status: "active",
  },
  {
    id: "P-4156",
    name: "Luis Fernández",
    age: 41,
    sessions: 5,
    lastSession: "2024-01-08",
    progress: 62,
    status: "inactive",
  },
  {
    id: "P-5234",
    name: "Elena Sánchez",
    age: 35,
    sessions: 20,
    lastSession: "2024-01-07",
    progress: 97,
    status: "completed",
  },
  {
    id: "P-6789",
    name: "Roberto López",
    age: 48,
    sessions: 3,
    lastSession: "2024-01-05",
    progress: 45,
    status: "active",
  },
]

// State
const selectedPatient = ref<string | null>(null)
const searchQuery = ref("")
const statusFilter = ref("all")

// Computed
const filteredPatients = computed(() => {
  return patients.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          p.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesStatus = statusFilter.value === 'all' || p.status === statusFilter.value
    
    return matchesSearch && matchesStatus
  })
})

// Helpers
const getInitials = (name: string) => name.split(" ").map((n) => n[0]).join("")
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Panel de Pacientes" subtitle="Gestión global y seguimiento longitudinal" />

    <div class="content">
      <!-- KPI Grid -->
      <div class="kpi-grid">
        <div class="card kpi-card">
          <div class="card-header-flex">
             <span class="card-title-sm">Pacientes Totales</span>
             <Users class="icon-sm text-primary" />
          </div>
          <div class="card-content">
             <div class="metric-value">124</div>
             <p class="metric-sub text-success">
                <TrendingUp class="icon-xs" /> +8 este mes
             </p>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="card-header-flex">
             <span class="card-title-sm">Sesiones Hoy</span>
             <Calendar class="icon-sm text-chart-2" />
          </div>
          <div class="card-content">
             <div class="metric-value">18</div>
             <p class="metric-sub">5 en progreso</p>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="card-header-flex">
             <span class="card-title-sm">Progreso Promedio</span>
             <TrendingUp class="icon-sm text-chart-4" />
          </div>
          <div class="card-content">
             <div class="metric-value">78%</div>
             <p class="metric-sub">+5% vs. mes anterior</p>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="card-header-flex">
             <span class="card-title-sm">Pacientes Activos</span>
             <Activity class="icon-sm text-success" />
          </div>
          <div class="card-content">
             <div class="metric-value">89</div>
             <p class="metric-sub">72% del total</p>
          </div>
        </div>
      </div>

      <!-- Main Grid -->
      <div class="dashboard-grid">
        <!-- Patient List Column -->
        <div class="main-column">
           <div class="card">
              <div class="card-header-row">
                 <div>
                    <h3 class="card-title">Listado de Pacientes</h3>
                    <p class="card-desc">Gestión y seguimiento de todos los pacientes</p>
                 </div>
                 <div class="filters-row">
                    <div class="search-wrapper">
                       <Search class="search-icon" />
                       <input v-model="searchQuery" placeholder="Buscar paciente..." class="search-input" />
                    </div>
                    <select v-model="statusFilter" class="select-input">
                       <option value="all">Todos</option>
                       <option value="active">Activos</option>
                       <option value="inactive">Inactivos</option>
                       <option value="completed">Completados</option>
                    </select>
                    <button class="btn-icon"><Download class="icon-sm" /></button>
                 </div>
              </div>

              <div class="table-container">
                 <table class="patient-table">
                    <thead>
                       <tr>
                          <th>Paciente</th>
                          <th>Sesiones</th>
                          <th>Última Sesión</th>
                          <th>Progreso</th>
                          <th>Estado</th>
                          <th></th>
                       </tr>
                    </thead>
                    <tbody>
                       <tr v-for="patient in filteredPatients" 
                           :key="patient.id"
                           class="clickable-row"
                           :class="{ selected: selectedPatient === patient.id }"
                           @click="selectedPatient = patient.id"
                       >
                          <td>
                             <div class="patient-info">
                                <div class="avatar">
                                   {{ getInitials(patient.name) }}
                                </div>
                                <div>
                                   <p class="patient-name">{{ patient.name }}</p>
                                   <p class="patient-meta">{{ patient.id }} • {{ patient.age }} años</p>
                                </div>
                             </div>
                          </td>
                          <td>{{ patient.sessions }}</td>
                          <td>{{ patient.lastSession }}</td>
                          <td>
                             <div class="progress-cell">
                                <div class="progress-track">
                                   <div class="progress-fill" :style="{ width: patient.progress + '%' }"></div>
                                </div>
                                <span class="progress-text">{{ patient.progress }}%</span>
                             </div>
                          </td>
                          <td>
                             <span class="badge" :class="'badge-' + patient.status">
                                {{ patient.status === 'active' ? 'Activo' : patient.status === 'completed' ? 'Completado' : 'Inactivo' }}
                             </span>
                          </td>
                          <td><ChevronRight class="icon-sm text-muted" /></td>
                       </tr>
                    </tbody>
                 </table>
              </div>
           </div>

           <PatientProgressChart />
        </div>

        <!-- Right Column -->
        <div class="side-column">
           <GestureComparisonChart />
           
           <div class="card export-card">
              <div class="card-header-simple">
                 <h3 class="card-title">Exportación de Datos</h3>
                 <p class="card-desc">Descargue datos clínicos anonimizados</p>
              </div>
              <div class="export-actions">
                 <button class="btn-outline-full"><Download class="icon-sm" /> Exportar datos de sesiones</button>
                 <button class="btn-outline-full"><Download class="icon-sm" /> Exportar métricas de progreso</button>
                 <button class="btn-outline-full"><Download class="icon-sm" /> Informe clínico completo</button>
              </div>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Reuse basic layout styles consistent with AiConsole */
.page-layout { display: flex; flex-direction: column; height: 100%; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 1.5rem; }

.card { background: white; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 1.5rem; }

/* KPI Grid */
.kpi-grid { display: grid; grid-template-columns: 1fr; gap: 1rem; margin-bottom: 1.5rem; }
@media (min-width: 768px) { .kpi-grid { grid-template-columns: repeat(4, 1fr); } }

.kpi-card { padding: 1.25rem; }
.card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.card-title-sm { font-size: 0.875rem; font-weight: 500; color: #64748b; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; }
.metric-sub { font-size: 0.75rem; color: #64748b; display: flex; align-items: center; gap: 4px; }

/* Dashboard Grid */
.dashboard-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media (min-width: 1024px) { 
  .dashboard-grid { grid-template-columns: 2fr 1fr; } 
}

.main-column { display: flex; flex-direction: column; gap: 1.5rem; }
.side-column { display: flex; flex-direction: column; gap: 1.5rem; }

/* Table Section Styles */
.card-header-row { display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; }
@media(min-width: 768px) { .card-header-row { flex-direction: row; justify-content: space-between; align-items: flex-start; } }

.card-title { font-size: 1.1rem; font-weight: 600; color: #0f172a; margin: 0; }
.card-desc { font-size: 0.875rem; color: #64748b; margin: 0.25rem 0 0 0; }

.filters-row { display: flex; gap: 0.5rem; align-items: center; }
.search-wrapper { position: relative; }
.search-icon { position: absolute; left: 0.5rem; top: 50%; transform: translateY(-50%); width: 14px; height: 14px; color: #94a3b8; }
.search-input { padding: 0.5rem 0.5rem 0.5rem 2rem; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.875rem; width: 200px; }
.select-input { padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.875rem; background: white; }
.btn-icon { padding: 0.5rem; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; display: flex; align-items: center;}

/* Table */
.table-container { overflow-x: auto; }
.patient-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.patient-table th { text-align: left; padding: 0.75rem; color: #64748b; font-weight: 500; border-bottom: 1px solid #e2e8f0; }
.patient-table td { padding: 0.75rem; border-bottom: 1px solid #f1f5f9; color: #334155; }
.clickable-row { cursor: pointer; transition: background-color 0.15s; }
.clickable-row:hover { background-color: #f8fafc; }
.clickable-row.selected { background-color: #f1f5f9; }

.patient-info { display: flex; align-items: center; gap: 0.75rem; }
.avatar { width: 32px; height: 32px; background-color: #eff6ff; color: #2563eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; }
.patient-name { font-weight: 500; color: #0f172a; margin: 0; }
.patient-meta { font-size: 0.75rem; color: #64748b; margin: 0; }

.progress-cell { display: flex; align-items: center; gap: 0.5rem; }
.progress-track { width: 60px; height: 6px; background-color: #f1f5f9; border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background-color: #2563eb; border-radius: 99px; }
.progress-text { font-size: 0.75rem; color: #64748b; }

.badge { display: inline-flex; padding: 2px 8px; border-radius: 99px; font-size: 0.7rem; font-weight: 500; text-transform: capitalize; }
.badge-active { background-color: #dcfce7; color: #166534; } /* Green */
.badge-completed { background-color: #cfFAfe; color: #155e75; } /* Cyan */
.badge-inactive { background-color: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

/* Exports */
.export-card { height: fit-content; }
.card-header-simple { margin-bottom: 1rem; }
.export-actions { display: flex; flex-direction: column; gap: 0.75rem; }
.btn-outline-full { display: flex; align-items: center; gap: 0.5rem; width: 100%; padding: 0.6rem; background: white; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.875rem; color: #334155; cursor: pointer; transition: all 0.2s; }
.btn-outline-full:hover { background-color: #f8fafc; border-color: #cbd5e1; }

.text-primary { color: #2563eb; }
.text-success { color: #16a34a; }
.text-chart-2 { color: #0891b2; }
.text-chart-4 { color: #7c3aed; }
.text-muted { color: #94a3b8; }
.icon-sm { width: 1rem; height: 1rem; }
.icon-xs { width: 0.75rem; height: 0.75rem; }
</style>
