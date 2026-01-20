<script setup lang="ts">
import { Play, Pause } from 'lucide-vue-next'

defineProps<{
  isPaused: boolean
}>()

defineEmits<{
  (e: 'toggle'): void
}>()
</script>

<template>
  <button class="btn-play" @click="$emit('toggle')">
    <component :is="isPaused ? Play : Pause" class="icon-xl" />
    <span v-if="isPaused" class="sr-only">Resume</span>
    <span v-else class="sr-only">Pause</span>
  </button>
</template>

<style scoped>
.btn-play {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background-color: #2563eb;
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    transition: all 0.2s;
}

.btn-play:hover {
    transform: scale(1.05);
    background-color: #1d4ed8;
}

.icon-xl {
    width: 32px;
    height: 32px;
}

/* Optional: Add a pulse effect when paused to indicate waiting state */
</style>
