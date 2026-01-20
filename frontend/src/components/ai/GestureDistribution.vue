<script setup lang="ts">
// Gesture Distribution Placeholder
</script>

<template>
  <div class="distribution-container">
    <h3>Distribución de Gestos</h3>
    <div class="list">
       <div class="item">
         <span class="label">Fist</span>
         <div class="bar-bg"><div class="bar" style="width: 35%"></div></div>
         <span class="value">35%</span>
       </div>
       <div class="item">
         <span class="label">Open</span>
         <div class="bar-bg"><div class="bar" style="width: 25%"></div></div>
         <span class="value">25%</span>
       </div>
       <div class="item">
         <span class="label">Pinch</span>
         <div class="bar-bg"><div class="bar" style="width: 20%"></div></div>
         <span class="value">20%</span>
       </div>
       <div class="item">
         <span class="label">Wave</span>
         <div class="bar-bg"><div class="bar" style="width: 15%"></div></div>
         <span class="value">15%</span>
       </div>
       <div class="item">
         <span class="label">Other</span>
         <div class="bar-bg"><div class="bar" style="width: 5%"></div></div>
         <span class="value">5%</span>
       </div>
    </div>
  </div>
</template>

<style scoped>
.distribution-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
}
h3 { margin-top: 0; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; }

.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.label {
  width: 60px;
  font-size: 0.875rem;
  font-weight: 500;
}

.bar-bg {
  flex: 1;
  height: 8px;
  background-color: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background-color: #8b5cf6;
  border-radius: 4px;
}

.value {
  width: 40px;
  text-align: right;
  font-size: 0.875rem;
  color: #64748b;
}
</style>
