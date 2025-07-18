<template>
  <div class="p-6 space-y-8">
    <h1 class="text-2xl font-bold mb-4">Soil Moisture Forecast</h1>

    <!-- 🔹 Device Slicer -->
<div class="w-full max-w-xl">
  <!-- Label + live‑count -->
  <div class="flex items-center justify-between mb-2">
    <label class="font-medium">Filter by Device(s)</label>
    <span class="text-sm text-gray-500">{{ selected.length }} selected</span>
  </div>

  <!-- Selected chips -->
  <div class="flex flex-wrap gap-2 mb-3">
    <span
      v-for="d in selected"
      :key="d"
      class="bg-blue-100 text-blue-800 px-3 py-0.5 rounded-full flex items-center"
    >
      {{ d }}
      <button
        @click="remove(d)"
        class="ml-1 text-blue-600 hover:text-blue-800 focus:outline-none"
      >
        ×
      </button>
    </span>

    <button
      v-if="selected.length"
      @click="clearAll"
      class="ml-auto text-sm text-red-600 hover:underline"
    >
      Clear All
    </button>
  </div>

  <!-- Combobox -->
  <Combobox v-model="selected" multiple>
    <div class="relative">
      <ComboboxInput
        v-model="query"
        placeholder="Type to search devices…"
        class="w-full border rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      />

      <Transition
        enter="transition ease-out duration-100"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="transition ease-in duration-75"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <ComboboxOptions
          v-if="options.length"
          class="absolute z-10 mt-1 w-full bg-white dark:bg-zinc-800 border rounded shadow max-h-60 overflow-auto"
        >
          <!-- Select‑All / Deselect‑All toggle -->
          <ComboboxOption
            :value="'__ALL__'"
            class="px-3 py-2 font-medium bg-gray-50 cursor-pointer hover:bg-gray-100"
            @click.prevent="toggleAll"
          >
            {{ allSelected ? 'Deselect All' : 'Select All' }}
          </ComboboxOption>

          <!-- Individual devices -->
          <ComboboxOption
            v-for="d in options"
            :key="d"
            :value="d"
            class="px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-700"
          >
            {{ d }}
          </ComboboxOption>
        </ComboboxOptions>
      </Transition>
    </div>
  </Combobox>
</div>

    <!-- Moisture Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MoistureCard
        v-for="(device, index) in selected"
        :key="device + '-latest'"
        :device="device"
        :title="`${device} Latest`"
        :value="latestMoisture[device] ?? 0"
        :change="round(latestMoisture[device] - forecastValues[device]?.[29])"
        :changeLabel="'vs forecast'"
        :status="statusTag(latestMoisture[device])"
      />
      <MoistureCard
        v-for="(device, index) in selected"
        :key="device + '-forecast'"
        :device="device"
        :title="`${device} Forecast Day 30`"
        :value="forecastValues[device]?.[29] ?? 0"
        :change="round(forecastValues[device]?.[29] - latestMoisture[device])"
        :changeLabel="'vs current'"
        :status="statusTag(forecastValues[device]?.[29])"
      />
    </div>

    <!-- Historical Charts -->
    <section v-if="selected.length">
      <h2 class="text-lg font-semibold mb-2">Recent Soil Moisture Readings</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="device in selected"
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

import {
  Combobox,
  ComboboxInput,
  ComboboxOptions,
  ComboboxOption,
} from '@headlessui/vue'        // npm i @headlessui/vue

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

interface MoistureData {
  timestamp: string
  devicename: string
  moisture: number
}

/* ── reactive state ───────────────────────────── */
const selected  = ref<string[]>([])      // replaces selectedDevices in template
const query     = ref('')

/* unique device list from your existing rawData */
const allDevices = computed(() =>
  Array.from(
    new Set(
      (rawData.value ?? [])
        .map(r => r.devicename)
        .filter(name => /plant pot/i.test(name))   // ← keep only “Plant Pot”
    )
  ).sort()
)

/* live‑filtered dropdown list (excludes already‑selected) */
const options = computed(() => {
  const q = query.value.toLowerCase().trim()
  return allDevices.value
    .filter(d => !selected.value.includes(d))
    .filter(d => !q || d.toLowerCase().includes(q))
})

/* helper flags & actions */
const allSelected = computed(() =>
  selected.value.length === allDevices.value.length
)

function toggleAll() {
  selected.value = allSelected.value ? [] : [...allDevices.value]
}

function remove(d: string) {
  selected.value = selected.value.filter(x => x !== d)
}

function clearAll() {
  selected.value = []
  query.value    = ''
}

/* optional: pre‑select first two on mount */
onMounted(() => {
  if (!selected.value.length && allDevices.value.length) {
    selected.value = allDevices.value.slice(0, 2)
  }
})

const { data: rawData } = await useFetch<MoistureData[]>(
  'http://localhost:3001/moisture-all',
  { query: { bucket_min: 10, window_min: 180 } }
)

const deviceOptions = computed(() => {
  const names = new Set((rawData.value ?? []).map(d => d.devicename))
  return [...names]
})

onMounted(() => {
  if (deviceOptions.value.length && selected.value.length === 0) {
    selected.value = deviceOptions.value.slice(0, 2)
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
  for (const device of selected.value) {
    latest[device] = round(deviceData.value[device]?.[0]?.moisture ?? 0)
  }
  return latest
})

const forecastValues = computed(() => {
  const forecasted: Record<string, number[]> = {}
  for (const device of selected.value) {
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
      min: 48,
      max: 65,
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
  const y = data.map(d => d.moisture)
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

/* ─── 1) 30‑day datasets + global y‑min / y‑max ───────────────────────── */
const forecastChart = computed(() => {
  const labels = [...Array(30)].map((_, i) => `Day ${i + 1}`)

  const datasets = selected.value.map((device, idx) => ({
    label : `${device} Forecast`,
    data  : forecastValues.value[device],
    borderColor     : `hsl(${idx * 40}, 70%, 50%)`,
    backgroundColor : `hsla(${idx * 40}, 70%, 50%, 0.1)`,
    fill            : true,
    pointRadius     : 3
  }))

  // find global min / max across all devices
  const allVals = datasets.flatMap(ds => ds.data)
  const pad     = 0.3                               // % points padding
  const yMin    = Math.floor(Math.min(...allVals) - pad)
  const yMax    = Math.ceil (Math.max(...allVals) + pad)

  // return both the data and the limits
  return { labels, datasets, yMin, yMax }
})

/* ─── 2) options that use those limits ────────────────────────────────── */
const forecastOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min : forecastChart.value.yMin,
      max : forecastChart.value.yMax,
      ticks: { callback: v => `${v}%` },
      title: { display: true, text: 'Moisture (%)' }
    },
    x: {
      title: { display: true, text: 'Day' }
    }
  }
}))
</script>
