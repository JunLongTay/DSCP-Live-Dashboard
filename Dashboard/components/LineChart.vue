<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale
} from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

ChartJS.register(
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale
)

const props = defineProps<{
  chartData: ChartData<'line'>
}>()

// extract options to a constant for clarity
const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  // …any other scales/legend/title config
}
</script>

<template>
  <!-- 
    w-full: fill the full width of its parent
    h-[40vh]: height = 40% of viewport height
    (you can tweak to h-[30vh], md:h-[50vh], etc.)
  -->
  <div class="w-full h-[40vh] md:h-[50vh]">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

