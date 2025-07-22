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

  <Combobox v-model="selected" multiple>
    <div class="relative">
      <!-- Button that toggles the dropdown -->
      <ComboboxButton class="w-full border rounded p-2 bg-white text-left focus:outline-none focus:ring-2 focus:ring-blue-400">
        Add more devices
      </ComboboxButton>

      <!-- Dropdown options -->
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
          <!-- Select All / Deselect All toggle -->
          <ComboboxOption
            :value="'__ALL__'"
            class="px-3 py-2 font-medium bg-gray-50 cursor-pointer hover:bg-gray-100"
            @click.prevent="toggleAll"
        >
            {{ allSelected ? 'Deselect All' : 'Select All' }}
          </ComboboxOption>

          <!-- Devices -->
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

<!-- Moisture Summary Cards: 4 columns on md+ -->
<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
  <MoistureCard
    v-for="(device, index) in selected"
    :key="device + '-latest'"
    :device="device"
    :title="`${device} Latest`"
    :value="latestMoisture[device] ?? 0"
    :change="round(latestMoisture[device] - forecastValues[device]?.[29])"
    :changeLabel="'vs forecast'"
    :status="statusTag(latestMoisture[device])"
    :isForecast="false"
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
    :isForecast="true"
  />
</div>




  <!-- Time Range Selector -->
    <div class="flex gap-3 items-center mb-4">
      <label class="font-medium">Time Range:</label>
      <select v-model="selectedRange" class="border rounded p-2 text-sm">
        <option value="short">Short (1 Day)</option>
        <option value="medium">Medium (3 Days)</option>
        <option value="long">Long (7 Days)</option>
      </select>
    </div>

  <!-- 🔽 Download CSV Button -->
    <div class="mt-4">
      <button
        @click="downloadCSV"
        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded"
      >
        Download Moisture Data as CSV
      </button>
    </div>
    
    <!-- Format Toggle + Button -->
    <div class="flex items-center gap-3 mt-4">
      <select v-model="downloadFormat" class="border rounded p-2 text-sm">
        <option value="csv">CSV</option>
        <option value="xlsx">Excel</option>
      </select>
      <button
        @click="downloadSelectedData"
        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded"
      >
        Download Selected Moisture Data
      </button>
    </div>

<!-- Full Report Button -->
    <div class="mt-3">
      <button
        @click="downloadFullDashboardReport"
        class="bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-2 rounded"
      >
        Download Full Dashboard Report (Excel)
      </button>
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
          <Line :data="historicalChart(deviceData[device] ?? [], device)" :options="getChartOptions()" class="h-60" />
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
import { ref, computed, onMounted, watchEffect } from 'vue'
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
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
} from '@headlessui/vue'
import * as XLSX from 'xlsx'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

interface MoistureData {
  timestamp: string
  devicename: string
  moisture: number
}

/* ── Config & Time Range ───────────────────────────── */
const selectedRange = ref<'short' | 'medium' | 'long'>('short')
const timeConfigs = {
  short:  { bucket_min: 60, window_min: 1440 },
  medium: { bucket_min: 180, window_min: 4320 },
  long:   { bucket_min: 1440, window_min: 10080 }
}

/* ── State ───────────────────────────── */
const selected = ref<string[]>([])
const query = ref('')
const rawData = ref<MoistureData[]>([])

/* ── Fetch Data ───────────────────────────── */
watchEffect(async () => {
  const config = timeConfigs[selectedRange.value]
  const { data } = await useFetch<MoistureData[]>(
    'http://localhost:3001/moisture-all',
    { query: config }
  )
  rawData.value = data.value ?? []
})

/* ── Download Data ───────────────────────────── */
function downloadCSV() {
  if (!rawData.value.length || !selected.value.length) return

  const header = ['Timestamp', 'Device Name', 'Moisture (%)']
  const rows = rawData.value
    .filter(d => selected.value.includes(d.devicename))
    .map(d => [
      new Date(d.timestamp).toISOString(),
      d.devicename,
      d.moisture.toFixed(1)
    ])

  if (!rows.length) return

  const csvContent =
    [header, ...rows]
      .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(','))
      .join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'selected_moisture_data.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
const downloadFormat = ref<'csv' | 'xlsx'>('csv')

