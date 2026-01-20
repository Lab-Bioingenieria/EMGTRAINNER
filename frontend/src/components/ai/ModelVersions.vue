<script setup lang="ts">
import { Clock, CheckCircle2 } from 'lucide-vue-next'
</script>

<template>
  <div class="versions-container">
    <div class="version-header">
       <h3>Historial de Versiones</h3>
       <button class="btn-primary">Nueva Versión</button>
    </div>

    <div class="timeline">
       <div class="version-item active">
         <div class="marker"></div>
         <div class="content">
            <div class="version-title">
               <h4>v2.4.1</h4>
               <span class="badge">Active</span>
            </div>
            <p class="meta">
               <Clock class="icon" /> 3 days ago • Trained on 1,247 samples
            </p>
            <p class="desc">
               Optimización de parámetros para el gesto de "Pinch". Mejora del 2.3%.
            </p>
         </div>
       </div>

       <div class="version-item">
         <div class="marker secondary"></div>
         <div class="content">
            <div class="version-title">
               <h4>v2.4.0</h4>
            </div>
            <p class="meta">
               <Clock class="icon" /> 1 week ago • Trained on 1,100 samples
            </p>
            <p class="desc">
               Inclusión de nuevos datasets de pacientes pediátricos.
            </p>
         </div>
       </div>
    </div>
  </div>
</template>

<style scoped>
.versions-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
}
.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
h3 { margin: 0; font-size: 1.1rem; font-weight: 600; }

.btn-primary {
  background-color: #0f172a;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
}

.timeline {
  border-left: 2px solid #e2e8f0;
  padding-left: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.version-item {
  position: relative;
}

.marker {
  position: absolute;
  left: -1.95rem; /* Adjust based on padding/border */
  top: 0.25rem;
  width: 1rem;
  height: 1rem;
  background-color: #22c55e;
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 0 0 1px #22c55e;
}
.marker.secondary {
  background-color: #94a3b8;
  box-shadow: 0 0 0 1px #94a3b8;
}

.version-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
h4 { margin: 0; font-size: 1rem; font-weight: 600; }

.badge {
  background-color: #dcfce7;
  color: #166534;
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 9999px;
  font-weight: 500;
}

.meta {
  color: #64748b;
  font-size: 0.85rem;
  margin: 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.icon { width: 14px; height: 14px; }

.desc {
  margin: 0.5rem 0 0 0;
  font-size: 0.9rem;
  color: #334155;
}
</style>
