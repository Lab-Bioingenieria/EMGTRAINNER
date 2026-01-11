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

    <RouterLink :to="to" class="card-button">
      Acceder 
      <span class="arrow">→</span>
    </RouterLink>
  </div>
</template>

<style scoped>
.card-home {
  background-color: #ffffff;
  border: 1px solid #e5e7eb; /* Gris muy suave */
  border-radius: 12px;
  padding: 24px;
  width: 100%;
  max-width: 400px; /* O el ancho que prefieras */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-family: 'Inter', sans-serif; /* O la fuente que uses */
}

.card-home:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-wrapper {
  background-color: #f3f4f6; /* Fondo gris/azulado suave */
  color: #0f172a; /* Color del icono oscuro */
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.card-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #111827;
}

.card-subtitle {
  font-size: 0.875rem;
  color: #6b7280; /* Gris texto secundario */
  font-weight: 500;
}

.card-description {
  margin: 0;
  font-size: 0.95rem;
  color: #4b5563;
  line-height: 1.5;
  flex-grow: 1; /* Para que todos los botones queden alineados abajo si hay varias cards */
}

.card-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background-color: #f3f4f6;
  color: #1f2937;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  border-radius: 8px;
  transition: background-color 0.2s;
  width: fit-content;
}

.card-button:hover {
  background-color: #e5e7eb;
}

.arrow {
  transition: transform 0.2s;
}

.card-button:hover .arrow {
  transform: translateX(3px);
}
</style>
