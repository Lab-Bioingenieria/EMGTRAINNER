<script setup lang="ts">

import { RouterLink } from 'vue-router'
import type { CardHomeProps } from '../../types/home'

// Definimos las propiedades (props) que recibirá el componente
defineProps<CardHomeProps>()
</script>

<template>
  <div class="card-home">
    <div class="card-header">
      <!-- Contenedor del Icono -->
      <div class="icon-wrapper">
        <!-- Slot para insertar cualquier icono SVG o imagen -->
        <slot name="icon">
          <!-- Icono por defecto (opcional) -->
          <span>🔹</span>
        </slot>
      </div>

      <div class="header-text">
        <h3 class="card-title">{{ title }}</h3>
        <span class="card-subtitle">{{ subtitle }}</span>
      </div>
    </div>

    <p class="card-description">
      {{ description }}
    </p>

    <div class="card-footer">
      <RouterLink :to="to" class="card-button">
        Acceder 
        <span class="arrow">→</span>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.card-home {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 40px;
  
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  /* gap: 24px; */
  font-family: 'Roboto', sans-serif;
}

.card-home:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.icon-wrapper {
  background-color: #e0f2fe; /* Light Cyan/Blue */
  color: #0284c7; /* Primary Blue from design */
  min-width: 48px;
  width: 48px;
  height: 48px;
  border-radius: 50%; /* Rounded or slightly rounded square? Image looks like rounded square but let's try rounded rect */
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Deep selector for the SVG icon passed in slot */
:deep(.card-icon) {
  width: 24px;
  height: 24px;
  stroke-width: 2px;
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.card-description {
  margin: 0;
  font-size: 0.925rem;
  color: #475569;
  line-height: 1.6;
  flex-grow: 1;
}

.card-footer {
  margin-top: auto;
}

.card-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #f1f5f9;
  color: #334155;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: 6px;
  transition: all 0.2s;
  width: fit-content;
}

.card-button:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}

.arrow {
  transition: transform 0.2s;
}

.card-button:hover .arrow {
  transform: translateX(4px);
}
</style>
