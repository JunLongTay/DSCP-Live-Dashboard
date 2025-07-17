<template>
  <div class="bg-white dark:bg-zinc-800 p-4 rounded shadow flex flex-col gap-2">
    <!-- Title -->
    <h3 class="text-sm font-semibold text-gray-500 dark:text-gray-300">{{ title }}</h3>

    <!-- Value Display -->
    <div class="flex items-center justify-between">
      <div class="text-2xl font-bold text-gray-900 dark:text-white">
        {{ isNaN(props.value) ? '--' : props.value.toFixed(1) }}%
      </div>

      <!-- Optional % Change & Icon -->
      <div
        v-if="props.change !== undefined"
        class="flex items-center text-sm"
        :class="{
          'text-green-500': props.change > 0,
          'text-red-500': props.change < 0,
          'text-gray-400': props.change === 0
        }"
      >
        <component v-if="trendIcon" :is="trendIcon" class="w-4 h-4 mr-1" />
        {{ formatChange(props.change) }}%
        <span v-if="props.changeLabel" class="ml-1 text-gray-400">({{ props.changeLabel }})</span>
      </div>
    </div>

    <!-- Status Tag -->
    <div
      class="inline-block px-2 py-0.5 text-xs font-medium rounded"
      :class="{
        'bg-green-100 text-green-800': props.status === 'Healthy',
        'bg-yellow-100 text-yellow-800': props.status === 'Dry',
        'bg-red-100 text-red-800': props.status === 'Too Wet'
      }"
    >
      {{ props.status }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, MinusIcon } from '@heroicons/vue/20/solid'

const props = defineProps<{
  title: string
  value: number
  change?: number
  changeLabel?: string
  status: 'Healthy' | 'Dry' | 'Too Wet'
}>()

const trendIcon = computed(() => {
  if (props.change === undefined || props.change === 0) return null
  return props.change > 0 ? ArrowTrendingUpIcon : ArrowTrendingDownIcon
})

function formatChange(change: number) {
  return Math.abs(change).toFixed(2)
}
</script>
