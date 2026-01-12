<script setup lang="ts">
import { Hand } from 'lucide-vue-next'
defineProps<{ gesture?: string }>()
</script>

<template>
  <div class="monitor-card">
      <div class="header">
          <h3>Gesto Detectado</h3>
          <Hand class="icon text-primary" />
      </div>
      <div class="content">
          <div class="gesture-display">
              <span class="gesture-name">{{ gesture || '--' }}</span>
              <div class="confidence-bar">
                  <div class="fill" style="width: 88%"></div>
              </div>
              <span class="confidence-text">88% confianza</span>
          </div>
      </div>
  </div>
</template>

<style scoped>
.monitor-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem;
}
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h3 { margin: 0; font-size: 1rem; font-weight: 600; color: #64748b; }
.icon { width: 1.25rem; height: 1.25rem; color: #2563eb; }

.content { display: flex; justify-content: center; padding: 1rem 0; }
.gesture-display { text-align: center; width: 100%; }
.gesture-name { display: block; font-size: 1.5rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; }

.confidence-bar { width: 100%; height: 6px; background: #f1f5f9; border-radius: 99px; overflow: hidden; margin-bottom: 0.25rem; }
.fill { height: 100%; background: #2563eb; border-radius: 99px; }
.confidence-text { font-size: 0.75rem; color: #64748b; }
</style>
