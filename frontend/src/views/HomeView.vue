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
        <div class="hero-section text-center mb-10 mt-12">
          <h1 class="text-3xl font-bold text-slate-900 mb-3">Sistema de Entrenamiento sEMG</h1>
          <p class="text-slate-500 text-lg max-w-2xl mx-auto">
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
.hero-section { margin-bottom: 3rem; }
.text-center { text-align: center; }
.mx-auto { margin-left: auto; margin-right: auto; }
.max-w-2xl { max-width: 42rem; }
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.font-bold { font-weight: 700; }
.text-slate-900 { color: #0f172a; }
.text-slate-500 { color: #64748b; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-10 { margin-bottom: 2.5rem; }
.mt-4 { margin-top: 1rem; }

/* Grid */
.grid-container {
  display: grid;
  gap: 4rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .grid-container {
    grid-template-columns: repeat(2, 1fr);
  }
}

.card-icon {
  height: 2rem;
  width: 2rem;
  color: #2563eb; /* Primary Blue */
}
</style>
