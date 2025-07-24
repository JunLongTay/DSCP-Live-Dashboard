<template>
  <div class="relative min-h-screen">
    <!-- BG + overlay -->
    <img
      src="/home.jpg"
      alt="Background"
      class="fixed top-0 left-0 w-full h-full object-cover z-0 blur-md opacity-70 pointer-events-none select-none"
      onerror="this.style.display='none'"
    />
    <div class="fixed top-0 left-0 w-full h-full bg-black/80 z-10 pointer-events-none" />

    <!-- Sidebar -->
    <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30 border-r-2 border-orange-800 shadow-xl">
      <Sidebar />
    </div>

    <!-- Main -->
    <div class="min-h-screen relative z-20 flex flex-col gap-10 px-6 md:px-12 py-8">

      <!-- 🔹 Device Slicer -->
      <section class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-4">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-xl font-semibold text-orange-400">Soil Moisture Forecast</h2>
          <Button
            @click="downloadFullReport"
            class=""
          >
            Download All Charts + Summary
          </Button>
        </div>

        <div class="w-full max-w-xl">
          <div class="flex items-center justify-between mb-2">
            <label class="font-medium  text-orange-300">Filter by Device(s)</label>
            <span class="text-sm text-gray-400">{{ selected.length }} selected</span>
          </div>

          <!-- Chips -->
          <div class="flex flex-wrap gap-2 mb-3">
            <span
              v-for="d in selected"
              :key="d"
              class="bg-blue-100 text-blue-800 px-3 py-0.5 rounded-full flex items-center"
            >
              {{ d }}
              <Button
                @click="remove(d)"
                variant="ghost"
                class="ml-1"
              >
                ×
              </Button>
            </span>

            <Button
              v-if="selected.length"
              @click="clearAll"
              variant="destructive"
              class="ml-auto text-sm"
            >
              Clear All
            </Button>
          </div>

          <!-- Combobox -->
          <Combobox v-model="selected" multiple>
            <div class="relative">
              <ComboboxButton
                class="w-full border rounded p-2 bg-white dark:bg-zinc-800 text-left focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                Add more devices
              </ComboboxButton>

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
                  <ComboboxOption
                    :value="'__ALL__'"
                    class="px-3 py-2 font-medium bg-gray-50 dark:bg-zinc-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-600"
                    @click.prevent="toggleAll"
                  >
                    {{ allSelected ? 'Deselect All' : 'Select All' }}
                  </ComboboxOption>

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
      </section>

      <!-- 🔹 Average NPK Levels -->
      <section class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6">
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Average NPK Levels</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Nitrogen</h3>
            <p class="text-3xl font-bold text-orange-400">{{ avg.nitrogen }} {{ NPK_UNIT }}</p>
            <span class="mt-2 inline-block px-2 py-0.5 text-xs font-medium rounded"
                  :class="statusClass(npkStatus('nitrogen', avg.nitrogen))">
              {{ npkStatus('nitrogen', avg.nitrogen) }}
            </span>
          </div>

          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Phosphorus</h3>
            <p class="text-3xl font-bold text-orange-400">{{ avg.phosphorus }} {{ NPK_UNIT }}</p>
            <span class="mt-2 inline-block px-2 py-0.5 text-xs font-medium rounded"
                  :class="statusClass(npkStatus('phosphorus', avg.phosphorus))">
              {{ npkStatus('phosphorus', avg.phosphorus) }}
            </span>
          </div>

          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Potassium</h3>
            <p class="text-3xl font-bold text-orange-400">{{ avg.potassium }} {{ NPK_UNIT }}</p>
            <span class="mt-2 inline-block px-2 py-0.5 text-xs font-medium rounded"
                  :class="statusClass(npkStatus('potassium', avg.potassium))">
              {{ npkStatus('potassium', avg.potassium) }}
            </span>
          </div>
        </div>
      </section>

      <!-- 🔸 Soil Temperature -->
      <section
        v-if="soilRaw && soilRaw.length"
        class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6 h-full"
      >
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Soil Temperature</h2>

        <div class="flex gap-4 mb-4">
          <Button @click="downloadSoilChart('Soil Temp (°C)')" variant="secondary">
            Download Soil Temp CSV
          </Button>

          <Button @click="downloadChartImage('soilTempChart')" variant="default">
            Download Soil Temp Chart as Image
          </Button>
        </div>

        <!-- Make sure this container stretches -->
        <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex-1">
          <LineChart
            :chart-data="soilChartDataSingle('Soil Temp (°C)')"
            :chart-options="soilOptions"
            ref="soilTempChart"
            class="w-full h-full"
          />
        </div>
      </section>

      <!-- 🔸 CO₂ Forecast -->
      <section
        v-if="co2ForecastData"
        class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6"
      >
        <h2 class="text-xl font-semibold mb-4 text-orange-400">CO₂ Forecast</h2>

        <Button @click="downloadCO2Chart" variant="secondary" class="mb-4">
          Download CO₂ CSV
        </Button>
        
        <Button @click="downloadChartImage('co2Chart')" variant="default">
          Download CO₂ Chart as Image
        </Button>

        <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
          <LineChart :chart-data="co2ForecastData" :chart-options="co2Options" ref="co2Chart"/>
        </div>
      </section>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '../components/Sidebar/index.vue'
