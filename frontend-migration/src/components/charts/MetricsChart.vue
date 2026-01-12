<script setup lang="ts">
// Placeholder for Metrics Chart
</script>

<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>Rendimiento del Modelo</h3>
      <p>Precisión vs. Epochs</p>
    </div>
    <div class="chart-placeholder">
       <!-- CSS Bar Chart Simulation -->
       <div class="bar" style="height: 40%"></div>
       <div class="bar" style="height: 55%"></div>
       <div class="bar" style="height: 45%"></div>
       <div class="bar" style="height: 70%"></div>
       <div class="bar" style="height: 85%"></div>
       <div class="bar" style="height: 80%"></div>
       <div class="bar" style="height: 92%"></div>
       <div class="chart-line"></div>
    </div>
    <div class="chart-labels">
      <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  height: 350px;
  display: flex;
  flex-direction: column;
}

.chart-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.chart-header p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

.chart-placeholder {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding-top: 2rem;
  padding-bottom: 1rem;
  position: relative;
  gap: 10px;
}

.bar {
  flex: 1;
  background-color: #3b82f6;
  border-radius: 4px 4px 0 0;
  opacity: 0.8;
  transition: height 0.3s, opacity 0.2s;
}

.bar:hover {
  opacity: 1;
}

.chart-line {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: #e2e8f0;
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 0.75rem;
  padding: 0 10px;
}
</style>
