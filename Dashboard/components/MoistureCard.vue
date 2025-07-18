<template>
  <div
    class="w-full max-w-sm bg-white dark:bg-zinc-800 border-t-4 border-blue-500
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
    <div class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
      {{ isNaN(props.value) ? '--' : props.value.toFixed(1) }}%
    </div>

    <!-- 2) Value‑change line -->
    <div
      v-if="props.change !== undefined"
      class="flex items-baseline text-sm gap-1"
      :class="{
        'text-green-500': props.change > 0,
        'text-red-500':   props.change < 0,
        'text-gray-400':  props.change === 0
      }"
    >
      <span>{{ formatChange(props.change) }}%</span>
      <span class="text-gray-500 dark:text-gray-400">
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
        'bg-green-100 text-green-800':  props.status === 'Healthy',
        'bg-yellow-100 text-yellow-800': props.status === 'Dry',
        'bg-red-100 text-red-800':      props.status === 'Too Wet'
      }"
    >
      {{ props.status }}
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title:        string
  device:       string
  value:        number
  change?:      number
  changeLabel?: string
  status:       'Healthy' | 'Dry' | 'Too Wet'
  isForecast?:  boolean
}>()

function formatChange(change: number) {
  return Math.abs(change).toFixed(2)
}
</script>
