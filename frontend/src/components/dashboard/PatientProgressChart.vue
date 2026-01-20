<script setup lang="ts">
// PatientProgressChart Placeholder
</script>

<template>
  <div class="chart-container">
    <div class="chart-header">
       <h3>Progreso del Paciente</h3>
       <select class="chart-select">
          <option>Últimos 30 días</option>
          <option>Últimos 3 meses</option>
       </select>
    </div>
    
    <div class="chart-area">
       <!-- Simple Line Chart Simulation -->
       <svg viewBox="0 0 400 150" class="chart-svg">
          <path d="M0,120 L50,110 L100,90 L150,95 L200,60 L250,50 L300,55 L350,30 L400,20" 
                fill="none" stroke="#2563eb" stroke-width="3" />
          <circle cx="0" cy="120" r="4" fill="#2563eb"/>
          <circle cx="50" cy="110" r="4" fill="#2563eb"/>
          <circle cx="100" cy="90" r="4" fill="#2563eb"/>
          <circle cx="150" cy="95" r="4" fill="#2563eb"/>
          <circle cx="200" cy="60" r="4" fill="#2563eb"/>
          <circle cx="250" cy="50" r="4" fill="#2563eb"/>
          <circle cx="300" cy="55" r="4" fill="#2563eb"/>
          <circle cx="350" cy="30" r="4" fill="#2563eb"/>
          <circle cx="400" cy="20" r="4" fill="#2563eb"/>
       </svg>
    </div>

    <div class="chart-footer">
       <span>S1</span><span>S2</span><span>S3</span><span>S4</span><span>S5</span><span>S6</span><span>S7</span><span>S8</span><span>S9</span>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  height: 300px;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
h3 { margin: 0; font-size: 1.1rem; font-weight: 600; color: #0f172a; }

.chart-select {
  border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 6px; font-size: 0.85rem; color: #64748b;
}

.chart-area {
  flex: 1;
  display: flex;
  align-items: center;
}
.chart-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.chart-footer {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 0.75rem;
  margin-top: 1rem;
}
</style>
