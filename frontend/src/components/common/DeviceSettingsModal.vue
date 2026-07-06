<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { HealthService, type HardwareConfig, type PortInfo } from '@/services/health.service';
import { XIcon, RefreshCwIcon, SaveIcon } from 'lucide-vue-next';

const emit = defineEmits(['close']);

const config = ref<HardwareConfig>({
  main_port: null,
  independent_data_acquisition: false,
  data_port: null
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
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
    <div class="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-700 flex justify-between items-center bg-gray-800/50">
        <h2 class="text-lg font-semibold text-white">Configuración de Hardware</h2>
        <button @click="$emit('close')" class="text-gray-400 hover:text-white transition-colors">
          <XIcon class="w-5 h-5" />
        </button>
      </div>
      
      <!-- Body -->
      <div class="px-6 py-5 flex flex-col gap-5 text-gray-200">
        <div v-if="isLoading" class="flex justify-center items-center py-8">
            <RefreshCwIcon class="w-8 h-8 text-blue-500 animate-spin" />
            <span class="ml-3 text-sm text-gray-400">Cargando dispositivos...</span>
        </div>
        <div v-else class="space-y-5">
            
            <div class="flex justify-between items-end">
                <p class="text-sm text-gray-400">Selecciona los puertos seriales correspondientes a los microcontroladores.</p>
                <button @click="refreshPorts" class="flex items-center gap-2 text-xs bg-gray-800 hover:bg-gray-700 border border-gray-600 px-2 py-1 rounded transition-colors" title="Actualizar puertos">
                    <RefreshCwIcon class="w-3 h-3" /> Refrescar
                </button>
            </div>

            <!-- Main Port -->
            <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-300">
                    Puerto Principal (Cerebro de la prótesis)
                </label>
                <select v-model="config.main_port" class="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-white outline-none">
                    <option :value="null">-- Seleccionar Puerto --</option>
                    <option v-for="p in availablePorts" :key="p.port" :value="p.port">
                        {{ p.port }} - {{ p.description }}
                    </option>
                </select>
                <p class="text-xs text-gray-500">Normalmente el U2D2 u otro micro que controla los motores Dynamixel.</p>
            </div>

            <!-- Independent Data Checkbox -->
            <div class="flex items-center gap-3 py-2">
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" v-model="config.independent_data_acquisition" class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <span class="text-sm font-medium text-gray-300">Toma de datos independiente</span>
            </div>

            <!-- Data Port (Conditional) -->
            <div v-if="config.independent_data_acquisition" class="space-y-2 animate-in fade-in slide-in-from-top-4 duration-300">
                <label class="block text-sm font-medium text-gray-300">
                    Puerto de Toma de Datos
                </label>
                <select v-model="config.data_port" class="w-full bg-gray-950 border border-gray-700 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-white outline-none">
                    <option :value="null">-- Seleccionar Puerto --</option>
                    <option v-for="p in availablePorts" :key="p.port" :value="p.port">
                        {{ p.port }} - {{ p.description }}
                    </option>
                </select>
                <p class="text-xs text-gray-500">El microcontrolador exclusivo para la lectura de sensores (ej. EMG).</p>
            </div>
            <div v-else class="text-xs text-gray-500 italic py-1">
                La toma de datos se realizará a través del puerto principal.
            </div>

        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-700 bg-gray-800/50 flex justify-end gap-3">
        <button 
          @click="$emit('close')" 
          class="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white bg-transparent border border-gray-600 rounded-lg hover:bg-gray-700 transition-colors"
        >
          Cancelar
        </button>
        <button 
          @click="saveConfig" 
          :disabled="isSaving || isLoading"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-900/20"
        >
          <RefreshCwIcon v-if="isSaving" class="w-4 h-4 animate-spin" />
          <SaveIcon v-else class="w-4 h-4" />
          Guardar Configuración
        </button>
      </div>
    </div>
  </div>
</template>
