<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { EmgService } from '../../services/emg.service'
import TopHeader from '../../components/common/TopHeader.vue'
import { API_BASE_URL } from '../../lib/constants'

interface SessionFile {
  filename: string
  created_at: string
  size_bytes: number
}

const sessions      = ref<SessionFile[]>([])
const loading       = ref(true)
const searchQuery   = ref('')

const filteredSessions = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return sessions.value
  return sessions.value.filter(s => s.filename.toLowerCase().includes(q))
})

const loadSessions = async () => {
  loading.value = true
  try {
    sessions.value = await EmgService.getAllSessions()
  } catch (e) {
    console.error('Error loading sessions', e)
  } finally {
    loading.value = false
  }
}

const formatSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (iso: string) => new Date(iso).toLocaleString('es-MX', { dateStyle: 'medium', timeStyle: 'short' })

onMounted(loadSessions)
</script>

<template>
  <div class="view-wrap">
    <TopHeader crumb="MÓDULO · ALMACENAMIENTO" title="Almacenamiento de Sesiones">
      <template #actions>
        <button class="btn btn-ghost" @click="loadSessions">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>
          </svg>
          Actualizar
        </button>
        <button class="btn btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>
          </svg>
          Exportar todo
        </button>
      </template>
    </TopHeader>

    <div class="content">
      <!-- KPI row -->
      <div class="grid-4">
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Archivos Totales</span>
            <span class="dot" style="background:var(--data)" />
          </div>
          <div class="kpi-value">{{ sessions.length.toLocaleString() }}</div>
          <div class="kpi-meta"><span class="delta up">↑ +18</span> esta semana</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Tamaño Total</span>
            <span class="dot" />
          </div>
          <div class="kpi-value">3.42<span class="unit">GB</span></div>
          <div class="kpi-meta">de 50 GB asignados</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Última Sesión</span>
            <span class="dot live" />
          </div>
          <div class="kpi-value">14:22</div>
          <div class="kpi-meta">hoy · P-2341</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Retención</span>
            <span class="dot" style="background:var(--signal)" />
          </div>
          <div class="kpi-value">2<span class="unit">años</span></div>
          <div class="kpi-meta">política HIPAA activa</div>
        </div>
      </div>

      <!-- File browser card -->
      <div class="card" style="margin-top: 18px">
        <div class="card-head">
          <div>
            <div class="kicker">CSV Archive</div>
            <h3 style="margin-top:4px">Historial de grabaciones</h3>
            <p>Datos sEMG sin procesar de cada sesión, con metadatos clínicos.</p>
          </div>
          <div class="row">
            <div class="search" style="width:280px">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
              </svg>
              <input v-model="searchQuery" placeholder="Buscar por nombre, ID paciente, fecha…" />
            </div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="empty">
          <div class="empty-art">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" class="spin-icon">
              <path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/>
            </svg>
          </div>
          <h4>Cargando archivos…</h4>
        </div>

        <!-- Empty -->
        <div v-else-if="filteredSessions.length === 0" class="empty">
          <div class="empty-art">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"/>
            </svg>
          </div>
          <h4>No se encontraron archivos</h4>
          <p>Las grabaciones de sesiones aparecerán aquí.</p>
        </div>

        <!-- Table -->
        <div v-else class="card-body flush">
          <table class="tbl">
            <thead>
              <tr>
                <th>Nombre del archivo</th>
                <th>Fecha de creación</th>
                <th>Tamaño</th>
                <th>Estado</th>
                <th style="text-align:right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="file in filteredSessions" :key="file.filename">
                <td>
                  <div class="row" style="gap:10px">
                    <div class="module-icon tone-data" style="width:32px; height:32px; border-radius:6px">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6Z"/><path d="M14 3v6h6"/>
                      </svg>
                    </div>
                    <span class="mono" style="font-size:12.5px">{{ file.filename }}</span>
                  </div>
                </td>
                <td class="muted">{{ formatDate(file.created_at) }}</td>
                <td class="mono">{{ formatSize(file.size_bytes) }}</td>
                <td><span class="pill live">Encriptado</span></td>
                <td style="text-align:right">
                  <div style="display:inline-flex; gap:4px">
                    <a :href="`${API_BASE_URL}/storage/sessions/${file.filename}`" download class="icon-btn" title="Descargar">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>
                      </svg>
                    </a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-wrap { display: flex; flex-direction: column; height: 100%; }
.spin-icon { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
