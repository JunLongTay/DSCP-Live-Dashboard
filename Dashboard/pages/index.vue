<template>
  <div class="relative min-h-screen w-full">
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
    <div class="ml-64 min-h-screen relative z-20 flex flex-col gap-10 px-6 md:px-12 py-8">

      <!-- 🔹 Device Slicer -->
      <section class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-4">
        <h2 class="text-xl font-semibold text-orange-400">Soil Moisture Forecast</h2>

        <div class="w-full max-w-xl">
          <!-- Label + count -->
          <div class="flex items-center justify-between mb-2">
            <label class="font-medium">Filter by Device(s)</label>
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
              class="ml-auto text-sm text-red-500 hover:underline"
            >
              Clear All
            </button>
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
                  <!-- Select / Deselect all -->
                  <ComboboxOption
                    :value="'__ALL__'"
                    class="px-3 py-2 font-medium bg-gray-50 dark:bg-zinc-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-600"
                    @click.prevent="toggleAll"
                  >
                    {{ allSelected ? 'Deselect All' : 'Select All' }}
                  </ComboboxOption>

                  <!-- Individual devices (not already selected) -->
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
          <!-- Nitrogen -->
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Nitrogen</h3>
            <p class="text-3xl font-bold text-orange-400">
              {{ avg.nitrogen }} {{ NPK_UNIT }}
            </p>
            <span
              class="mt-2 inline-block px-2 py-0.5 text-xs font-medium rounded"
              :class="statusClass(npkStatus('nitrogen', avg.nitrogen))"
            >
              {{ npkStatus('nitrogen', avg.nitrogen) }}
            </span>
          </div>

          <!-- Phosphorus -->
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Phosphorus</h3>
            <p class="text-3xl font-bold text-orange-400">
              {{ avg.phosphorus }} {{ NPK_UNIT }}
            </p>
            <span
              class="mt-2 inline-block px-2 py-0.5 text-xs font-medium rounded"
              :class="statusClass(npkStatus('phosphorus', avg.phosphorus))"
            >
              {{ npkStatus('phosphorus', avg.phosphorus) }}
            </span>
          </div>

          <!-- Potassium -->
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500 flex flex-col items-center">
            <h3 class="font-semibold text-base text-orange-300 mb-1">Potassium</h3>
            <p class="text-3xl font-bold text-orange-400">
              {{ avg.potassium }} {{ NPK_UNIT }}
            </p>
            <span
              class="mt-2 inline-block px-2 py-0.5 text-xs font-medium rounded"
              :class="statusClass(npkStatus('potassium', avg.potassium))"
            >
              {{ npkStatus('potassium', avg.potassium) }}
            </span>
          </div>
        </div>
      </section>

      <!-- 🔸 Soil Temp & Moisture -->
      <section
        v-if="soilRaw && soilRaw.length"
        class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6"
      >
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Soil Temperature & Moisture</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
            <LineChart :chart-data="soilChartDataSingle('Soil Temp (°C)')" :chart-options="soilOptions" />
          </div>
          <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
            <LineChart :chart-data="soilChartDataSingle('Moisture (%)')" :chart-options="soilOptions" />
          </div>
        </div>
      </section>

      <!-- 🔸 CO₂ Forecast -->
      <section
        v-if="co2ForecastData"
        class="bg-zinc-900 border border-orange-500 rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6"
      >
        <h2 class="text-xl font-semibold mb-4 text-orange-400">CO₂ Forecast</h2>
        <div class="bg-zinc-900 rounded shadow p-4 border border-orange-500">
          <LineChart :chart-data="co2ForecastData" :chart-options="co2Options" />
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
import { ref, computed, onMounted } from 'vue'
import type { ChartData, ChartOptions } from 'chart.js'

/* ── Types ───────────────────────── */
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
interface MoistureReading {
  timestamp: string
  device: string
  moisture: number | null
}

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
    case 'Low':     return 'bg-yellow-100 text-yellow-800'
    case 'High':    return 'bg-red-100 text-red-800'
    case 'Optimal': return 'bg-green-100 text-green-800'
    default:        return 'bg-gray-100 text-gray-600'
  }
}

/* ── NPK fetch/avg ───────────────── */
const npkData = await $fetch<NPKReading[]>('http://localhost:3001/compost-npk')
const avg = computed(() => {
  if (!npkData.length) return { nitrogen: '-', phosphorus: '-', potassium: '-' }
  const avgField = (f: keyof NPKReading) =>
    (npkData.reduce((sum, d) => sum + (Number(d[f]) || 0), 0) / npkData.length).toFixed(1)
  return {
    nitrogen: avgField('nitrogen'),
    phosphorus: avgField('phosphorus'),
    potassium: avgField('potassium')
  }
})

/* ── Soil helpers ─────────────────── */
const TEMP_RANGE  = { low: 25, high: 32 } // tweak
const MOIST_RANGE = { low: 50, high: 65 } // tweak

function cleanZeros(arr: number[], minValid = 1) {
  return arr.map(v => (v <= minValid ? null : v))
}
function movingAvg(values: (number | null)[], window = 5) {
  const out: (number | null)[] = []
  for (let i = 0; i < values.length; i++) {
    const slice = values.slice(Math.max(0, i - window + 1), i + 1).filter(v => v != null) as number[]
    out.push(slice.length ? slice.reduce((a, b) => a + b, 0) / slice.length : null)
  }
  return out
}

