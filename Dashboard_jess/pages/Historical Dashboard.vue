<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { ChartData } from 'chart.js'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Line } from 'vue-chartjs'

import { loadExcel } from '../lib/utils'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const sensorData = ref<any[]>([])

const chartData = ref<ChartData<'line'>>({
  labels: [],
  datasets: []
})

onMounted(async () => {
  sensorData.value = await loadExcel('/data/sensordata.xlsx', 100)

  // Example: visualize temperature readings over time
  const labels = sensorData.value.map((row: any) => row.timestamp || 'Unknown')
  const values = sensorData.value.map((row: any) => Number(row.temperature) || 0)

  chartData.value = {
    labels,
    datasets: [
      {
        label: 'Temperature (°C)',
        data: values,
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">📊 Historical Dashboard</h1>

    <div class="bg-blue-100 p-4 rounded shadow">
      <p class="font-semibold text-blue-700">✅ Historical Dashboard loaded!</p>
      <p class="text-sm mt-2">Now showing chart from your Excel data.</p>
    </div>

    <Line :data="chartData" />
  </div>
</template>