<template>
  <div class="relative min-h-screen w-full">
    <!-- Blurred background image with dark overlay -->
    <img src="/home.jpg" alt="Background" class="fixed top-0 left-0 w-full h-full object-cover z-0 blur-md opacity-70 pointer-events-none select-none" onerror="this.style.display='none'" />
    <div class="fixed top-0 left-0 w-full h-full bg-black/80 z-10 pointer-events-none" />
    <!-- Sidebar absolutely positioned, flush with all edges -->
    <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30 border-r-2 border-orange-800 shadow-xl">
      <Sidebar />
    </div>
    <!-- Main content, margin-left for sidebar, above overlay -->
    <div class="ml-64 min-h-screen relative z-20 flex flex-col gap-10 px-6 md:px-12 py-8">
      <!-- 🔹 Average NPK Levels -->
      <section class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6">
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Average NPK Levels</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Nitrogen</h3>
            <p class="text-3xl font-bold text-orange-400">{{ avg.nitrogen }}</p>
          </div>
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Phosphorus</h3>
            <p class="text-3xl font-bold text-orange-400">{{ avg.phosphorus }}</p>
          </div>
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Potassium</h3>
            <p class="text-3xl font-bold text-orange-400">{{ avg.potassium }}</p>
          </div>
        </div>
      </section>

      <!-- 🔸 Soil Temp & Moisture -->
      <section v-if="soilRaw && soilRaw.length" class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6">
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Soil Temperature & Moisture</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
            <LineChart :chart-data="soilChartDataSingle('Soil Temp (°C)')" />
          </div>
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
            <LineChart :chart-data="soilChartDataSingle('Moisture (%)')" />
          </div>
        </div>
      </section>

      <!-- 🔸 CO₂ Forecast -->
      <section v-if="co2ForecastData" class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6">
        <h2 class="text-xl font-semibold mb-4 text-orange-400">CO₂ Forecast</h2>
        <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
          <LineChart :chart-data="co2ForecastData" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '../components/Sidebar/index.vue'
import LineChart from '../components/LineChart.vue'
import type { ChartData } from 'chart.js'

interface NPKReading {
  timestamp: string
  nitrogen: number | null
  phosphorus: number | null
  potassium: number | null
}

interface SoilReading {
  timestamp: string
  soil_temp: number | null
}

interface CO2Reading {
  timestamp: string
  co2: number | null
}

// 🟡 NPK average
const npkData = await $fetch<NPKReading[]>('http://localhost:3001/compost-npk')

const avg = computed(() => {
  if (!npkData.length) return { nitrogen: '-', phosphorus: '-', potassium: '-' }

  const avgField = (field: keyof NPKReading) =>
    Math.round(npkData.reduce((sum, d) => sum + (Number(d[field]) || 0), 0) / npkData.length)

  return {
    nitrogen: avgField('nitrogen'),
    phosphorus: avgField('phosphorus'),
    potassium: avgField('potassium')
  }
})

// 🟢 Soil temp + mocked moisture
const soilRaw = await $fetch<SoilReading[]>('http://localhost:3001/soil-temp-co2')

function soilChartDataSingle(label: string): ChartData<'line'> {
  const labels = soilRaw.map(d => new Date(d.timestamp).toLocaleTimeString())
  const soilTemps = soilRaw.map(d => d.soil_temp ?? 0)
  const moistures = soilTemps.map(() => Math.floor(Math.random() * 30) + 40)
  const data = label === 'Soil Temp (°C)' ? soilTemps : moistures
  const avgVal = Math.round(data.reduce((a, b) => a + b, 0) / data.length)

  return {
    labels,
    datasets: [
      {
        label,
        data,
        borderColor: label === 'Soil Temp (°C)' ? 'rgb(75, 192, 192)' : 'rgb(255, 205, 86)',
        fill: false
      },
      {
        label: `Avg ${label}`,
        data: Array(data.length).fill(avgVal),
        borderColor: label === 'Soil Temp (°C)' ? 'rgb(75, 192, 192)' : 'rgb(255, 205, 86)',
        borderDash: [6, 6],
        fill: false
      }
    ]
  }
}

// pull bucketed moisture for charts that need it
const { data: moistureRaw } = await useFetch(
  'http://localhost:3001/moisture-all',
  { query: { bucket_min: 10, window_min: 180 } }
)

// 🔴 CO₂ Forecast
const co2Raw = await $fetch<CO2Reading[]>('http://localhost:3001/soil-temp-co2')

const co2ForecastData = computed<ChartData<'line'>>(() => {
  const co2 = co2Raw.map(d => d.co2 ?? 0)
  const labels = co2Raw.map(d => new Date(d.timestamp).toLocaleTimeString())

  const n = co2.length
  const x = [...Array(n).keys()]
  const sumX = x.reduce((a, b) => a + b, 0)
  const sumY = co2.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * co2[i], 0)
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0)

  const m = (n * sumXY - sumX * sumY) / ((n * sumX2 - sumX ** 2) || 1)
  const b = (sumY - m * sumX) / (n || 1)

  const forecast = [...Array(5)].map((_, i) => Math.round(m * (n + i) + b))
  const forecastLabels = [...Array(5)].map((_, i) => `T+${i + 1}`)

  return {
    labels: [...labels, ...forecastLabels],
    datasets: [
      {
        label: 'CO₂ (Actual)',
        data: co2,
        borderColor: 'rgb(255, 99, 132)',
        fill: false
      },
      {
        label: 'CO₂ (Forecast)',
        data: [...Array(n).fill(null), ...forecast],
        borderColor: 'rgb(54, 162, 235)',
        borderDash: [6, 6],
        fill: false
      }
    ]
  }
})

</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
</style>
