<script setup lang="ts">
// Confusion Matrix Placeholder
</script>

<template>
  <div class="matrix-container">
    <h3 class="title">Matriz de Confusión</h3>
    <div class="matrix-grid">
      <!-- Header Row -->
      <div class="cell header"></div>
      <div class="cell header">G1</div>
      <div class="cell header">G2</div>
      <div class="cell header">G3</div>
      
      <!-- Row 1 -->
      <div class="cell header">G1</div>
      <div class="cell high">92%</div>
      <div class="cell low">5%</div>
      <div class="cell low">3%</div>

      <!-- Row 2 -->
      <div class="cell header">G2</div>
      <div class="cell low">4%</div>
      <div class="cell high">89%</div>
      <div class="cell low">7%</div>

      <!-- Row 3 -->
      <div class="cell header">G3</div>
      <div class="cell low">2%</div>
      <div class="cell low">3%</div>
      <div class="cell high">95%</div>
    </div>
  </div>
</template>

<style scoped>
.matrix-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
}

.title {
 margin-top: 0;
 font-size: 1.1rem;
 font-weight: 600;
 margin-bottom: 1rem;
}

.matrix-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2px;
  background-color: #e2e8f0;
  border: 1px solid #e2e8f0;
}

.cell {
  background-color: white;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
}

.header {
  font-weight: 600;
  color: #64748b;
  background-color: #f8fafc;
}

.high {
  background-color: #dcfce7;
  color: #166534;
  font-weight: bold;
}

.low {
  color: #94a3b8;
}
</style>
