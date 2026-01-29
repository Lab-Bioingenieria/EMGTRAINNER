<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { EmgService } from '../../services/emg.service'
import { FileText, Download, Search, Calendar, Database, FolderOpen, ArrowRight } from 'lucide-vue-next'
import TopHeader from '../../components/common/TopHeader.vue'
import { API_BASE_URL } from '../../lib/constants'

interface SessionFile {
    filename: string;
    created_at: string;
    size_bytes: number;
}

const sessions = ref<SessionFile[]>([])
const loading = ref(true)
const searchQuery = ref('')
const selectedSession = ref<SessionFile | null>(null)

// Computed filtered sessions could be added here if needed
const filteredSessions = ref<SessionFile[]>([])

const loadSessions = async () => {
    loading.value = true
    try {
        const data = await EmgService.getAllSessions()
        sessions.value = data
        filteredSessions.value = data
    } catch (e) {
        console.error("Error loading sessions", e)
    } finally {
        loading.value = false
    }
}

const filterSessions = () => {
    if (!searchQuery.value) {
        filteredSessions.value = sessions.value
        return
    }
    const query = searchQuery.value.toLowerCase()
    filteredSessions.value = sessions.value.filter(s => 
        s.filename.toLowerCase().includes(query)
    )
}

const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString()
}

onMounted(() => {
    loadSessions()
})
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Almacenamiento de Sesiones" subtitle="Historial de grabaciones CSV" />
    
    <div class="content">
        <!-- Stats / Header Card -->
        <div class="container-xl">
             <div class="grid-stats mb-8">
                 <div class="stat-card">
                     <div class="icon-bg blue"><Database class="icon text-blue"/></div>
                     <div class="stat-info">
                         <span class="stat-value">{{ sessions.length }}</span>
                         <span class="stat-label">Archivos Totales</span>
                     </div>
                 </div>
                 <div class="stat-card">
                     <div class="icon-bg green"><Calendar class="icon text-green"/></div>
                     <div class="stat-info">
                         <span class="stat-value">{{ sessions.length > 0 ? new Date(sessions[0].created_at).toLocaleDateString() : '-' }}</span>
                         <span class="stat-label">Última Sesión</span>
                     </div>
                 </div>
             </div>

             <!-- Main Browser -->
             <div class="browser-card">
                 <!-- Toolbar -->
                 <div class="browser-toolbar">
                     <div class="search-wrapper">
                         <Search class="search-icon" />
                         <input v-model="searchQuery" @input="filterSessions" placeholder="Buscar por nombre de archivo..." class="search-input" />
                     </div>
                     <button class="btn btn-outline" @click="loadSessions">
                         Actualizar
                     </button>
                 </div>

                 <!-- List -->
                 <div class="file-list-header">
                     <span class="col-name">Nombre del Archivo</span>
                     <span class="col-date">Fecha de Creación</span>
                     <span class="col-size">Tamaño</span>
                     <span class="col-action">Acción</span>
                 </div>
                 
                 <div v-if="loading" class="loading-state">
                     <div class="spinner"></div>
                     <p>Cargando archivos...</p>
                 </div>
                 
                 <div v-else-if="filteredSessions.length === 0" class="empty-state">
                     <FolderOpen class="empty-icon" />
                     <h3>No se encontraron archivos</h3>
                     <p>Las grabaciones de las sesiones aparecerán aquí.</p>
                 </div>

                 <div v-else class="file-list">
                     <div v-for="file in filteredSessions" :key="file.filename" class="file-row">
                         <div class="col-name file-primary">
                             <div class="file-icon-wrapper">
                                 <FileText class="file-icon" />
                             </div>
                             <span class="filename-text">{{ file.filename }}</span>
                         </div>
                         <div class="col-date text-secondary">
                             {{ formatDate(file.created_at) }}
                         </div>
                         <div class="col-size text-secondary">
                             {{ formatSize(file.size_bytes) }}
                         </div>
                         <div class="col-action">
                             <a :href="`${API_BASE_URL}/storage/sessions/${file.filename}`" 
                                download 
                                class="btn-download"
                                title="Descargar CSV">
                                 <span class="download-text">Descargar</span>
                                 <Download class="icon-xs" />
                             </a>
                         </div>
                     </div>
                 </div>
             </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1200px; margin: 0 auto; width: 100%; }
.mb-8 { margin-bottom: 2rem; }

/* Stats */
.grid-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; }
.stat-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 1rem; }
.icon-bg { width: 3.5rem; height: 3.5rem; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.icon-bg.blue { background-color: #eff6ff; }
.icon-bg.green { background-color: #f0fdf4; }
.text-blue { color: #2563eb; }
.text-green { color: #16a34a; }
.icon { width: 1.75rem; height: 1.75rem; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: #0f172a; line-height: 1.1; }
.stat-label { font-size: 0.875rem; color: #64748b; margin-top: 0.25rem; }

/* Browser Card */
.browser-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; display: flex; flex-direction: column; height: 600px; }
.browser-toolbar { padding: 1.25rem; border-bottom: 1px solid #e2e8f0; display: flex; gap: 1rem; align-items: center; background-color: #fff; }

/* Search */
.search-wrapper { flex: 1; position: relative; }
.search-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 1.25rem; height: 1.25rem; color: #94a3b8; }
.search-input { width: 100%; padding: 0.625rem 1rem 0.625rem 2.5rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; transition: all 0.2s; outline: none; }
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

/* Buttons */
.btn { padding: 0.625rem 1rem; border-radius: 8px; font-weight: 500; font-size: 0.9rem; cursor: pointer; transition: all 0.2s; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #475569; }
.btn-outline:hover { border-color: #cbd5e1; background-color: #f8fafc; color: #0f172a; }

/* File List Header */
.file-list-header { display: grid; grid-template-columns: 2fr 1fr 1fr 140px; padding: 0.75rem 1.5rem; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0; font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }

/* File List Body */
.file-list { overflow-y: auto; flex: 1; }
.file-row { display: grid; grid-template-columns: 2fr 1fr 1fr 140px; padding: 1rem 1.5rem; border-bottom: 1px solid #f1f5f9; align-items: center; transition: background 0.1s; }
.file-row:last-child { border-bottom: none; }
.file-row:hover { background-color: #f8fafc; }

/* Columns */
.col-name { display: flex; align-items: center; gap: 0.75rem; overflow: hidden; }
.file-icon-wrapper { width: 2.25rem; height: 2.25rem; background-color: #f0fdf4; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.file-icon { width: 1.25rem; height: 1.25rem; color: #16a34a; }
.filename-text { font-weight: 500; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.text-secondary { color: #64748b; font-size: 0.9rem; }

/* Actions */
.btn-download { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.75rem; background-color: #eff6ff; color: #2563eb; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 500; transition: all 0.2s; }
.btn-download:hover { background-color: #dbeafe; }
.icon-xs { width: 1rem; height: 1rem; }

/* Empty & Loading */
.loading-state, .empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #94a3b8; gap: 1rem; min-height: 200px; }
.spinner { width: 2rem; height: 2rem; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 0.8s linear infinite; }
.empty-icon { width: 3rem; height: 3rem; opacity: 0.5; }
@keyframes spin { to { transform: rotate(360deg); } }

</style>
