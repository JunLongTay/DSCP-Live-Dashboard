<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale
} from 'chart.js'
import type { ChartData } from 'chart.js'

ChartJS.register(
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale
)

defineProps<{
  chartData: ChartData<'line'>
}>()
</script>

<template>
  <Line
    :data="chartData"
    :options="{ responsive: true, maintainAspectRatio: false }"
    class="h-48"
  />
</template>

