<script setup lang="ts">
import { ref } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import MetricsChart from '../../components/charts/MetricsChart.vue'
import ConfusionMatrix from '../../components/ai/ConfusionMatrix.vue'
import GestureDistribution from '../../components/ai/GestureDistribution.vue'
import ModelVersions from '../../components/ai/ModelVersions.vue'
import { 
  Target, TrendingUp, Layers, CheckCircle2, GitCompare, Clock, 
  Filter, Download, RefreshCw 
} from 'lucide-vue-next'

import type { Session } from '../../types/session'

// Data


const sessions: Session[] = [
  { id: "SES-001", patient: "P-2341", date: "2024-01-10", gestures: 45, accuracy: 92.3, valid: true },
  { id: "SES-002", patient: "P-1892", date: "2024-01-10", gestures: 38, accuracy: 88.7, valid: true },
  { id: "SES-003", patient: "P-3021", date: "2024-01-09", gestures: 52, accuracy: 95.1, valid: false },
  { id: "SES-004", patient: "P-2341", date: "2024-01-09", gestures: 41, accuracy: 89.4, valid: true },
  { id: "SES-005", patient: "P-4156", date: "2024-01-08", gestures: 36, accuracy: 84.2, valid: false },
  { id: "SES-006", patient: "P-1892", date: "2024-01-08", gestures: 48, accuracy: 91.8, valid: true },
]

// State
const selectedSessions = ref<string[]>([])
const activeTab = ref('metrics')

// Methods
const toggleSession = (id: string) => {
  if (selectedSessions.value.includes(id)) {
    selectedSessions.value = selectedSessions.value.filter(s => s !== id)
  } else {
    selectedSessions.value.push(id)
  }
}
</script>

<template>
  <div class="page-layout">
    <TopHeader title="AI Model Console" subtitle="Análisis y mejora del modelo de clasificación sEMG" />

    <div class="content">
      <!-- KPI Cards Grid -->
      <div class="kpi-grid">
        <div class="card kpi-card">
          <div class="card-header-flex">
            <span class="card-title-sm">Precisión Global</span>
            <Target class="icon-sm text-primary" />
          </div>
          <div class="card-content">
            <div class="metric-value">91.4%</div>
            <p class="metric-sub text-success">
              <TrendingUp class="icon-xs" />
              +2.3% vs. versión anterior
            </p>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="card-header-flex">
            <span class="card-title-sm">Sesiones Totales</span>
            <Layers class="icon-sm text-chart-2" />
          </div>
          <div class="card-content">
            <div class="metric-value">1,247</div>
            <p class="metric-sub">843 válidas para reentrenamiento</p>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="card-header-flex">
            <span class="card-title-sm">Gestos Clasificados</span>
            <CheckCircle2 class="icon-sm text-chart-4" />
          </div>
          <div class="card-content">
            <div class="metric-value">52,891</div>
            <p class="metric-sub">8 clases de gestos</p>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="card-header-flex">
            <span class="card-title-sm">Versión Activa</span>
            <GitCompare class="icon-sm text-chart-3" />
          </div>
          <div class="card-content">
            <div class="metric-value">v2.4.1</div>
            <p class="metric-sub">
              <Clock class="icon-xs" />
              Actualizado hace 3 días
            </p>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs-container">
        <div class="tabs-list">
          <button 
            v-for="tab in ['metrics', 'confusion', 'distribution', 'sessions', 'versions']" 
            :key="tab"
            class="tab-trigger"
            :class="{ active: activeTab === tab }"
            @click="activeTab = tab"
          >
            {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content-area">
          <MetricsChart v-if="activeTab === 'metrics'" />
          <ConfusionMatrix v-if="activeTab === 'confusion'" />
          <GestureDistribution v-if="activeTab === 'distribution'" />
          <ModelVersions v-if="activeTab === 'versions'" />

          <!-- Sessions Tab Mockup -->
          <div v-if="activeTab === 'sessions'" class="card sessions-card">
             <div class="card-header-row">
                <div>
                   <h3 class="card-title">Sesiones de Entrenamiento</h3>
                   <p class="card-desc">Gestione los datos para reentrenamiento del modelo</p>
                </div>
                <div class="actions-row">
                   <button class="btn-outline"><Filter class="icon-xs" /> Filtros</button>
                   <button class="btn-outline"><Download class="icon-xs" /> Exportar CSV</button>
                </div>
             </div>

             <div class="table-controls">
                <input type="text" placeholder="Buscar por ID..." class="input-search" />
                <select class="select-filter">
                   <option value="all">Todos</option>
                   <option value="valid">Válidos</option>
                   <option value="invalid">No válidos</option>
                </select>
             </div>

             <table class="session-table">
                <thead>
                   <tr>
                      <th class="w-12"></th>
                      <th>ID Sesión</th>
                      <th>Paciente</th>
                      <th>Fecha</th>
                      <th>Gestos</th>
                      <th>Precisión</th>
                      <th>Estado</th>
                   </tr>
                </thead>
                <tbody>
                   <tr v-for="session in sessions" :key="session.id">
                      <td>
                         <input type="checkbox" 
                                :checked="selectedSessions.includes(session.id)" 
                                @change="toggleSession(session.id)" />
                      </td>
                      <td class="font-mono">{{ session.id }}</td>
                      <td>{{ session.patient }}</td>
                      <td>{{ session.date }}</td>
                      <td>{{ session.gestures }}</td>
                      <td>
                         <span :class="{
                            'text-success': session.accuracy >= 90,
                            'text-warning': session.accuracy >= 85 && session.accuracy < 90,
                            'text-destructive': session.accuracy < 85
                         }">{{ session.accuracy }}%</span>
                      </td>
                      <td>
                         <span class="badge" :class="session.valid ? 'badge-success' : 'badge-secondary'">
                            {{ session.valid ? 'Válido' : 'No válido' }}
                         </span>
                      </td>
                   </tr>
                </tbody>
             </table>
             
             <div v-if="selectedSessions.length > 0" class="selection-bar">
                <span>{{ selectedSessions.length }} sesiones seleccionadas</span>
                <button class="btn-sm"><RefreshCw class="icon-xs" /> Marcar para reentrenamiento</button>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.page-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f8fafc;
  font-family: 'Roboto', sans-serif;
}
.content {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
}

