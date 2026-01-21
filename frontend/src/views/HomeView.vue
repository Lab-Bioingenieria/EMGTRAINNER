<script setup lang="ts">
import { interfaces } from '../types/home'
import CardHome from '../components/home/card_home.vue'
import TopHeader from '../components/common/TopHeader.vue'
</script>

<template>
  <div class="page-layout">
    <TopHeader 
      title="MyoTrainer" 
      :show-search="false"
      :show-notifications="false"
    />

    <main class="content">
      <div class="container-xl">
        <div class="hero-section">
          <h1 class="hero-title">Sistema de Entrenamiento sEMG</h1>
          <p class="hero-subtitle">
            Plataforma clínica para entrenamiento y evaluación de prótesis mioeléctricas
          </p>
        </div>

        <div class="grid-container">
          <CardHome
            v-for="item in interfaces"
            :key="item.to"
            :title="item.title"
            :subtitle="item.subtitle"
            :description="item.description"
            :to="item.to"
            class="grid-item"
          >
            <template #icon>
              <component :is="item.icon" class="card-icon" />
            </template>
          </CardHome>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Standard Layout */
.page-layout { display: flex; flex-direction: column; height: 100vh; background-color: #f8fafc; font-family: 'Roboto', sans-serif; }
.content { flex: 1; overflow: auto; padding: 2rem; }
.container-xl { max-width: 1024px; margin: 0 auto; width: 100%; }

/* Hero */
.hero-section { margin-bottom: 3rem; margin-top: 3rem; text-align: center; }
.hero-title { font-size: 2rem; font-weight: 700; color: #0f172a; margin-bottom: 0.75rem; line-height: 1.2; }
.hero-subtitle { font-size: 1.125rem; color: #64748b; max-width: 42rem; margin: 0 auto; line-height: 1.6; }

/* Grid */
.grid-container {
  display: grid;
  gap: 2rem;
  grid-template-columns: 1fr;
  padding-bottom: 2rem;
}

@media (min-width: 768px) {
  .grid-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 3rem;
  }
}

.card-icon {
  height: 2rem;
  width: 2rem;
  color: #2563eb; /* Primary Blue */
}
</style>
