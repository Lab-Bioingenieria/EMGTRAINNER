<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import {
  Search, Filter, ChevronRight, UserPlus
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { PatientService, type PatientRead } from '../../services/patient.service'

const router = useRouter()

const patients = ref<PatientRead[]>([])
const isLoading = ref(true)
const loadError = ref('')

const loadPatients = async () => {
    isLoading.value = true
    loadError.value = ''
    try {
        patients.value = await PatientService.getPatients()
    } catch (e) {
        console.error('Failed to load patients:', e)
        loadError.value = 'No se pudo cargar el listado de pacientes.'
    } finally {
        isLoading.value = false
    }
}

onMounted(loadPatients)

const searchQuery = ref("")
const statusFilter = ref("all")

// Filter Logic
const filteredPatients = computed(() => {
    return patients.value.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                              p.patient_code.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesStatus = statusFilter.value === 'all' || p.status === statusFilter.value
        return matchesSearch && matchesStatus
    })
})

const getInitials = (name: string) => name.split(" ").map(n => n[0]).join("")

const goToDetails = (id: number) => {
    router.push(`/patients/${id}`)
}

// New patient form
const showCreateForm = ref(false)
const newPatientCode = ref('')
const newPatientName = ref('')
const newPatientAge = ref<number | null>(null)
const createError = ref('')
const isCreating = ref(false)

const openCreateForm = () => {
    newPatientCode.value = ''
    newPatientName.value = ''
    newPatientAge.value = null
    createError.value = ''
    showCreateForm.value = true
}

const submitNewPatient = async () => {
    if (!newPatientCode.value || !newPatientName.value || !newPatientAge.value) {
        createError.value = 'Completá código, nombre y edad.'
        return
    }
    isCreating.value = true
    createError.value = ''
    try {
        await PatientService.createPatient({
            patient_code: newPatientCode.value,
            name: newPatientName.value,
            age: newPatientAge.value,
        })
        showCreateForm.value = false
        await loadPatients()
    } catch (e: any) {
        createError.value = e?.response?.data?.detail || 'No se pudo crear el paciente.'
    } finally {
        isCreating.value = false
    }
}
</script>

<template>
  <div class="page-layout">
    <TopHeader title="Pacientes" subtitle="Directorio y gestión clínica" />
    
    <div class="content">
        <div class="container-xl">
            <!-- Controls Bar -->
            <div class="card mb-6 p-4">
                <div class="flex-row-between gap-4 flex-wrap">
                    <div class="search-group">
                        <div class="search-wrapper">
                            <Search class="search-icon" />
                            <input v-model="searchQuery" placeholder="Buscar por nombre o ID..." class="search-input" />
                        </div>
                        <div class="filter-wrapper">
                            <Filter class="icon-xs text-muted" />
                            <select v-model="statusFilter" class="select-input">
                                <option value="all">Todos los estados</option>
                                <option value="active">Activos</option>
                                <option value="inactive">Inactivos</option>
                                <option value="completed">Completados</option>
                            </select>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary" @click="openCreateForm">
                        <UserPlus class="icon-sm mr-2" /> Nuevo Paciente
                    </button>
                </div>
            </div>

            <p v-if="loadError" class="load-error">{{ loadError }}</p>

            <!-- Patient List -->
            <div class="card p-0 overflow-hidden">
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Paciente</th>
                                <th>Estado</th>
                                <th>Progreso General</th>
                                <th>Última Sesión</th>
                                <th class="w-10"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-if="isLoading">
                                <td colspan="5" class="text-center text-muted p-4">Cargando pacientes…</td>
                            </tr>
                            <tr v-else-if="filteredPatients.length === 0">
                                <td colspan="5" class="text-center text-muted p-4">No hay pacientes registrados todavía.</td>
                            </tr>
                            <tr v-for="patient in filteredPatients" v-else :key="patient.id" class="hover-row" @click="goToDetails(patient.id)">
                                <td>
                                    <div class="flex items-center gap-3">
                                        <div class="avatar">{{ getInitials(patient.name) }}</div>
                                        <div>
                                            <div class="font-medium text-slate-900">{{ patient.name }}</div>
                                            <div class="text-xs text-muted">{{ patient.patient_code }} • {{ patient.age }} años</div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span class="badge" :class="'badge-' + patient.status">
                                        {{ patient.status === 'active' ? 'Activo' : patient.status === 'completed' ? 'Alta' : 'Inactivo' }}
                                    </span>
                                </td>
                                <td>
                                    <div class="flex items-center gap-2">
                                        <div class="w-full bg-slate-100 rounded-full h-1.5 w-24">
                                            <div class="bg-blue-600 h-1.5 rounded-full" :style="{ width: patient.progress + '%' }"></div>
                                        </div>
                                        <span class="text-xs font-medium">{{ patient.progress }}%</span>
                                    </div>
                                </td>
                                <td class="text-slate-500">{{ patient.last_session || '—' }}</td>
                                <td>
                                    <button class="btn-icon-ghost">
                                        <ChevronRight class="icon-sm text-slate-400" />
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="p-4 border-t border-slate-100 flex-center text-sm text-muted">
                    Mostrando {{ filteredPatients.length }} pacientes
                </div>
            </div>
        </div>

        <!-- Create Patient Modal -->
        <div v-if="showCreateForm" class="modal-backdrop" @click.self="showCreateForm = false">
            <div class="modal-card">
                <h3 class="modal-title">Nuevo Paciente</h3>
                <div class="modal-field">
                    <label>Código de paciente</label>
                    <input v-model="newPatientCode" placeholder="P-1234" />
                </div>
                <div class="modal-field">
                    <label>Nombre completo</label>
                    <input v-model="newPatientName" placeholder="Nombre y apellido" />
                </div>
                <div class="modal-field">
                    <label>Edad</label>
                    <input v-model.number="newPatientAge" type="number" min="0" />
                </div>
                <p v-if="createError" class="load-error">{{ createError }}</p>
                <div class="actions-row">
                    <button class="btn btn-outline" @click="showCreateForm = false">Cancelar</button>
                    <button class="btn btn-primary" :disabled="isCreating" @click="submitNewPatient">
                        {{ isCreating ? 'Creando…' : 'Crear paciente' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Scoped Standard Styles (Premium Feel) */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1280px; margin: 0 auto; width: 100%; }

.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.p-4 { padding: 1rem; }
.p-0 { padding: 0; }
.mb-6 { margin-bottom: 1.5rem; }

/* Utilities */
.flex-row-between { display: flex; justify-content: space-between; align-items: center; }
.flex-center { display: flex; align-items: center; justify-content: center; }
.gap-4 { gap: 1rem; }
.flex-wrap { flex-wrap: wrap; }
.w-full { width: 100%; }
.w-10 { width: 2.5rem; }
.w-24 { width: 6rem; }
.mr-2 { margin-right: 0.5rem; }

/* Inputs */
.search-group { display: flex; gap: 1rem; flex: 1; max-width: 600px; }
.search-wrapper { position: relative; flex: 2; }
.search-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: #94a3b8; }
.search-input { width: 100%; padding: 0.6rem 0.6rem 0.6rem 2.5rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; outline: none; transition: box-shadow 0.2s; }
.search-input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }

.filter-wrapper { position: relative; flex: 1; display: flex; align-items: center; }
.select-input { width: 100%; padding: 0.6rem 0.6rem 0.6rem 2rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; background: white; outline: none; cursor: pointer; }
.filter-wrapper .icon-xs { position: absolute; left: 0.75rem; z-index: 1; }

/* Buttons */
.btn { padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 500; font-size: 0.9rem; cursor: pointer; border: none; display: flex; align-items: center; transition: all 0.2s; }
.btn-primary { background-color: #0f172a; color: white; box-shadow: 0 2px 4px rgba(15, 23, 42, 0.1); }
.btn-primary:hover { background-color: #1e293b; transform: translateY(-1px); }
.btn-icon-ghost { background: transparent; border: none; padding: 0.5rem; border-radius: 6px; cursor: pointer; display: flex; align-items: center; }
.btn-icon-ghost:hover { background-color: #f1f5f9; }

/* Table */
.table-container { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }
.data-table th { padding: 1rem 1.5rem; background-color: #f8fafc; font-weight: 600; color: #64748b; border-bottom: 1px solid #e2e8f0; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
.data-table td { padding: 1rem 1.5rem; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: middle; }
.hover-row { transition: background-color 0.15s; cursor: pointer; }
.hover-row:hover { background-color: #f8fafc; }

/* Patient Info */
.avatar { width: 36px; height: 36px; background-color: #eff6ff; color: #2563eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem; }
.font-medium { font-weight: 500; }
.text-xs { font-size: 0.75rem; }
.text-muted { color: #94a3b8; }
.text-slate-900 { color: #0f172a; }

/* Badges */
.badge { display: inline-flex; padding: 2px 10px; border-radius: 99px; font-size: 0.75rem; font-weight: 500; }
.badge-active { background-color: #dcfce7; color: #166534; }
.badge-inactive { background-color: #f1f5f9; color: #64748b; }
.badge-completed { background-color: #dbeafe; color: #1e40af; }

/* Icons */
.icon-sm { width: 1.1rem; height: 1.1rem; }
.icon-xs { width: 0.875rem; height: 0.875rem; }

/* Load / form error */
.load-error { color: #dc2626; font-size: 0.875rem; margin-bottom: 1rem; }

/* Create Patient Modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-card { background: white; border-radius: 12px; padding: 1.5rem; width: 100%; max-width: 400px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
.modal-title { font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 0 0 1.25rem; }
.modal-field { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 0.35rem; }
.modal-field label { font-size: 0.8rem; color: #64748b; font-weight: 500; }
.modal-field input { padding: 0.6rem 0.75rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.9rem; outline: none; }
.modal-field input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1); }
.actions-row { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.25rem; }
.btn-outline { background: white; border: 1px solid #e2e8f0; color: #0f172a; }
.btn-outline:hover { background-color: #f8fafc; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
