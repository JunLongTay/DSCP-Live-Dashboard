<template>
  <div class="relative">
    <!-- Blurred plant background with black overlay -->
    <img src="/plant.jpeg" alt="Plant background" class="fixed top-0 left-0 w-full h-full object-cover z-0 blur-md opacity-70 pointer-events-none select-none" />
    <div class="fixed top-0 left-0 w-full h-full bg-black/80 z-10 pointer-events-none" />
    <!-- Sidebar absolutely positioned, flush with all edges, above overlay -->
    <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30 border-r-2 border-orange-800 shadow-xl">
      <Sidebar />
    </div>
    <!-- Main content, margin-left for sidebar, above overlay -->
    <div class="relative z-20 flex flex-col">
      <!-- 🔝 Header with Sticky Filter Bar -->
      <div class="sticky z-40 shadow-md border-b border-orange-700 pb-4 mb-8 ">
        <div class="flex flex-wrap justify-between items-center gap-6 mb-4">
          <h1 class="text-3xl font-bold text-orange-400">Soil Moisture Forecast</h1>
          <div class="flex flex-wrap gap-4 items-center justify-end w-full md:w-auto">
            <div class="flex items-center gap-2">
              <label class="font-medium text-orange-300">Time Range:</label>
              <select v-model="selectedRange" class="border border-orange-500 rounded p-2 text-sm bg-zinc-900 text-orange-200">
                <option value="short">Short (1 Day)</option>
                <option value="medium">Medium (3 Days)</option>
                <option value="long">Long (7 Days)</option>
              </select>
            </div>
            <!-- 📁 Export Dropdown -->
            <div class="relative inline-block text-left">
              <Menu as="div" class="relative">
                <div>
                  <MenuButton as="template">
                    <Button variant="default">
                      Export Data ▼
                    </Button>
                  </MenuButton>
                </div>
                <Transition enter="transition ease-out duration-100" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="transition ease-in duration-75" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
                  <MenuItems class="origin-top-right absolute right-0 mt-2 w-64 rounded-md shadow-lg bg-zinc-900 ring-1 ring-orange-700 ring-opacity-70 focus:outline-none z-50">
                    <div class="py-1">
                      <MenuItem>
                        <div class="px-4 py-2 text-sm text-orange-200 font-semibold">Selected Data</div>
                      </MenuItem>
                      <MenuItem>
                        <button @click="downloadSelectedData('csv')" class="w-full px-4 py-2 text-sm text-orange-100 hover:bg-orange-800">
                          Export as CSV
                        </button>
                      </MenuItem>
                      <MenuItem>
                        <button @click="downloadSelectedData('xlsx')" class="w-full px-4 py-2 text-sm text-orange-100 hover:bg-orange-800">
                          Export as Excel
                        </button>
                      </MenuItem>
                      <hr class="my-1 border-orange-700" />
                      <MenuItem>
                        <div class="px-4 py-2 text-sm text-orange-200 font-semibold">Full Report</div>
                      </MenuItem>
                      <MenuItem>
                        <button @click="downloadFullDashboardReport" class="w-full px-4 py-2 text-sm text-orange-100 hover:bg-orange-800">
                          Download All Charts + Summary
                        </button>
                      </MenuItem>
                    </div>
                  </MenuItems>
                </Transition>
              </Menu>
            </div>
          </div>
        </div>
      </div>

      <!-- 🔹 Device Slicer -->
      <section class="  pl-0 mb-10">
        <div class="flex items-center justify-between mb-2">
          <label class="font-medium text-orange-300">Filter by Device(s)</label>
          <span class="text-sm text-orange-200">{{ selected.length }} selected</span>
        </div>
        <!-- Selected chips -->
        <div class="flex flex-wrap gap-2 mb-3">
          <span
            v-for="d in selected"
            :key="d"
            class="bg-orange-900 text-orange-200 px-3 py-0.5 rounded-full flex items-center animate-fade-in"
          >
            {{ d }}
            <button
              @click="remove(d)"
              class="ml-1 text-orange-400 hover:text-orange-200 focus:outline-none transition-colors duration-200"
            >
              ×
            </button>
          </span>
          <button
            v-if="selected.length"
            @click="clearAll"
            class="ml-auto text-sm text-orange-400 hover:underline"
          >
            Clear All
          </button>
        </div>
        <!-- Modal Picker Trigger -->
        <button @click="showDeviceModal = true" class="w-full border border-orange-500 rounded p-2 bg-zinc-900 text-left text-orange-200 focus:outline-none focus:ring-2 focus:ring-orange-400 transition-colors duration-200">
          Select Devices
        </button>
        <!-- Modal Picker -->
        <transition name="fade">
          <div v-if="showDeviceModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
            <div class="bg-zinc-900 border border-orange-500 rounded-lg shadow-lg p-6 w-full max-w-lg relative">
              <h2 class="text-lg font-bold mb-4 text-orange-400 font-roboto-slab">Select Devices</h2>
              <input v-model="deviceSearch" type="text" placeholder="Search devices..." class="w-full mb-3 p-2 rounded border border-orange-500 bg-black text-orange-100 focus:outline-none focus:ring-2 focus:ring-orange-400" />
              <div class="flex justify-between mb-2">
                <button @click="modalSelectAll" class="text-sm text-orange-400 hover:underline">Select All</button>
                <button @click="modalClearAll" class="text-sm text-orange-400 hover:underline">Clear All</button>
              </div>
              <div class="max-h-60 overflow-y-auto mb-4">
                <div v-if="deviceNamesLoading" class="text-orange-300 text-sm py-2 flex items-center gap-2">
                  <span class="loader"></span> Loading devices...
                </div>
                <template v-else>
                  <label v-for="d in filteredDevices" :key="d" class="flex items-center gap-2 py-1 cursor-pointer text-orange-100 hover:text-orange-400">
                    <input type="checkbox" :value="d" v-model="modalSelected" class="accent-orange-500" />
                    {{ d }}
                  </label>
                  <div v-if="!filteredDevices.length" class="text-orange-300 text-sm py-2">No devices found.</div>
                </template>
              </div>
              <div class="flex justify-end gap-3 mt-4">
                <button @click="showDeviceModal = false" class="px-4 py-2 rounded bg-zinc-800 text-orange-200 hover:bg-zinc-700">Cancel</button>
                <button @click="confirmDeviceModal" class="px-4 py-2 rounded bg-orange-600 text-white font-semibold hover:bg-orange-700">Confirm</button>
              </div>
              <button @click="showDeviceModal = false" class="absolute top-2 right-2 text-orange-400 hover:text-orange-200 text-xl">×</button>
            </div>
          </div>
        </transition>
      </section>

      <!-- 📊 Moisture Summary Cards -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Moisture Summary</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          <MoistureCard v-for="(device, index) in selected" :key="device + '-latest'" :device="device" :title="`${device} Latest`" :value="latestMoisture[device] ?? 0" :change="round(latestMoisture[device] - forecastValues[device]?.[29])" :changeLabel="'vs forecast'" :status="statusTag(latestMoisture[device])" :isForecast="false" class="transition-shadow hover:shadow-lg bg-zinc-900 border border-orange-500 text-orange-100 p-4" />
          <MoistureCard v-for="(device, index) in selected" :key="device + '-forecast'" :device="device" :title="`${device} Forecast Day 30`" :value="forecastValues[device]?.[29] ?? 0" :change="round(forecastValues[device]?.[29] - latestMoisture[device])" :changeLabel="'vs current'" :status="statusTag(forecastValues[device]?.[29])" :isForecast="true" class="transition-shadow hover:shadow-lg bg-zinc-900 border border-orange-500 text-orange-100 p-4" />
        </div>
      </section>

      <!-- 📈 Historical Charts -->
      <section v-if="selected.length" class="mb-12">
        <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Recent Soil Moisture Readings</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 justify-start items-start w-full">
          <div v-for="(device, idx) in selected" :key="device + '-chart'" class="bg-zinc-900 p-8 rounded shadow-md hover:shadow-lg border border-orange-500 flex flex-col gap-2">
            <div class="max-h-[320px] overflow-hidden">
              <Line :id="`historical-${device}`" :data="historicalChart(deviceData[device] ?? [], device, idx)" :options="getChartOptions()" class="h-48" />
            </div>
            <div class="flex justify-between items-center mt-2 text-sm">
              <span class="text-orange-200">Chart: Historical - {{ device }}</span>
              <button @click="downloadChartImage(`historical-${device}`, `${device}-historical.png`)" class="text-orange-400 hover:underline">⬇ Download</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 📉 Forecast Chart -->
      <section v-if="forecastChart" class="w-full mb-8 flex flex-col items-start">
        <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Moisture Forecast (Next 30 Days)</h2>
        <div class="bg-zinc-900 p-8 rounded shadow-md hover:shadow-lg border border-orange-500 w-full flex flex-col gap-2 max-w-full">
          <div class="max-h-[340px] overflow-hidden">
            <Line id="forecast-chart" :data="forecastChart" :options="forecastOptions" class="h-48 w-full" />
          </div>
          <div class="flex justify-between items-center mt-2 text-sm">
            <span class="text-orange-200">Chart: Forecast (30 Days)</span>
            <button @click="downloadChartImage('forecast-chart', 'forecast-30day.png')" class="text-orange-400 hover:underline">⬇ Download</button>
          </div>
        </div>
      </section>
    </div>
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
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Transition } from 'vue'
import * as XLSX from 'xlsx-js-style'

