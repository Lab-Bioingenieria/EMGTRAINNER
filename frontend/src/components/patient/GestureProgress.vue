<script setup lang="ts">
import { Check } from 'lucide-vue-next'

defineProps<{
  steps: number
  currentStep: number
  completedSteps: number[]
}>()
</script>

<template>
  <div class="gesture-progress">
    <div 
        v-for="index in steps" 
        :key="index" 
        class="step-item"
        :class="{ 
            'active': currentStep === index - 1, 
            'completed': completedSteps.includes(index - 1)
        }"
    >
        <div class="step-circle">
            <Check v-if="completedSteps.includes(index - 1)" class="icon-check" />
            <span v-else>{{ index }}</span>
        </div>
        <div v-if="index < steps" class="step-line" :class="{ 'completed': completedSteps.includes(index - 1) }"></div>
    </div>
  </div>
</template>

<style scoped>
.gesture-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
}
.step-item {
    display: flex;
    align-items: center;
    flex: 1;
}
.step-item:last-child {
    flex: 0;
}
.step-circle {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background-color: #f1f5f9;
    border: 2px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 600;
    color: #64748b;
    z-index: 2;
    transition: all 0.3s;
}
.step-item.active .step-circle {
    border-color: #3b82f6;
    background-color: #eff6ff;
    color: #3b82f6;
    transform: scale(1.1);
}
.step-item.completed .step-circle {
    background-color: #22c55e;
    border-color: #22c55e;
    color: white;
}
.step-line {
    flex: 1;
    height: 2px;
    background-color: #e2e8f0;
    margin: 0 4px;
}
.step-line.completed {
    background-color: #22c55e;
}
.icon-check { width: 14px; height: 14px; }
</style>
