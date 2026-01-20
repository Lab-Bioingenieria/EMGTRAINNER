<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  timeRemaining: number
  totalTime: number
  isResting: boolean
}>()

const radius = 45
const circumference = 2 * Math.PI * radius
const strokeDashoffset = computed(() => {
  const percent = props.timeRemaining / props.totalTime
  return circumference - percent * circumference
})
</script>

<template>
  <div class="radial-timer">
    <svg class="timer-svg" viewBox="0 0 100 100">
      <circle class="timer-bg" cx="50" cy="50" r="45" />
      <circle
        class="timer-progress"
        :class="isResting ? 'rest' : 'active'"
        cx="50"
        cy="50"
        r="45"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
      />
    </svg>
    <div class="timer-text">
      <span class="text-3xl font-bold">{{ timeRemaining }}</span>
    </div>
  </div>
</template>

<style scoped>
.radial-timer {
  position: relative;
  width: 120px;
  height: 120px;
}
.timer-svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}
.timer-bg {
  fill: none;
  stroke: #e2e8f0;
  stroke-width: 8;
}
.timer-progress {
  fill: none;
  stroke: #3b82f6; /* active blue */
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s linear;
}
.timer-progress.rest {
  stroke: #fbbf24; /* amber for rest */
}
.timer-text {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  color: #0f172a;
}
</style>