import Sidebar from '../components/Sidebar/index.vue'
import { Button } from '@/components/ui/button'

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

/* ── Loading State ───────────────────────────── */
const isLoading = ref(true)

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
/* ── Download Data (CSV Only) ───────────────── */
function downloadCSV() {
  if (!rawData.value.length || !selected.value.length) return;

  const header = ['Timestamp', 'Device Name', 'Moisture (%)'];
  const rows = rawData.value
    .filter(d => selected.value.includes(d.devicename))
    .map(d => [
      new Date(d.timestamp).toISOString(),
      d.devicename,
      d.moisture.toFixed(1)
    ]);

  if (!rows.length) return;

  const csvContent =
    [header, ...rows]
      .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(','))
      .join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'selected_moisture_data.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/* ── Download Selected Data ───────────────── */
function downloadSelectedData(format: 'csv' | 'xlsx') {
  if (!rawData.value.length || !selected.value.length) return;

  const filtered = rawData.value.filter(d => selected.value.includes(d.devicename));
  if (!filtered.length) return;

  const rows = filtered.map(d => ({
    Timestamp: new Date(d.timestamp).toISOString(),
    'Device Name': d.devicename,
    'Moisture (%)': d.moisture.toFixed(1)
  }));

  if (format === 'csv') {
    const csv = [
      Object.keys(rows[0]),
      ...rows.map(row => Object.values(row))
    ]
      .map(r => r.map(val => `"${val}"`).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'selected_moisture_data.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else {
    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Selected Moisture Data');
    XLSX.writeFile(workbook, 'selected_moisture_data.xlsx');
  }
}

async function downloadFullDashboardReport(): Promise<void> {
  const wb = XLSX.utils.book_new();

  /* 🟢 Summary Sheet */
  const summary: any[] = selected.value.map(device => {
    const latest = latestMoisture.value[device] ?? 0;
    const forecast = forecastValues.value[device]?.[29] ?? 0;
    return {
      'Device': device,
      'Latest Moisture (%)': latest.toFixed(1),
      'Forecast Day 30 Moisture (%)': forecast.toFixed(1),
      'Change (%)': (forecast - latest).toFixed(1)
    };
  });
  const summarySheet = XLSX.utils.json_to_sheet(summary);
  XLSX.utils.book_append_sheet(wb, summarySheet, 'Summary');

  /* 📈 Historical Data Sheet */
  const historical: any[] = [];
  for (const device of selected.value) {
    for (const d of deviceData.value[device] ?? []) {
      historical.push({
        'Timestamp': new Date(d.timestamp).toISOString(),
        'Device': device,
        'Moisture (%)': d.moisture.toFixed(1)
      });
    }
  }
  const historicalSheet = XLSX.utils.json_to_sheet(historical);
  XLSX.utils.book_append_sheet(wb, historicalSheet, 'Historical');

  /* 🔮 Forecast Data Sheet */
  const forecast: any[] = [];
  for (const device of selected.value) {
    forecastValues.value[device]?.forEach((val, i) => {
      forecast.push({
        'Device': device,
        'Day': i + 1,
        'Forecast Moisture (%)': val.toFixed(1)
      });
    });
  }
  const forecastSheet = XLSX.utils.json_to_sheet(forecast);
  XLSX.utils.book_append_sheet(wb, forecastSheet, 'Forecast');

  /* 💾 Save Workbook */
  XLSX.writeFile(wb, 'soil_moisture_dashboard_report.xlsx');
}



/* ── Image Download ───────────────────────────── */
function downloadChartImage(canvasId: string, filename: string) {
  const canvas = document.getElementById(canvasId) as HTMLCanvasElement
  if (!canvas) {
    alert('Chart not found.')
    return
  }

  const link = document.createElement('a')
  link.download = filename
  link.href = canvas.toDataURL('image/png')
  link.click()
}

// --- Device Names (faster device picker) ---
const deviceNames = ref<string[]>([])
const deviceNamesLoading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:3001/device-names')
    deviceNames.value = await res.json()
  } catch (e) {
    deviceNames.value = []
  } finally {
    deviceNamesLoading.value = false
  }
})