/* ── Soil charts ─────────────────── */
const soilRaw = await $fetch<SoilReading[]>('http://localhost:3001/soil-temp-co2')
function soilChartDataSingle(label: string): ChartData<'line'> {
  const labels    = soilRaw.map(d => new Date(d.timestamp).toLocaleTimeString())
  const temps     = soilRaw.map(d => d.soil_temp ?? 0)
  const moistMock = temps.map(() => Math.floor(Math.random() * 30) + 40) // mock moisture

  const isTemp = label === 'Soil Temp (°C)'
  const raw    = isTemp ? temps : moistMock

  const cleaned  = cleanZeros(raw)
  const smoothed = movingAvg(cleaned, 5)

  const valid = cleaned.filter(v => v != null) as number[]
  const avgVal = valid.length ? Math.round(valid.reduce((a, b) => a + b, 0) / valid.length) : 0

  const datasets: any[] = [
    {
      label,
      data: cleaned,
      borderColor: 'rgb(255,165,0)',
      pointRadius: 2,
      spanGaps: true,
      fill: false
    },
    {
      label: `Smoothed ${label}`,
      data: smoothed,
      borderColor: 'rgb(0,181,255)',
      borderDash: [6, 6],
      pointRadius: 0,
      spanGaps: true,
      fill: false
    },
    {
      label: `Avg ${label}`,
      data: Array(labels.length).fill(avgVal),
      borderColor: 'rgb(0,153,255)',
      borderDash: [4, 4],
      pointRadius: 0,
      fill: false
    }
  ]

  return { labels, datasets }
}

const soilOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { ticks: { autoSkip: true, maxTicksLimit: 8, maxRotation: 0 } }
  },
  plugins: {
    decimation: { enabled: true, algorithm: 'lttb', samples: 60 },
    tooltip: {
      callbacks: {
        afterBody(items) {
        const item = items?.[0];
        if (!item) return '';

        const lbl = String(item.dataset?.label ?? '');
        const v   = item.parsed?.y;
        if (v == null) return '';

        const isTemp = lbl.includes('Temp');
        const range  = isTemp ? TEMP_RANGE : MOIST_RANGE;

        if (v < range.low)  return isTemp ? 'Below ideal range' : 'Too dry';
        if (v > range.high) return isTemp ? 'Above ideal range' : 'Too wet';
        return isTemp ? 'Within ideal range' : 'Healthy moisture';
        }
      }
    }
  }
}

/* ── CO₂ Forecast ─────────────────── */
const CO2_UNIT = 'ppm'

const co2Raw = await $fetch<CO2Reading[]>('http://localhost:3001/soil-temp-co2')
const co2ForecastData = computed<ChartData<'line'>>(() => {
  const co2    = co2Raw.map(d => d.co2 ?? 0)
  const labels = co2Raw.map(d => new Date(d.timestamp).toLocaleTimeString())

  const n     = co2.length
  const x     = [...Array(n).keys()]
  const sumX  = x.reduce((a, b) => a + b, 0)
  const sumY  = co2.reduce((a, b) => a + b, 0)
  const sumXY = x.reduce((sum, xi, i) => sum + xi * co2[i], 0)
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0)

  const m = (n * sumXY - sumX * sumY) / ((n * sumX2 - sumX ** 2) || 1)
  const b = (sumY - m * sumX) / (n || 1)

  const forecast       = [...Array(5)].map((_, i) => Math.round(m * (n + i) + b))
  const forecastLabels = [...Array(5)].map((_, i) => `T+${i + 1}`)
  const allLabels      = [...labels, ...forecastLabels]
  const totalPoints    = allLabels.length

  return {
    labels: allLabels,
    datasets: [
      {
        label: `CO₂ (Actual) (${CO2_UNIT})`,
        data: co2,
        borderColor: 'rgb(255,99,132)',
        fill: false
      },
      {
        label: `CO₂ (Forecast) (${CO2_UNIT})`,
        data: [...Array(n).fill(null), ...forecast],
        borderColor: 'rgb(54,162,235)',
        borderDash: [6, 6],
        fill: false
      }
    ]
  }
})

const co2Options: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: { ticks: { autoSkip: true, maxTicksLimit: 8 } },
    y: { title: { display: true, text: `CO₂ (${CO2_UNIT})` } }
  },
  plugins: {
    tooltip: {
      callbacks: {
        label(ctx) {
          return `${ctx.dataset.label}: ${ctx.parsed.y} ${CO2_UNIT}`
        }
      }
    }
  }
}

// ── Device names for slicer (shows ALL devices) ──
const allDeviceNamesRaw = await $fetch<string[]>('http://localhost:3001/device-names')
const allDeviceNames = allDeviceNamesRaw.filter(name => name.startsWith('NP'))

// Still grab moisture data if you use it elsewhere (charts, etc.)
const moistureRaw = await $fetch<MoistureReading[]>('http://localhost:3001/moisture-all')

const deviceData = computed<Record<string, MoistureReading[]>>(() => {
  const map: Record<string, MoistureReading[]> = {}
  // ensure every device exists, even with no rows
  for (const name of allDeviceNames) map[name] = []
  for (const r of moistureRaw) (map[r.device] ||= []).push(r)
  for (const k in map) {
    map[k].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }
  return map
})

const options = computed(() => allDeviceNames.filter(d => !selected.value.includes(d)))
const allSelected = computed(() =>
  allDeviceNames.length > 0 && selected.value.length === allDeviceNames.length
)

function toggleAll() {
  selected.value = allSelected.value ? [] : [...allDeviceNames]
}
function remove(dev: string) {
  selected.value = selected.value.filter(d => d !== dev)
}
function clearAll() {
  selected.value = []
}

onMounted(() => {
  if (!selected.value.length && allDeviceNames.length) {
    selected.value = [...allDeviceNames]
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
