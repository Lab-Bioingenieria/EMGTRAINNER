<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import PatientProgressChart from '../../components/dashboard/PatientProgressChart.vue'
import GestureComparisonChart from '../../components/dashboard/GestureComparisonChart.vue'
import type { Patient } from '../../types/patient'
import { authService } from '@/services/auth.service'
import { API_BASE_URL } from '@/lib/constants'

const patients = ref<Patient[]>([])

onMounted(async () => {
  const token = authService.getToken()
  if (token) {
    try {
      const res = await fetch(`${API_BASE_URL}/patients/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        patients.value = await res.json()
      }
    } catch(e) {}
  }
})

const searchQuery  = ref('')
const statusFilter = ref('all')

const filteredPatients = computed(() =>
  patients.value.filter(p => {
    const matchSearch = p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                        p.patient_code.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchStatus = statusFilter.value === 'all' || p.status === statusFilter.value
    return matchSearch && matchStatus
  })
)

const statusMap: Record<string, [string, string]> = {
  active:    ['live', 'Activo'],
  inactive:  ['off',  'Inactivo'],
  completed: ['data', 'Completado'],
}

const getInitials = (name: string) => name.split(' ').map(n => n[0]).join('')
</script>

<template>
  <div class="view-wrap">
    <TopHeader crumb="MÓDULO · PANEL DE PACIENTES" title="Panel de Pacientes">
      <template #actions>
        <button class="btn btn-ghost">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>
          </svg>
          Exportar
        </button>
        <button class="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          Nuevo paciente
        </button>
      </template>
    </TopHeader>

    <div class="content">
      <!-- KPI row -->
      <div class="grid-4">
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Pacientes Totales</span>
            <span class="dot" style="background:var(--ink)" />
          </div>
          <div class="kpi-value">{{ patients.length }}</div>
          <div class="kpi-meta"><span class="delta up">↑ +{{ patients.length }}</span> este mes</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Sesiones Hoy</span>
            <span class="dot live" />
          </div>
          <div class="kpi-value">18</div>
          <div class="kpi-meta">5 en progreso</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Progreso Promedio</span>
            <span class="dot" style="background:var(--data)" />
          </div>
          <div class="kpi-value">78<span class="unit">%</span></div>
          <div class="kpi-meta"><span class="delta up">↑ +5%</span> vs. mes anterior</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Pacientes Activos</span>
            <span class="dot" style="background:var(--signal)" />
          </div>
          <div class="kpi-value">{{ patients.filter(p => p.status === 'active').length }}</div>
          <div class="kpi-meta">72% del total</div>
        </div>
      </div>

      <!-- Main grid -->
      <div class="grid-2-3" style="margin-top: 18px">
        <!-- Patient table -->
        <div class="card">
          <div class="card-head">
            <div>
              <div class="kicker">Patient Registry</div>
              <h3 style="margin-top:4px">Listado de pacientes</h3>
              <p>Gestión y seguimiento de todos los pacientes activos.</p>
            </div>
            <div class="row">
              <div class="search" style="width:220px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
                </svg>
                <input v-model="searchQuery" placeholder="Buscar paciente…" />
              </div>
              <select v-model="statusFilter" style="padding:8px 12px; border:1px solid var(--bone-200); border-radius:6px; font-size:13px; background:var(--paper)">
                <option value="all">Todos</option>
                <option value="active">Activos</option>
                <option value="inactive">Inactivos</option>
                <option value="completed">Completados</option>
              </select>
            </div>
          </div>
          <div class="card-body flush">
            <table class="tbl">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Sesiones</th>
                  <th>Última sesión</th>
                  <th>Progreso</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in filteredPatients" :key="p.id">
                  <td>
                    <div class="row" style="gap:10px">
                      <div class="avatar">{{ getInitials(p.name) }}</div>
                      <div>
                        <div style="font-weight:600">{{ p.name }}</div>
                        <div class="mono muted" style="font-size:11px">{{ p.patient_code }} · {{ p.age }} años</div>
                      </div>
                    </div>
                  </td>
                  <td class="num">{{ p.sessions_count }}</td>
                  <td class="mono muted" style="font-size:12px">{{ p.last_session || '---' }}</td>
                  <td>
                    <div class="row" style="gap:10px">
                      <div class="bar signal" style="width:90px"><span :style="{ width: p.progress + '%' }" /></div>
                      <span class="num" style="font-size:12px">{{ p.progress }}%</span>
                    </div>
                  </td>
                  <td>
                    <span :class="['pill', statusMap[p.status][0]]">{{ statusMap[p.status][1] }}</span>
                  </td>
                  <td>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--ink-4)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                      <path d="m9 6 6 6-6 6"/>
                    </svg>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Right column -->
        <div class="col">
          <GestureComparisonChart />

          <div class="card">
            <div class="card-head">
              <div>
                <div class="kicker">Data Export</div>
                <h3 style="margin-top:4px">Exportación clínica</h3>
              </div>
            </div>
            <div class="card-body" style="display:flex; flex-direction:column; gap:8px">
              <button class="btn btn-ghost btn-block" style="justify-content:flex-start; padding:12px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>
                </svg>
                Datos de sesiones (.csv)
              </button>
              <button class="btn btn-ghost btn-block" style="justify-content:flex-start; padding:12px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>
                </svg>
                Métricas de progreso (.xlsx)
              </button>
              <button class="btn btn-ghost btn-block" style="justify-content:flex-start; padding:12px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6Z"/><path d="M14 3v6h6"/>
                </svg>
                Informe clínico (.pdf)
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress chart -->
      <div style="margin-top:18px">
        <PatientProgressChart />
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-wrap { display: flex; flex-direction: column; height: 100%; }
</style>