/* ── Device Management ───────────────────────────── */
const allDevices = computed(() => deviceNames.value)

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
const chartPalette = [
  '#ff8800', // orange
  '#1e90ff', // blue
  '#ffd600', // yellow
  '#e91e63', // pink
  '#4caf50', // green
  '#9c27b0', // purple
]

function historicalChart(data: MoistureData[], label: string, idx = 0): ChartData<'line'> {
  const sliced = data.slice(0, 100)
  const format: Intl.DateTimeFormatOptions = selectedRange.value === 'long'
    ? { weekday: 'short', month: 'short', day: 'numeric' }
    : { hour: '2-digit', minute: '2-digit' }

  return {
    labels: sliced.map(d => new Date(d.timestamp).toLocaleString(undefined, format)).reverse(),
    datasets: [{
      label,
      data: sliced.map(d => d.moisture).reverse(),
      borderColor: chartPalette[idx % chartPalette.length],
      backgroundColor: chartPalette[idx % chartPalette.length] + '33',
      pointRadius: 3,
      pointBackgroundColor: chartPalette[idx % chartPalette.length],
      pointBorderColor: chartPalette[idx % chartPalette.length],
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
          color: '#ff8800',
          font: { size: 16, weight: 'bold' },
          callback: value => `${Number(value).toFixed(1)}%`
        },
        title: { display: true, text: 'Moisture (%)', color: '#ff8800', font: { size: 16, weight: 'bold' } }
      },
      x: {
        ticks: {
          color: '#ff8800',
          font: { size: 14, weight: 'bold' }
        },
        title: { display: true, text: 'Time', color: '#ff8800', font: { size: 14, weight: 'bold' } }
      }
    }
  }
}