import LineChart from '../components/LineChart.vue'
import {
  Combobox,
  ComboboxButton,
  ComboboxOptions,
  ComboboxOption,
} from '@headlessui/vue'
import { ref, computed } from 'vue'
import type { ChartData, ChartOptions } from 'chart.js'
import 'chartjs-adapter-date-fns'
import { Button } from '@/components/ui/button'

/* ── Types ───────────────────────── */
interface NPKReading { timestamp: string; nitrogen: number | null; phosphorus: number | null; potassium: number | null }
interface SoilReading { timestamp: string; soil_temp: number | null; device: string }
interface CO2Reading   { timestamp: string; co2: number | null; device: string }

/* ── State ───────────────────────── */
const selected = ref<string[]>([])

/* ── NPK helpers ─────────────────── */
const NPK_UNIT = 'ppm'
type NPKKey = 'nitrogen' | 'phosphorus' | 'potassium'
const NPK_THRESHOLDS: Record<NPKKey, { low: number; high: number }> = {
  nitrogen:   { low: 100, high: 400 },
  phosphorus: { low: 50,  high: 200 },
  potassium:  { low: 100, high: 300 }
}
function npkStatus(key: NPKKey, valStr: string) {
  const v = Number(valStr)
  if (isNaN(v)) return '—'
  const { low, high } = NPK_THRESHOLDS[key]
  return v < low ? 'Low' : v > high ? 'High' : 'Optimal'
}
function statusClass(status: string) {
  switch (status) {
    case 'Low': return 'bg-yellow-100 text-yellow-800'
    case 'High': return 'bg-red-100 text-red-800'
    case 'Optimal': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-600'
  }
}

/* ── NPK fetch/avg ───────────────── */
const npkData = await $fetch<NPKReading[]>('http://localhost:3001/compost-npk')
const avg = computed(() => {
  if (!npkData.length) return { nitrogen: '-', phosphorus: '-', potassium: '-' }
  const avgField = (f: keyof NPKReading) => (
    npkData.reduce((sum, d) => sum + (Number(d[f]) || 0), 0) / npkData.length
  ).toFixed(1)
  return { nitrogen: avgField('nitrogen'), phosphorus: avgField('phosphorus'), potassium: avgField('potassium') }
})

/* ── Soil helpers ─────────────────── */
const TEMP_RANGE  = { low: 25, high: 32 }

/* ── Soil charts ─────────────────── */
const soilRaw = await $fetch<SoilReading[]>('http://localhost:3001/soil-temp-co2')

function movingAvg(values: (number | null)[], window = 5): (number | null)[] {
  const out: (number | null)[] = []
  for (let i = 0; i < values.length; i++) {
    const slice = values.slice(Math.max(0, i - window + 1), i + 1).filter(v => v != null) as number[]
    out.push(slice.length ? slice.reduce((a, b) => a + b, 0) / slice.length : null)
  }
  return out
}

function cleanZeros(arr: number[], minValid = 1): (number | null)[] {
  return arr.map(v => (v <= minValid ? null : v))
}

function soilChartDataSingle(label: string): ChartData<'line'> {
  const src = [...soilRaw].sort((a,b) => +new Date(a.timestamp) - +new Date(b.timestamp))

  const labels = src.map(r => new Date(r.timestamp))
  const temps  = src.map(d => d.soil_temp ?? 0)

  const isTemp = label === 'Soil Temp (°C)'

  const cleaned  = cleanZeros(temps)
  const smoothed = movingAvg(cleaned, 5)
  const valid    = cleaned.filter(v => v != null) as number[]
  const avgVal   = valid.length ? Math.round(valid.reduce((a,b) => a + b, 0) / valid.length) : 0

  return {
    labels,
    datasets: [
      { label, data: cleaned, borderColor: 'rgb(255,165,0)', pointRadius: 2, spanGaps: true, fill: false },
      { label: `Smoothed ${label}`, data: smoothed, borderColor: 'rgb(0,181,255)', borderDash: [6,6], pointRadius: 0, spanGaps: true, fill: false },
      { label: `Avg ${label}`, data: Array(labels.length).fill(avgVal), borderColor: 'rgb(0,153,255)', borderDash: [4,4], pointRadius: 0, fill: false }
    ]
  }
}

const soilOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'time',
      time: { unit: 'hour', displayFormats: { hour: 'h:mm aa' } },
      ticks: {
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 12,
        callback(value) {
          const date = new Date(value as number)
          return date.getMinutes() === 0
            ? date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
            : ''
        }
      }
    }
  },
  plugins: {
    decimation: { enabled: true, algorithm: 'lttb', samples: 60 },
    tooltip: {
      callbacks: {
        afterBody(items) {
          const item = items?.[0]; if (!item) return ''
          const lbl = String(item.dataset?.label ?? '')
          const v   = item.parsed?.y; if (v == null) return ''
          const isTemp = lbl.includes('Temp')
          const range = TEMP_RANGE;
          if (v < range.low)  return isTemp ? 'Below ideal range' : 'Too dry'
          if (v > range.high) return isTemp ? 'Above ideal range' : 'Too wet'
          return isTemp ? 'Within ideal range' : 'Healthy moisture'
        }
      }
    }
  }
}

/* ── CO₂ Forecast ─────────────────── */
const CO2_UNIT = 'ppm'
const FORECAST_RATIO = 0.25
const co2Raw = await $fetch<CO2Reading[]>('http://localhost:3001/soil-temp-co2')

const co2ForecastData = computed<ChartData<'line'>>(() => {
  const src = [...co2Raw].sort((a, b) => +new Date(a.timestamp) - +new Date(b.timestamp))
  const pastVals   = src.map(d => d.co2 ?? 0)
  const pastLabels = src.map(d => new Date(d.timestamp)) // Use Date objects

  const n = pastVals.length
  if (!n) return { labels: [], datasets: [] }

  // Linear regression on index
  const x     = [...Array(n).keys()]
  const sumX  = x.reduce((a, b) => a + b, 0)
  const sumY  = pastVals.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((s, xi, i) => s + xi * pastVals[i], 0)
  const sumX2 = x.reduce((s, xi) => s + xi * xi, 0)

  const m = (n * sumXY - sumX * sumY) / ((n * sumX2 - sumX ** 2) || 1)
  const b = (sumY - m * sumX) / (n || 1)

  // Use actual time delta for forecast
  const fCount = Math.max(3, Math.round(n * FORECAST_RATIO))
  const lastDate = pastLabels[n - 1]
  const prevDate = n > 1 ? pastLabels[n - 2] : new Date(lastDate.getTime() - 60_000)
  const deltaMs = Math.max(1, lastDate.getTime() - prevDate.getTime())

  const forecastVals   = Array.from({ length: fCount }, (_, i) => Math.round(m * (n + i) + b))
  const forecastLabels = Array.from({ length: fCount }, (_, i) =>
    new Date(lastDate.getTime() + deltaMs * (i + 1))
  )

  const labels = [...pastLabels, ...forecastLabels]
  const avgVal = Math.round(sumY / n)

  return {
    labels,
    datasets: [
      { label: `CO₂ (Actual) (${CO2_UNIT})`,   data: pastVals, borderColor: 'rgb(255,165,0)', pointRadius: 2, fill: false },
      { label: `CO₂ (Forecast) (${CO2_UNIT})`, data: [...Array(n).fill(null), ...forecastVals], borderColor: 'rgb(54,162,235)', borderDash: [6, 6], pointRadius: 2, fill: false },
      { label: `Avg (${avgVal} ${CO2_UNIT})`,  data: Array(labels.length).fill(avgVal), borderColor: 'rgb(0,153,255)', borderDash: [4, 4], pointRadius: 0, fill: false }
    ]
  }
}
)

const co2Options: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { ticks: { autoSkip: true, maxTicksLimit: 8, maxRotation: 0 } },
    y: { title: { display: true, text: `CO₂ (${CO2_UNIT})` } }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label(ctx) { return `${ctx.dataset.label}: ${ctx.parsed.y} ${CO2_UNIT}` }
      }
    }
  }
}

/* ── CSV / Excel helpers ─────────────────── */
function toCSV(rows: Record<string, any>[], headers: string[]) {
  const escape = (val: any) => {
    if (val == null) return ''
    const s = String(val)
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
  }
  return [headers.join(','), ...rows.map(r => headers.map(h => escape(r[h])).join(','))].join('\n')
}

function downloadBlob(name: string, content: string | ArrayBuffer, type = 'text/csv') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}

/* specific rows builders */
function buildSoilRows(label: 'Soil Temp (°C)') {
  const chart = soilChartDataSingle(label)
  const labels  = (chart.labels ?? []) as (string | Date)[]
  const dataArr = (chart.datasets?.[0]?.data ?? []) as (number | null | undefined)[]
  return labels.map((d, i) => ({
    timestamp: d instanceof Date ? d.toISOString() : String(d),
    value: dataArr[i] ?? ''
  }))
}

