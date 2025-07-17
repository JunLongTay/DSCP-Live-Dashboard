<template>
  <div
    class="w-full max-w-sm bg-white dark:bg-zinc-800 border-t-4 border-blue-500
           p-4 sm:p-6 rounded-lg shadow flex flex-col gap-2
           transition-transform duration-200 ease-out hover:scale-[1.02] hover:shadow-lg"
  >
    <!-- Title + Icon… -->

    <!-- 1) Big Value -->
    <div class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
      {{ isNaN(props.value) ? '--' : props.value.toFixed(1) }}%
    </div>

    <!-- 2) Change Line Below the Number -->
    <div
      v-if="props.change !== undefined"
      class="flex items-baseline text-sm text-gray-500 gap-1"
    >
      <!-- change amount -->
      <span
        :class="{
          'text-green-500': props.change > 0,
          'text-red-500':   props.change < 0,
          'text-gray-400':  props.change === 0
        }"
      >
        {{ formatChange(props.change) }}%
      </span>
      <!-- static “vs forecast” label -->
      <span>(vs forecast)</span>
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
import { computed } from 'vue'
import {
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon,
  CloudIcon
} from '@heroicons/vue/20/solid'

const props = defineProps<{
  title:        string
  value:        number
  change?:      number
  changeLabel?: string
  status:       'Healthy' | 'Dry' | 'Too Wet'
}>()

// Always returns an icon: up, down, or neutral minus
const trendIcon = computed(() => {
  if (props.change === undefined) return null
  if (props.change > 0)  return ArrowTrendingUpIcon
  if (props.change < 0)  return ArrowTrendingDownIcon
  return MinusIcon
})

function formatChange(change: number) {
  return Math.abs(change).toFixed(2)
}
</script>