const forecastChart = computed(() => {
  const labels = [...Array(30)].map((_, i) => `Day ${i + 1}`)

  const datasets = selected.value.map((device, idx) => ({
    label: `${device} Forecast`,
    data: forecastValues.value[device],
    borderColor: chartPalette[idx % chartPalette.length],
    backgroundColor: chartPalette[idx % chartPalette.length] + '33',
    fill: true,
    pointRadius: 3,
    pointBackgroundColor: chartPalette[idx % chartPalette.length],
    pointBorderColor: chartPalette[idx % chartPalette.length],
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

// Modal picker state
const showDeviceModal = ref(false)
const deviceSearch = ref('')
const modalSelected = ref<string[]>([])

const filteredDevices = computed(() =>
  options.value.filter(d => d.toLowerCase().includes(deviceSearch.value.toLowerCase()))
)

function modalSelectAll() {
  modalSelected.value = [...options.value]
}
function modalClearAll() {
  modalSelected.value = []
}
function confirmDeviceModal() {
  selected.value = Array.from(new Set([...selected.value, ...modalSelected.value]))
  showDeviceModal.value = false
}

watchEffect(() => {
  // Keep modalSelected in sync with current selection when opening modal
  if (showDeviceModal.value) {
    modalSelected.value = [...selected.value]
  }
})

// Set loading to false when all main data is loaded
watchEffect(() => {
  if (rawData.value.length || (Array.isArray(rawData.value) && rawData.value.length === 0)) {
    isLoading.value = false
  }
})

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Slab:wght@700&display=swap');

.font-inter {
  font-family: 'Inter', Arial, sans-serif;
}
.font-roboto-slab {
  font-family: 'Roboto Slab', serif;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'Roboto Slab', serif;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.loader {
  border: 6px solid #222;
  border-top: 6px solid #ff8800;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
</style>