<template>
  <div class="p-6 space-y-8">
    <h1 class="text-2xl font-bold mb-4">Soil Moisture Forecast</h1>

    <!-- Multi-Select Device Filter -->
    <div>
      <label for="device-filter" class="block font-medium mb-1">Filter by Device(s)</label>
      <select
        id="device-filter"
        v-model="selectedDevices"
        multiple
        class="border rounded p-2 w-full max-w-xl h-32"
      >
        <option
          v-for="(device, i) in deviceOptions"
          :key="i"
          :value="device"
        >
          {{ device }}
        </option>
      </select>
      <p class="text-sm text-gray-500 mt-1">
        Hold Ctrl (Windows) or Command (Mac) to select multiple devices
      </p>
    </div>

    <!-- Moisture Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MoistureCard
        v-for="(device, index) in selectedDevices"
        :key="device + '-latest'"
        :title="`${device} Latest`"
        :value="latestMoisture[device] ?? 0"
        :change="round(latestMoisture[device] - forecastValues[device]?.[29])"
        :changeLabel="'vs forecast'"
        :status="statusTag(latestMoisture[device])"
      />
      <MoistureCard
        v-for="(device, index) in selectedDevices"
        :key="device + '-forecast'"
        :title="`${device} Forecast Day 30`"
        :value="forecastValues[device]?.[29] ?? 0"
        :change="round(forecastValues[device]?.[29] - latestMoisture[device])"
        :changeLabel="'vs current'"
        :status="statusTag(forecastValues[device]?.[29])"
      />
    </div>

    <!-- Historical Charts -->
    <section v-if="selectedDevices.length">
      <h2 class="text-lg font-semibold mb-2">Recent Soil Moisture Readings</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="device in selectedDevices"
          :key="device + '-chart'"
          class="bg-white dark:bg-zinc-800 p-4 rounded shadow"
        >
          <Line :data="historicalChart(deviceData[device] ?? [], device)" :options="chartOptions" class="h-60" />
        </div>
      </div>
    </section>

    <!-- Forecast Chart -->
    <section v-if="forecastChart">
      <h2 class="text-lg font-semibold mt-6 mb-2">Moisture Forecast (Next 30 Days)</h2>
      <div class="bg-white dark:bg-zinc-800 p-4 rounded shadow">
        <Line :data="forecastChart" :options="forecastOptions" class="h-64" />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import MoistureCard from '../components/MoistureCard.vue'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement,
  CategoryScale, LinearScale, Filler
} from 'chart.js'
import type { ChartData, ChartOptions } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

interface MoistureData {
  timestamp: string
  devicename: string
  moisture: number
}

const { data: rawData } = await useFetch<MoistureData[]>('http://localhost:3001/moisture-all')

const selectedDevices = ref<string[]>([])
const deviceOptions = computed(() => {
  const names = new Set((rawData.value ?? []).map(d => d.devicename))
  return [...names]
})

onMounted(() => {
  if (deviceOptions.value.length && selectedDevices.value.length === 0) {
    selectedDevices.value = deviceOptions.value.slice(0, 2)
  }
})

const deviceData = computed(() => {
  const grouped: Record<string, MoistureData[]> = {}
  for (const d of rawData.value ?? []) {
    if (!grouped[d.devicename]) grouped[d.devicename] = []
    grouped[d.devicename].push(d)
  }
  return grouped
})

const latestMoisture = computed(() => {
  const latest: Record<string, number> = {}
  for (const device of selectedDevices.value) {
    latest[device] = round(deviceData.value[device]?.[0]?.moisture ?? 0)
  }
  return latest
})

const forecastValues = computed(() => {
  const forecasted: Record<string, number[]> = {}
  for (const device of selectedDevices.value) {
    forecasted[device] = forecast(deviceData.value[device] ?? [])
  }
  return forecasted
})

function round(val: number) {
  return Math.round(val * 10) / 10
}

function statusTag(value: number) {
  if (value < 40) return 'Dry'
  if (value > 70) return 'Too Wet'
  return 'Healthy'
}

const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 50,
      max: 60,
      ticks: {
        stepSize: 0.5,
        callback: value => `${Number(value).toFixed(1)}%`
      },
      title: { display: true, text: 'Moisture (%)' }
    },
    x: {
      title: { display: true, text: 'Time' }
    }
  }
}

function historicalChart(data: MoistureData[], label: string): ChartData<'line'> {
  const sliced = data.slice(0, 100)
  return {
    labels: sliced.map(d => new Date(d.timestamp).toLocaleTimeString()).reverse(),
    datasets: [
      {
        label,
        data: sliced.map(d => d.moisture).reverse(),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(0,0,0,0)',
        pointRadius: 0,
        tension: 0.3,
        fill: false
      }
    ]
  }
}

function forecast(data: MoistureData[]): number[] {
  const y = data.map(d => d.moisture).reverse()
  const x = y.map((_, i) => i)

  const n = x.length
  const xMean = x.reduce((a, b) => a + b, 0) / n
  const yMean = y.reduce((a, b) => a + b, 0) / n

  let num = 0, den = 0
  for (let i = 0; i < n; i++) {
    num += (x[i] - xMean) * (y[i] - yMean)
    den += (x[i] - xMean) ** 2
  }

  const slope = den === 0 ? 0 : num / den
  const intercept = yMean - slope * xMean

  return [...Array(30)].map((_, i) => {
    const xi = n + i
    return round(slope * xi + intercept)
  })
}

const forecastChart = computed<ChartData<'line'>>(() => {
  const labels = [...Array(30)].map((_, i) => `Day ${i + 1}`)
  const datasets = selectedDevices.value.map((device, index) => ({
    label: `${device} Forecast`,
    data: forecastValues.value[device],
    borderColor: `hsl(${index * 40}, 70%, 50%)`,
    backgroundColor: `hsla(${index * 40}, 70%, 50%, 0.1)`,
    fill: true
  }))
  return { labels, datasets }
})

const forecastOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: 50,
      max: 60,
      ticks: {
        stepSize: 0.5,
        callback: value => `${Number(value).toFixed(1)}%`
      },
      title: { display: true, text: 'Moisture (%)' }
    },
    x: {
      title: { display: true, text: 'Day' }
    }
  }
}
</script>
