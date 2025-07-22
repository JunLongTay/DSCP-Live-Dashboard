<script setup lang="ts">
import { computed } from 'vue'
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

// Color palette for up to 2 lines, fallback to more if needed
const palette = [
  '#ff8800', // orange
  '#1e90ff', // blue
  '#ffd600', // yellow
  '#e91e63', // pink
  '#4caf50', // green
  '#9c27b0', // purple
]

const coloredChartData = computed(() => {
  // Deep clone chartData to avoid mutating the prop
  const data = JSON.parse(JSON.stringify(props.chartData))
  if (data.datasets) {
    data.datasets.forEach((ds: any, i: number) => {
      ds.borderColor = palette[i % palette.length]
      ds.backgroundColor = palette[i % palette.length] + '55' // semi-transparent fill
      ds.pointBackgroundColor = palette[i % palette.length]
      ds.pointBorderColor = palette[i % palette.length]
    })
  }
  return data
})

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
    <Line :data="coloredChartData" :options="chartOptions" />
  </div>
</template>

