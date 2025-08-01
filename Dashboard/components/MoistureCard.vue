<template>
  <div
    class="w-full max-w-sm dark:bg-[#121212] border-t-4 border-blue-500
           p-4 sm:p-6 rounded-lg shadow flex flex-col gap-2
           transition-transform duration-200 ease-out hover:scale-[1.02] hover:shadow-lg"
  >
    <!-- Forecast/Current Badge -->
    <div
      v-if="props.isForecast !== undefined"
      class="self-start text-xs font-semibold inline-block px-2 py-0.5 rounded-full mb-1"
      :class="props.isForecast
        ? 'bg-yellow-100 text-yellow-800'
        : 'bg-blue-100 text-blue-800'"
    >
      {{ props.isForecast ? 'Forecast' : 'Current' }}
    </div>

    <!-- 1) Big Value -->
    <div class="text-2xl sm:text-3xl font-bold text-orange-400">
      {{ isNaN(props.value) ? '--' : props.value.toFixed(1) }}%
    </div>

    <!-- 2) Value‑change line -->
    <div
      v-if="props.change !== undefined"
      class="flex items-baseline text-sm gap-1"
      :class="{
        'text-green-500': props.change > 2,   // Significant improvement (forecast higher than current)
        'text-red-500':   props.change < -2,  // Significant decline (forecast lower than current) 
        'text-blue-500':  Math.abs(props.change) <= 2  // Stable (small change)
      }"
    >
      <span>{{ formatChange(props.change) }}%</span>
      <span style="color: #f0d5af;">
        — {{ props.device }}
        <template v-if="props.changeLabel">
          ({{ props.changeLabel }})
        </template>
      </span>
    </div>

    <!-- 3) Status Tag -->
    <div
      class="inline-block px-2 py-0.5 text-xs font-medium rounded mt-2"
      :class="{
        // For current readings with forecast comparison (isForecast = false)
        'bg-green-100 text-green-800':   props.isForecast === false && forecastStatus === 'Improving',
        'bg-blue-100 text-blue-800':     props.isForecast === false && forecastStatus === 'Stable',
        'bg-red-100 text-red-800':       props.isForecast === false && forecastStatus === 'Declining',
        
        // For forecast cards (isForecast = true or undefined)
        'bg-emerald-100 text-emerald-800': props.isForecast !== false && props.status === 'Healthy',
        'bg-yellow-100 text-yellow-800':   props.isForecast !== false && props.status === 'Dry',
        'bg-orange-100 text-orange-800':   props.isForecast !== false && props.status === 'Too Wet'
      }"
    >
      {{ props.isForecast === false ? forecastStatus : props.status }}
    </div>

    <!-- Recommendations Container -->
    <div class="mt-4 bg-zinc-900/80 rounded p-3 border border-orange-700">
      <div class="flex items-center gap-2 mb-2 cursor-pointer" @click="toggleRecommendations">
        <!-- Dynamic Icon based on forecast trend -->
        <svg v-if="forecastStatus === 'Improving'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
        </svg>
        <svg v-else-if="forecastStatus === 'Declining'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 3a7 7 0 00-7 7c0 3.07 1.64 5.64 4 6.32V18a1 1 0 001 1h4a1 1 0 001-1v-1.68c2.36-.68 4-3.25 4-6.32a7 7 0 00-7-7zm0 16v2m-4-2h8" />
        </svg>
        
        <span class="font-semibold text-orange-300">Recommendations</span>
      </div>

      <!-- Conditionally show recommendations content -->
      <div v-if="showRecommendations" class="text-sm text-orange-200 leading-relaxed whitespace-pre-line">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'  // ← Add computed import

const props = defineProps<{
  title:        string
  device:       string
  value:        number
  change?:      number
  changeLabel?: string
  status:       'Healthy' | 'Dry' | 'Too Wet'
  isForecast?:  boolean
}>()

// Add computed forecast status
const forecastStatus = computed(() => {
  if (props.isForecast === false && props.change !== undefined) {
    // For current readings with forecast comparison
    if (props.change > 5) return 'Improving'  // Forecast shows significant increase
    if (props.change < -5) return 'Declining' // Forecast shows significant decrease
    if (Math.abs(props.change) <= 5) return 'Stable' // Small change
  }
  return props.status // Use original status for forecast cards
})

// Reactive state to toggle the recommendations visibility
const showRecommendations = ref(false);

function toggleRecommendations() {
  showRecommendations.value = !showRecommendations.value;
}

function formatChange(change: number) {
  return Math.abs(change).toFixed(2)
}
</script>