function downloadSelectedData() {
  if (!rawData.value.length || !selected.value.length) return

  const filtered = rawData.value.filter(d => selected.value.includes(d.devicename))
  if (!filtered.length) return

  const rows = filtered.map(d => ({
    Timestamp: new Date(d.timestamp).toISOString(),
    'Device Name': d.devicename,
    'Moisture (%)': d.moisture.toFixed(1)
  }))

  if (downloadFormat.value === 'csv') {
    const csv = [
      Object.keys(rows[0]),
      ...rows.map(row => Object.values(row))
    ]
      .map(r => r.map(val => `"${val}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'selected_moisture_data.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } else {
    const worksheet = XLSX.utils.json_to_sheet(rows)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Selected Moisture Data')

    XLSX.writeFile(workbook, 'selected_moisture_data.xlsx')
  }
}

function downloadFullDashboardReport() {
  const summary: any[] = []
  for (const device of selected.value) {
    const latest = latestMoisture.value[device]
    const forecast = forecastValues.value[device]?.[29]
    summary.push({
      'Device': device,
      'Latest Moisture (%)': latest,
      'Forecast Day 30 Moisture (%)': forecast,
      'Change (%)': round(forecast - latest)
    })
  }

  const allHistorical: any[] = []
  for (const device of selected.value) {
    for (const d of deviceData.value[device] ?? []) {
      allHistorical.push({
        'Timestamp': new Date(d.timestamp).toISOString(),
        'Device': device,
        'Moisture (%)': d.moisture.toFixed(1)
      })
    }
  }

  const forecastData: any[] = []
  for (const device of selected.value) {
    forecastValues.value[device]?.forEach((val, i) => {
      forecastData.push({
        'Device': device,
        'Day': i + 1,
        'Forecast Moisture (%)': val
      })
    })
  }

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(summary), 'Summary')
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(allHistorical), 'Historical')
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(forecastData), 'Forecast')

  XLSX.writeFile(wb, 'soil_moisture_dashboard_report.xlsx')
}

/* ── Device Management ───────────────────────────── */
const allDevices = computed(() =>
  Array.from(new Set(
    (rawData.value ?? [])
      .map(r => r.devicename)
      .filter(name => /plant pot/i.test(name))
  )).sort()
)

const options = computed(() =>
  allDevices.value.filter(d => !selected.value.includes(d))
)

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
  query.value = ''
}

onMounted(() => {
  if (!selected.value.length && allDevices.value.length) {
    selected.value = allDevices.value.slice(0, 2)
  }
})

/* ── Data Structuring ───────────────────────────── */
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

/* ── Utility Functions ───────────────────────────── */
function round(val: number) {
  return Math.round(val * 10) / 10
}

function statusTag(value: number) {
  if (value < 40) return 'Dry'
  if (value > 70) return 'Too Wet'
  return 'Healthy'
}

function forecast(data: MoistureData[]): number[] {
  const yRaw = data.map(d => d.moisture)
  if (yRaw.length === 0) return Array(30).fill(0)

  const smoothed: number[] = []
  const window = 5
  for (let i = 0; i < yRaw.length; i++) {
    const start = Math.max(0, i - window + 1)
    const avg = yRaw.slice(start, i + 1).reduce((a, b) => a + b, 0) / (i - start + 1)
    smoothed.push(avg)
  }

  const x = smoothed.map((_, i) => i)
  const y = smoothed
  const n = x.length
  const xMean = x.reduce((a, b) => a + b) / n
  const yMean = y.reduce((a, b) => a + b) / n

  let num = 0, den = 0
  for (let i = 0; i < n; i++) {
    num += (x[i] - xMean) * (y[i] - yMean)
    den += (x[i] - xMean) ** 2
  }

  const slope = den === 0 ? 0 : num / den
  const intercept = yMean - slope * xMean

  return [...Array(30)].map((_, i) => {
    const xi = n + i
    const trend = slope * xi + intercept
    const jitter = (Math.random() - 0.5) * 0.4
    return round(trend + jitter)
  })
}

/* ── Chart Options ───────────────────────────── */
function historicalChart(data: MoistureData[], label: string): ChartData<'line'> {
  const sliced = data.slice(0, 100)
  const format: Intl.DateTimeFormatOptions = selectedRange.value === 'long'
    ? { weekday: 'short', month: 'short', day: 'numeric' }
    : { hour: '2-digit', minute: '2-digit' }

  return {
    labels: sliced.map(d => new Date(d.timestamp).toLocaleString(undefined, format)).reverse(),
    datasets: [{
      label,
      data: sliced.map(d => d.moisture).reverse(),
      borderColor: 'rgb(54, 162, 235)',
      backgroundColor: 'rgba(0,0,0,0)',
      pointRadius: 0,
      tension: 0.3,
      fill: false
    }]
  }
}

function getChartOptions(): ChartOptions<'line'> {
  return {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        min: moistureYAxisRange.value.min,
        max: moistureYAxisRange.value.max,
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
}


const forecastChart = computed(() => {
  const labels = [...Array(30)].map((_, i) => `Day ${i + 1}`)

  const datasets = selected.value.map((device, idx) => ({
    label: `${device} Forecast`,
    data: forecastValues.value[device],
    borderColor: `hsl(${idx * 40}, 70%, 50%)`,
    backgroundColor: `hsla(${idx * 40}, 70%, 50%, 0.1)`,
    fill: true,
    pointRadius: 3
  }))

  const allVals = datasets.flatMap(ds => ds.data)
  const pad = 0.3
  const yMin = Math.floor(Math.min(...allVals) - pad)
  const yMax = Math.ceil(Math.max(...allVals) + pad)

  return { labels, datasets, yMin, yMax }
})

const forecastOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      min: forecastChart.value.yMin,
      max: forecastChart.value.yMax,
      ticks: { callback: v => `${v}%` },
      title: { display: true, text: 'Moisture (%)' }
    },
    x: {
      title: { display: true, text: 'Day' }
    }
  }
}))

const moistureYAxisRange = computed(() => {
  const allValues: number[] = []

  for (const device of selected.value) {
    const readings = deviceData.value[device] ?? []
    for (const d of readings) {
      allValues.push(d.moisture)
    }
  }

  if (!allValues.length) return { min: 0, max: 100 }

  const min = Math.min(...allValues)
  const max = Math.max(...allValues)

  const pad = 2 // percentage points
  return {
    min: Math.floor(min - pad),
    max: Math.ceil(max + pad)
  }
})

</script>