function buildCO2Rows() {
  const chart   = co2ForecastData.value
  const labels  = chart.labels ?? []
  const actual  = chart.datasets?.[0]?.data ?? []
  const forecast= chart.datasets?.[1]?.data ?? []
  const avgLine = chart.datasets?.[2]?.data ?? []
  return labels.map((t: any, i: number) => ({
    timestamp: t,
    actual: (actual[i] as number | null) ?? '',
    forecast: (forecast[i] as number | null) ?? '',
    avg: (avgLine[i] as number | null) ?? ''
  }))
}
function buildNPKRows() {
  return npkData.map(r => ({
    timestamp: r.timestamp,
    nitrogen: r.nitrogen ?? '',
    phosphorus: r.phosphorus ?? '',
    potassium: r.potassium ?? ''
  }))
}

/* old CSV buttons */
function downloadSoilChart(label: 'Soil Temp (°C)') {
  const rows = buildSoilRows(label)
  downloadBlob(`${label.replace(/\W+/g,'_')}.csv`, toCSV(rows, ['timestamp', label === 'Soil Temp (°C)' ? 'value' : 'value']))
}
function downloadCO2Chart() {
  const rows = buildCO2Rows()
  downloadBlob('co2.csv', toCSV(rows, ['timestamp','actual','forecast','avg']))
}

/* new export panel */
type ExportFmt = 'csv' | 'xlsx'

async function exportSelected(fmt: ExportFmt) {
  const soilTempRows = buildSoilRows('Soil Temp (°C)')
  const co2Rows      = buildCO2Rows()

  if (fmt === 'csv') {
    downloadBlob('soil_temp.csv', toCSV(soilTempRows, ['timestamp','value']))
    downloadBlob('co2.csv',       toCSV(co2Rows,      ['timestamp','actual','forecast','avg']))
    return
  }

  const XLSX = await import(/* @vite-ignore */ 'xlsx')
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(soilTempRows), 'Soil Temp')
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(co2Rows),      'CO2')

  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  downloadBlob('selected_data.xlsx', wbout, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
}

async function downloadFullReport() {
  const XLSX = await import(/* @vite-ignore */ 'xlsx')
  const wb = XLSX.utils.book_new()

  // Add NPK card data
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(buildNPKRows()), 'NPK')

  // Add Soil Temp chart data
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(buildSoilRows('Soil Temp (°C)')), 'Soil Temp')

  // Add CO₂ chart data
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(buildCO2Rows()), 'CO2')

  // Add device slicer selection
  XLSX.utils.book_append_sheet(
    wb,
    XLSX.utils.aoa_to_sheet([
      ['Selected Devices'],
      ...selected.value.map(dev => [dev])
    ]),
    'Device Slicer'
  )

  // Add summary sheet
  const summary = [
    ['Dashboard Export Summary'],
    ['Generated', new Date().toLocaleString()],
    ['Devices Selected', selected.value.join(', ') || 'None'],
    [],
    ['Averages'],
    ['Nitrogen',   avg.value.nitrogen],
    ['Phosphorus', avg.value.phosphorus],
    ['Potassium',  avg.value.potassium]
  ]
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(summary), 'Summary')

  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  downloadBlob('full_report.xlsx', wbout, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
}

/* ── Chart Download Function ─────────────────── */
function downloadChartImage(chartRef: string) {
  let chartInstance = null
  if (chartRef === 'soilTempChart') {
    chartInstance = soilTempChart.value?.chartInstance
  } else if (chartRef === 'co2Chart') {
    chartInstance = co2Chart.value?.chartInstance
  }

  if (chartInstance) {
    const imageUrl = chartInstance.toBase64Image()
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = `${chartRef}.jpg`
    link.click()
  }
}

/* ── Refs for Chart Instances ─────────────────── */
import type { ComponentPublicInstance } from 'vue'

type ChartComponentRef = ComponentPublicInstance<{ chartInstance?: any }>

const soilTempChart = ref<ChartComponentRef | null>(null)
const co2Chart = ref<ChartComponentRef | null>(null)


/* ── Device slicer ─────────────────── */
const allDeviceNamesRaw = await $fetch<string[]>('http://localhost:3001/device-names')
const allDeviceNames = allDeviceNamesRaw.filter(name => name.startsWith('NP'))

const options = computed(() => allDeviceNames.filter(d => !selected.value.includes(d)))
const allSelected = computed(() =>
  allDeviceNames.length > 0 && selected.value.length === allDeviceNames.length
)

function toggleAll() { selected.value = allSelected.value ? [] : [...allDeviceNames] }
function remove(dev: string) { selected.value = selected.value.filter(d => d !== dev) }
function clearAll() { selected.value = [] }
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
</style>
