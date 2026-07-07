<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { HealthService, type HardwareConfig, type PortInfo } from '@/services/health.service';
import { XIcon, RefreshCwIcon, SaveIcon } from 'lucide-vue-next';

const emit = defineEmits(['close']);

const config = ref<HardwareConfig>({
  main_port: null,
  independent_data_acquisition: false,
  data_port: null,
  sensor_type: 'umyo',
  motor_type: 'dynamixels'
});

const availablePorts = ref<PortInfo[]>([]);
const isLoading = ref(true);
const isSaving = ref(false);

const loadData = async () => {
  isLoading.value = true;
  try {
    const [portsResponse, configResponse] = await Promise.all([
      HealthService.checkPorts(),
      HealthService.getConfig()
    ]);
    availablePorts.value = portsResponse.ports;
    config.value = configResponse;
  } catch (error) {
    console.error('Error loading hardware configuration', error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  loadData();
});

const saveConfig = async () => {
  isSaving.value = true;
  try {
    if (!config.value.independent_data_acquisition) {
        config.value.data_port = null; // Clear if disabled
    }
    await HealthService.updateConfig(config.value);
    emit('close');
  } catch (error) {
    console.error('Error saving config', error);
  } finally {
    isSaving.value = false;
  }
};

const refreshPorts = async () => {
  isLoading.value = true;
  try {
    const response = await HealthService.checkPorts();
    availablePorts.value = response.ports;
  } catch (error) {
    console.error('Error refreshing ports', error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="modal-backdrop">
    <div class="card modal-card">
      <!-- Header -->
      <div class="card-head">
        <h3>Configuración de Hardware</h3>
        <button @click="$emit('close')" class="icon-btn">
          <XIcon style="width: 20px; height: 20px;" />
        </button>
      </div>
      
      <!-- Body -->
      <div class="card-body col">
        <div v-if="isLoading" class="empty" style="padding: 40px 24px;">
            <RefreshCwIcon style="width: 32px; height: 32px; color: var(--pulse); animation: spin 1s linear infinite;" />
            <span class="muted" style="margin-top: 8px;">Cargando dispositivos...</span>
        </div>
        <div v-else class="col">
            
            <div class="grid-2" style="margin-bottom: 8px;">
                <div class="field">
                    <label>Tipo de Sensores</label>
                    <select v-model="config.sensor_type">
                        <option value="umyo">uMyo</option>
                        <option value="gravitys">Gravitys</option>
                    </select>
                </div>
                <div class="field">
                    <label>Tipo de Motores</label>
                    <select v-model="config.motor_type">
                        <option value="dynamixels">Dynamixel</option>
                        <option value="servos">Servomotores</option>
                    </select>
                </div>
            </div>

            <div class="between" style="align-items: flex-end;">
                <p class="muted" style="font-size: 13px;">Selecciona los puertos seriales correspondientes a los microcontroladores.</p>
                <button @click="refreshPorts" class="btn btn-ghost" style="padding: 4px 8px; font-size: 12px;" title="Actualizar puertos">
                    <RefreshCwIcon style="width: 14px; height: 14px;" /> Refrescar
                </button>
            </div>

            <!-- Main Port -->
            <div class="field">
                <label>
                    Puerto Principal <span class="muted" style="font-weight: 400;">(Cerebro de la prótesis)</span>
                </label>
                <select v-model="config.main_port">
                    <option :value="null">-- Seleccionar Puerto --</option>
                    <option v-for="p in availablePorts" :key="p.port" :value="p.port">
                        {{ p.port }} - {{ p.description }}
                    </option>
                </select>
                <span class="hint">Normalmente el U2D2 u otro micro que controla los motores Dynamixel.</span>
            </div>

            <!-- Independent Data Checkbox -->
            <div class="field" style="flex-direction: row; align-items: center; gap: 8px; margin-top: 8px;">
                <div class="toggle">
                    <button :class="{ active: !config.independent_data_acquisition }" @click="config.independent_data_acquisition = false">No</button>
                    <button :class="{ active: config.independent_data_acquisition }" @click="config.independent_data_acquisition = true">Sí</button>
                </div>
                <label style="margin: 0;">Toma de datos independiente</label>
            </div>

            <!-- Data Port (Conditional) -->
            <div v-if="config.independent_data_acquisition" class="field" style="margin-top: 8px; animation: fadeIn 0.2s ease;">
                <label>Puerto de Toma de Datos</label>
                <select v-model="config.data_port">
                    <option :value="null">-- Seleccionar Puerto --</option>
                    <option v-for="p in availablePorts" :key="p.port" :value="p.port">
                        {{ p.port }} - {{ p.description }}
                    </option>
                </select>
                <span class="hint">El microcontrolador exclusivo para la lectura de sensores (ej. EMG).</span>
            </div>
            <div v-else class="muted" style="font-size: 12px; font-style: italic; margin-top: 8px;">
                La toma de datos se realizará a través del puerto principal.
            </div>

        </div>
      </div>

      <!-- Footer -->
      <div class="modal-foot">
        <button 
          @click="$emit('close')" 
          class="btn btn-ghost"
        >
          Cancelar
        </button>
        <button 
          @click="saveConfig" 
          :disabled="isSaving || isLoading"
          class="btn btn-primary"
        >
          <RefreshCwIcon v-if="isSaving" style="width: 16px; height: 16px; animation: spin 1s linear infinite;" />
          <SaveIcon v-else style="width: 16px; height: 16px;" />
          Guardar Configuración
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 18, 22, 0.4);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.modal-card {
  width: 100%;
  max-width: 520px;
  box-shadow: var(--shadow-pop);
}

.modal-foot {
  padding: 16px 18px;
  border-top: 1px solid var(--bone-200);
  background: var(--bone-50);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-bottom-left-radius: var(--radius);
  border-bottom-right-radius: var(--radius);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
