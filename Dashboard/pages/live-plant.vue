<template>
  <div class="p-6 space-y-8 font-sans">
    <!-- 🔝 Header with Sticky Filter Bar -->
    <div class="sticky top-0 z-40 bg-white dark:bg-zinc-900 shadow-md border-b pb-4">
      <div class="flex flex-wrap justify-between items-center gap-4 mb-4">
        <h1 class="text-3xl font-bold">Soil Moisture Forecast</h1>
        <div class="flex flex-wrap gap-4 items-center justify-end w-full md:w-auto">
          <div class="flex items-center gap-2">
            <label class="font-medium">Time Range:</label>
            <select v-model="selectedRange" class="border rounded p-2 text-sm">
              <option value="short">Short (1 Day)</option>
              <option value="medium">Medium (3 Days)</option>
              <option value="long">Long (7 Days)</option>
            </select>
          </div>
          <!-- 📁 Export Dropdown -->
          <div class="relative inline-block text-left">
            <Menu as="div" class="relative">
              <div>
                <MenuButton class="inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-blue-600 text-white font-semibold hover:bg-blue-700 focus:outline-none">
                  Export Data ▼
                </MenuButton>
              </div>
              <Transition enter="transition ease-out duration-100" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="transition ease-in duration-75" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
                <MenuItems class="origin-top-right absolute right-0 mt-2 w-64 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                  <div class="py-1">
                    <MenuItem>
                      <div class="px-4 py-2 text-sm text-gray-800 font-semibold">Selected Data</div>
                    </MenuItem>
                    <MenuItem>
                      <button @click="downloadSelectedData('csv')" class="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        Export as CSV
                      </button>
                    </MenuItem>
                    <MenuItem>
                      <button @click="downloadSelectedData('xlsx')" class="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        Export as Excel
                      </button>
                    </MenuItem>
                    <hr class="my-1 border-gray-200" />
                    <MenuItem>
                      <div class="px-4 py-2 text-sm text-gray-800 font-semibold">Full Report</div>
                    </MenuItem>
                    <MenuItem>
                      <button @click="downloadFullDashboardReport" class="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
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

      <!-- 🔹 Device Slicer -->
      <div class="w-full max-w-4xl">
        <div class="flex items-center justify-between mb-2">
          <label class="font-medium">Filter by Device(s)</label>
          <span class="text-sm text-gray-500">{{ selected.length }} selected</span>
        </div>
        <div class="flex flex-wrap gap-2 mb-3">
          <span v-for="d in selected" :key="d" class="bg-blue-100 text-blue-800 px-3 py-0.5 rounded-full flex items-center">
            {{ d }}
            <button @click="remove(d)" class="ml-1 text-blue-600 hover:text-blue-800 focus:outline-none">×</button>
          </span>
          <button v-if="selected.length" @click="clearAll" class="ml-auto text-sm text-red-600 hover:underline">
            Clear All
          </button>
        </div>
        <Combobox v-model="selected" multiple>
          <div class="relative">
            <ComboboxButton class="w-full border rounded p-2 bg-white text-left focus:outline-none focus:ring-2 focus:ring-blue-400">
              Add more devices
            </ComboboxButton>
            <Transition enter="transition ease-out duration-100" enter-from="opacity-0" enter-to="opacity-100" leave="transition ease-in duration-75" leave-from="opacity-100" leave-to="opacity-0">
              <ComboboxOptions v-if="options.length" class="absolute z-10 mt-1 w-full bg-white dark:bg-zinc-800 border rounded shadow max-h-60 overflow-auto">
                <ComboboxOption :value="'__ALL__'" class="px-3 py-2 font-medium bg-gray-50 cursor-pointer hover:bg-gray-100" @click.prevent="toggleAll">
                  {{ allSelected ? 'Deselect All' : 'Select All' }}
                </ComboboxOption>
                <ComboboxOption v-for="d in options" :key="d" :value="d" class="px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-700">
                  {{ d }}
                </ComboboxOption>
              </ComboboxOptions>
            </Transition>
          </div>
        </Combobox>
      </div>
    </div>

    <!-- 📊 Moisture Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      <MoistureCard v-for="(device, index) in selected" :key="device + '-latest'" :device="device" :title="`${device} Latest`" :value="latestMoisture[device] ?? 0" :change="round(latestMoisture[device] - forecastValues[device]?.[29])" :changeLabel="'vs forecast'" :status="statusTag(latestMoisture[device])" :isForecast="false" class="transition-shadow hover:shadow-lg" />
      <MoistureCard v-for="(device, index) in selected" :key="device + '-forecast'" :device="device" :title="`${device} Forecast Day 30`" :value="forecastValues[device]?.[29] ?? 0" :change="round(forecastValues[device]?.[29] - latestMoisture[device])" :changeLabel="'vs current'" :status="statusTag(forecastValues[device]?.[29])" :isForecast="true" class="transition-shadow hover:shadow-lg" />
    </div>

    <!-- 📈 Historical Charts -->
    <section v-if="selected.length">
      <h2 class="text-lg font-semibold mt-6 mb-2">Recent Soil Moisture Readings</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="device in selected" :key="device + '-chart'" class="bg-white dark:bg-zinc-800 p-4 rounded shadow-md hover:shadow-lg">
          <div class="max-h-[320px] overflow-hidden">
            <Line :id="`historical-${device}`" :data="historicalChart(deviceData[device] ?? [], device)" :options="getChartOptions()" class="h-48" />
          </div>
          <div class="flex justify-between items-center mt-2 text-sm">
            <span class="text-gray-500">Chart: Historical - {{ device }}</span>
            <button @click="downloadChartImage(`historical-${device}`, `${device}-historical.png`)" class="text-blue-600 hover:underline">⬇ Download</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 📉 Forecast Chart -->
    <section v-if="forecastChart">
      <h2 class="text-lg font-semibold mt-6 mb-2">Moisture Forecast (Next 30 Days)</h2>
      <div class="bg-white dark:bg-zinc-800 p-4 rounded shadow-md hover:shadow-lg">
        <div class="max-h-[340px] overflow-hidden">
          <Line id="forecast-chart" :data="forecastChart" :options="forecastOptions" class="h-48" />
        </div>
        <div class="flex justify-between items-center mt-2 text-sm">
          <span class="text-gray-500">Chart: Forecast (30 Days)</span>
          <button @click="downloadChartImage('forecast-chart', 'forecast-30day.png')" class="text-blue-600 hover:underline">⬇ Download</button>
        </div>
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
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Transition } from 'vue'
import * as XLSX from 'xlsx-js-style'


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