/* Base Styles */
.card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}
@media (min-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(4, 1fr); }
}

.kpi-card { padding: 1.5rem; }
.card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.card-title-sm { font-size: 0.875rem; font-weight: 500; color: #64748b; }
.metric-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; }
.metric-sub { font-size: 0.75rem; color: #64748b; margin: 0; display: flex; align-items: center; gap: 4px; }

/* Colors & Icons */
.text-primary { color: #2563eb; }
.text-success { color: #16a34a; }
.text-warning { color: #d97706; }
.text-destructive { color: #dc2626; }
.text-chart-2 { color: #0891b2; } /* Cyan */
.text-chart-3 { color: #ca8a04; } /* Yellow-ish */
.text-chart-4 { color: #7c3aed; } /* Purple */

.icon-sm { width: 1rem; height: 1rem; }
.icon-xs { width: 0.75rem; height: 0.75rem; }

/* Tabs */
.tabs-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.tabs-list {
  display: flex;
  background-color: #f1f5f9;
  padding: 4px;
  border-radius: 8px;
  width: fit-content;
}
.tab-trigger {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-trigger:hover { color: #0f172a; }
.tab-trigger.active {
  background-color: white;
  color: #0f172a;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* Sessions Table Styles */
.card-header-row { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; }
.card-title { font-size: 1.25rem; font-weight: 600; margin: 0; color: #0f172a; }
.card-desc { font-size: 0.875rem; color: #64748b; margin: 0.25rem 0 0 0; }
.actions-row { display: flex; gap: 0.5rem; }

.btn-outline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
  cursor: pointer;
}
.btn-outline:hover { background-color: #f8fafc; }

.table-controls { display: flex; gap: 1rem; margin-bottom: 1rem; }
.input-search {
  padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.875rem;
}
.select-filter {
  padding: 0.5rem; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.875rem; background: white;
}

.session-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.session-table th { text-align: left; color: #64748b; font-weight: 500; padding: 0.75rem; border-bottom: 1px solid #e2e8f0; }
.session-table td { padding: 0.75rem; border-bottom: 1px solid #f1f5f9; color: #334155; }
.session-table tr:last-child td { border-bottom: none; }
.font-mono { font-family: monospace; }
.w-12 { width: 3rem; }

.badge {
  display: inline-flex; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 500;
}
.badge-success { background-color: #dcfce7; color: #16a34a; }
.badge-secondary { background-color: #f1f5f9; color: #475569; }

.selection-bar {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #f1f5f9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
}
.btn-sm {
  display: flex; align-items: center; gap: 0.5rem;
  background-color: #0f172a; color: white; border: none; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer;
}
</style>
