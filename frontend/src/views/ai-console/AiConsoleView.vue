<script setup lang="ts">
import { ref } from 'vue'
import TopHeader from '../../components/common/TopHeader.vue'
import MetricsChart from '../../components/charts/MetricsChart.vue'
import ConfusionMatrix from '../../components/ai/ConfusionMatrix.vue'
import GestureDistribution from '../../components/ai/GestureDistribution.vue'
import ModelVersions from '../../components/ai/ModelVersions.vue'
import type { Session } from '../../types/session'

const sessions: Session[] = []

const activeTab = ref('metrics')

const tabs = [
  { id: 'metrics',      label: 'Métricas' },
  { id: 'confusion',    label: 'Confusion matrix' },
  { id: 'distribution', label: 'Distribución' },
  { id: 'sessions',     label: 'Sesiones', count: '0' },
  { id: 'versions',     label: 'Versiones', count: '0' },
]

const gestures = [
  { name: 'Open',   pct: 0, color: 'var(--pulse)' },
  { name: 'Close',  pct: 0, color: 'var(--pulse)' },
  { name: 'Pinch',  pct: 0, color: 'var(--data)' },
  { name: 'Cyl.',   pct: 0, color: 'var(--pulse)' },
  { name: 'Sphere', pct: 0, color: 'var(--pulse)' },
  { name: 'Wave',   pct: 0, color: 'var(--warn)' },
  { name: 'Point',  pct: 0, color: 'var(--pulse)' },
]

const statusMap: Record<string, [string, string]> = {
  true:  ['live', 'Validada'],
  false: ['warn', 'Revisar'],
}
</script>

<template>
  <div class="view-wrap">
    <TopHeader crumb="MÓDULO · AI MODEL CONSOLE" title="AI Model Console">
      <template #actions>
        <button class="btn btn-ghost" onclick="document.getElementById('ai-model-upload').click()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8 12 3 7 8"/><path d="M12 3v12"/>
          </svg>
          Subir modelo de IA
        </button>
        <input type="file" id="ai-model-upload" style="display: none" accept=".pt,.h5,.onnx,.pkl" />
      </template>
    </TopHeader>

    <div class="content">
      <!-- KPI row -->
      <div class="grid-4">
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Precisión Global</span>
            <span class="dot" style="background:var(--ink)" />
          </div>
          <div class="kpi-value">0.0<span class="unit">%</span></div>
          <div class="kpi-meta"><span class="delta">--</span> sin entrenar</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">F1 Promedio</span>
            <span class="dot" style="background:var(--data)" />
          </div>
          <div class="kpi-value">0.00</div>
          <div class="kpi-meta"><span class="delta">--</span> 0 clases</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Dataset</span>
            <span class="dot" style="background:var(--pulse)" />
          </div>
          <div class="kpi-value">0</div>
          <div class="kpi-meta"><span class="delta">--</span> muestras válidas</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">
            <span class="kicker">Versión Activa</span>
            <span class="dot" style="background:var(--warn)" />
          </div>
          <div class="kpi-value">---</div>
          <div class="kpi-meta">sin modelo activo</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="tabs" style="margin-top:22px">
        <button
          v-for="t in tabs"
          :key="t.id"
          :class="['tab', { active: activeTab === t.id }]"
          @click="activeTab = t.id"
        >
          {{ t.label }}
          <span v-if="t.count" class="count">· {{ t.count }}</span>
        </button>
      </div>

      <!-- Tab content -->
      <div style="margin-top:18px">

        <!-- Metrics tab -->
        <div v-if="activeTab === 'metrics'" class="grid-2-3">
          <MetricsChart />
          <div class="card">
            <div class="card-head">
              <div>
                <div class="kicker">Per-Class</div>
                <h3 style="margin-top:4px">Métricas por gesto</h3>
              </div>
            </div>
            <div class="card-body">
              <div style="display:flex; flex-direction:column; gap:12px">
                <div
                  v-for="g in gestures" :key="g.name"
                  style="display:grid; grid-template-columns:70px 1fr 44px; gap:10px; align-items:center"
                >
                  <span style="font-weight:500; font-size:13px">{{ g.name }}</span>
                  <div class="bar"><span :style="{ width: g.pct + '%', background: g.color }" /></div>
                  <span class="num" style="font-size:12px; text-align:right">{{ g.pct }}%</span>
                </div>
              </div>
              <div class="divider" style="margin:16px 0" />
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px">
                <div>
                  <div class="kicker">Inference latency</div>
                  <div class="num" style="font-size:22px; margin-top:2px">0.0 <span class="muted" style="font-size:13px">ms</span></div>
                </div>
                <div>
                  <div class="kicker">Model size</div>
                  <div class="num" style="font-size:22px; margin-top:2px">0.0 <span class="muted" style="font-size:13px">MB</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Confusion matrix tab -->
        <div v-if="activeTab === 'confusion'">
          <ConfusionMatrix />
        </div>

        <!-- Distribution tab -->
        <div v-if="activeTab === 'distribution'">
          <GestureDistribution />
        </div>

        <!-- Sessions tab -->
        <div v-if="activeTab === 'sessions'" class="card">
          <div class="card-head">
            <div>
              <div class="kicker">Recent Sessions</div>
              <h3 style="margin-top:4px">Sesiones de entrenamiento</h3>
            </div>
            <div class="row">
              <div class="search" style="width:240px">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
                </svg>
                <input placeholder="Buscar sesión, paciente…" />
              </div>
              <button class="btn btn-ghost">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>
                </svg>
                CSV
              </button>
            </div>
          </div>
          <div class="card-body flush">
            <table class="tbl">
              <thead>
                <tr>
                  <th>Session ID</th>
                  <th>Paciente</th>
                  <th>Fecha</th>
                  <th>Gestos</th>
                  <th>Precisión</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in sessions" :key="s.id">
                  <td class="mono" style="font-size:12.5px">{{ s.id }}</td>
                  <td style="font-weight:500">{{ s.patient }}</td>
                  <td class="mono muted" style="font-size:12px">{{ s.date }}</td>
                  <td class="num">{{ s.gestures }}</td>
                  <td class="num" :style="{ color: s.accuracy >= 90 ? 'var(--pulse)' : s.accuracy >= 85 ? 'var(--warn)' : 'var(--danger)' }">
                    {{ s.accuracy }}%
                  </td>
                  <td>
                    <span :class="['pill', s.valid ? 'live' : 'warn']">
                      {{ s.valid ? 'Validada' : 'Revisar' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Versions tab -->
        <div v-if="activeTab === 'versions'">
          <ModelVersions />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.view-wrap { display: flex; flex-direction: column; height: 100%; }
</style>
