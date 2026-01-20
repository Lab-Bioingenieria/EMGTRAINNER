<script setup lang="ts">
// GestureComparisonChart Placeholder
</script>

<template>
  <div class="comparison-container">
    <h3>Comparativa de Gestos</h3>
    <div class="radar-placeholder">
       <!-- Simplified Radar Chart Visual -->
       <div class="radar-circle c1"></div>
       <div class="radar-circle c2"></div>
       <div class="radar-circle c3"></div>
       <div class="radar-shape"></div>
       
       <span class="label top">Fist</span>
       <span class="label right">Open</span>
       <span class="label bottom">Pinch</span>
       <span class="label left">Wave</span>
    </div>
    <div class="legend">
      <div class="item"><span class="dot current"></span> Actual</div>
      <div class="item"><span class="dot avg"></span> Promedio</div>
    </div>
  </div>
</template>

<style scoped>
.comparison-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  height: 350px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h3 { width: 100%; text-align: left; margin-top:0; font-size: 1.1rem; font-weight: 600; color: #0f172a; }

.radar-placeholder {
  position: relative;
  width: 200px;
  height: 200px;
  margin: 2rem 0;
}

.radar-circle {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  border: 1px solid #e2e8f0;
  border-radius: 50%;
}
.c1 { width: 100%; height: 100%; }
.c2 { width: 66%; height: 66%; }
.c3 { width: 33%; height: 33%; }

.radar-shape {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 70%; height: 60%;
  background-color: rgba(37, 99, 235, 0.2);
  border: 2px solid #2563eb;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}

.label { position: absolute; font-size: 0.75rem; color: #64748b; font-weight: 500; }
.top { top: -20px; left: 50%; transform: translateX(-50%); }
.bottom { bottom: -20px; left: 50%; transform: translateX(-50%); }
.left { left: -40px; top: 50%; transform: translateY(-50%); }
.right { right: -40px; top: 50%; transform: translateY(-50%); }

.legend {
  display: flex; gap: 1rem; margin-top: auto;
}
.item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #64748b; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.current { background-color: #2563eb; }
.avg { background-color: #e2e8f0; }
</style>
