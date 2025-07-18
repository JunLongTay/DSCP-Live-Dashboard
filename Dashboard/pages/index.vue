<template>
  <div class="p-6 space-y-12">

    <!-- 🔹 Average NPK Levels -->
    <section>
      <h2 class="text-xl font-bold mb-4">Average NPK Levels</h2>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-zinc-800 rounded shadow p-4">
          <h3 class="font-semibold text-sm">Nitrogen</h3>
          <p class="text-2xl font-bold text-blue-600">{{ avg.nitrogen }}</p>
        </div>
        <div class="bg-white dark:bg-zinc-800 rounded shadow p-4">
          <h3 class="font-semibold text-sm">Phosphorus</h3>
          <p class="text-2xl font-bold text-purple-600">{{ avg.phosphorus }}</p>
        </div>
        <div class="bg-white dark:bg-zinc-800 rounded shadow p-4">
          <h3 class="font-semibold text-sm">Potassium</h3>
          <p class="text-2xl font-bold text-green-600">{{ avg.potassium }}</p>
        </div>
      </div>
    </section>

<!-- 🔸 Soil Temp & Moisture -->
<section v-if="soilRaw && soilRaw.length">
  <h2 class="text-xl font-bold mb-4">Soil Temperature & Moisture</h2>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="bg-white dark:bg-zinc-800 rounded shadow p-4">
      <LineChart :chart-data="soilChartDataSingle('Soil Temp (°C)')" />
    </div>
    <div class="bg-white dark:bg-zinc-800 rounded shadow p-4">
      <LineChart :chart-data="soilChartDataSingle('Moisture (%)')" />
    </div>
  </div>
</section>

    <!-- 🔸 CO₂ Forecast -->
    <section v-if="co2ForecastData">
      <h2 class="text-xl font-bold mb-4">CO₂ Forecast</h2>
      <div class="bg-white dark:bg-zinc-800 rounded shadow p-4">
        <LineChart :chart-data="co2ForecastData" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
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
