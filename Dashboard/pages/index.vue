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
    <div class="min-h-screen relative z-20 flex flex-col px-6 md:px-12 py-8">

      <!-- 🔹 Device Slicer -->
      <!-- Dashboard Overview (no container) -->
      <div class="flex flex-col gap-4">
        <!-- Title + Last refreshed + Export row -->
        <div class="flex items-baseline gap-6 mb-2">
          <h1 class="text-3xl font-bold text-orange-400 font-roboto-slab">Composting Dashboard Overview</h1>
          <p class="text-sm text-orange-300">
            Last refreshed: {{ lastRefresh }}
          </p>
          <!-- Export Data Dropdown aligned right -->
          <div class="ml-auto">
            <Menu as="div" class="relative inline-block text-left">
              <div>
                <MenuButton>
                  <Button variant="default" class="export-data-btn">
                    Export Data ▼
                  </Button>
                </MenuButton>
              </div>
              <Transition
                enter="transition ease-out duration-100"
                enter-from="opacity-0 scale-95"
                enter-to="opacity-100 scale-100"
                leave="transition ease-in duration-75"
                leave-from="opacity-100 scale-100"
                leave-to="opacity-0 scale-95"
              >
                <MenuItems class="origin-top-right absolute right-0 mt-2 w-64 rounded-md shadow-lg
                                  bg-zinc-900 ring-1 ring-orange-700 ring-opacity-70 focus:outline-none z-50">
                  <div class="py-1">
                    <MenuItem>
                      <div class="px-4 py-2 text-sm text-orange-200 font-semibold">Full Report</div>
                    </MenuItem>
                    <MenuItem as="button"
                      @click="downloadFullReport"
                      class="w-full px-4 py-2 text-sm text-orange-100 hover:bg-orange-800 export-summary-btn"
                    >
                      Download All Charts + Summary
                    </MenuItem>
                  </div>
                </MenuItems>
              </Transition>
            </Menu>
          </div>
        </div>
        <!-- Divider line below header -->
        <hr class="border-t border-orange-700 mb-4" />

      <div class="w-full mb-8">
        <div class="flex items-center justify-between mb-2">
          <label class="font-medium text-orange-300">Filter by Device(s)</label>
          <span class="text-sm text-orange-200">{{ selected.length }} selected</span>
        </div>

        <!-- Selected Devices Chips & Clear All -->
        <div v-if="selected.length" class="flex items-center flex-wrap gap-2 mb-2">
          <span
            v-for="dev in selected"
            :key="dev"
            class="inline-flex items-center px-4 py-1 rounded-full bg-orange-800 text-orange-100 font-medium text-sm mr-2 animate-fade-in"
          >
            {{ dev }}
            <button
              @click.stop="remove(dev)"
              class="ml-2 text-orange-300 hover:text-orange-400 focus:outline-none pill-remove-btn"
              aria-label="Remove device"
            >
              ×
            </button>
          </span>
          <button
            @click="clearAll"
            class="ml-2 text-orange-400 text-sm font-semibold hover:underline clear-all-btn"
            style="margin-left:auto"
          >
            Clear All
          </button>
        </div>

        <!-- Modal Filter Trigger -->
        <button
          @click="showDeviceModal = true"
          class="w-full border border-orange-500 rounded p-2 bg-zinc-900 text-orange-100 text-left focus:outline-none focus:ring-2 focus:ring-orange-400 mt-3"
        >
          Select Devices
        </button>

        <!-- Device Filter Modal -->
        <div v-if="showDeviceModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div class="bg-zinc-900 border border-orange-500 rounded-lg shadow-lg p-6 w-full max-w-md relative animate-fade-in">
            <button @click="showDeviceModal = false" class="absolute top-3 right-3 text-orange-400 text-xl font-bold">×</button>
            <h3 class="text-lg font-bold text-orange-300 mb-3">Select Devices</h3>
            <input v-model="deviceSearch" type="text" placeholder="Search devices..." class="w-full mb-3 p-2 border border-orange-500 rounded bg-zinc-800 text-orange-100 placeholder-orange-400" />
            <div class="flex justify-between mb-2 text-orange-400 text-sm">
              <button @click="selectAllDevices" class="hover:underline">Select All</button>
              <button @click="clearAllDevices" class="hover:underline">Clear All</button>
            </div>
            <div class="max-h-60 overflow-y-auto mb-4">
              <div v-for="d in filteredDeviceOptions" :key="d" class="flex items-center gap-2 py-1">
                <input type="checkbox" :id="'dev-' + d" :value="d" v-model="modalSelected" class="accent-orange-500" />
                <label :for="'dev-' + d" class="text-orange-100">{{ d }}</label>
              </div>
            </div>
            <div class="flex justify-end gap-2 mt-2">
              <button @click="showDeviceModal = false" class="px-4 py-2 rounded bg-zinc-700 text-orange-200 font-semibold">Cancel</button>
              <button @click="confirmDeviceSelection" class="px-4 py-2 rounded bg-orange-500 text-white font-bold">Confirm</button>
            </div>
          </div>
        </div>
      </div>
    </div>

      <!-- 🔹 Average NPK Levels -->
      <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Average NPK Levels</h2>
      <div v-if="selected.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <!-- NPK Cards -->
        <div
          v-for="card in avgPerDevice"
          :key="card.devicename"
          class="bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6
                 transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl flex flex-col orange-glow"
          style="will-change: transform;"
        >
          <!-- Header -->
          <h3 class="text-xl font-semibold text-orange-300 mb-4 text-center">
            {{ card.devicename }}
          </h3>
          <!-- Nutrient rows -->
          <div v-for="nutrient in ['nitrogen','phosphorus','potassium']" :key="nutrient" class="mb-6 flex items-center gap-4">
            <!-- Status bar/glyph -->
            <div class="flex flex-col items-center w-16 flex-shrink-0">
              <div
                class="w-2 h-10 rounded-full"
                :class="{
                  'bg-green-500': npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card])==='Optimal',
                  'bg-yellow-500': npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card])==='Low',
                  'bg-red-500': npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card])==='High'
                }"
                :style="{
                  height: '40px',
                  transition: 'height 0.8s cubic-bezier(0.4,0,0.2,1)',
                  boxShadow:
                    npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card])==='Optimal'
                      ? '0 0 8px 2px #22c55e'
                      : npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card])==='Low'
                        ? '0 0 8px 2px #facc15'
                        : npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card])==='High'
                          ? '0 0 8px 2px #f87171'
                          : ''
                }"
              ></div>
              <span class="mt-1 text-xs text-zinc-400 font-semibold">
                {{ npkStatus(nutrient as NPKKey, card[nutrient as keyof typeof card]) }}
              </span>
            </div>
            <!-- Value & label -->
            <div class="flex-1 flex flex-col min-w-0">
              <span class="text-sm font-medium text-orange-300 capitalize mb-1" style="opacity:0.8;">
                {{ nutrient }}
              </span>
              <span class="text-3xl font-bold text-orange-400 leading-tight">
                {{ card[nutrient as keyof typeof card] }} {{ NPK_UNIT }}
              </span>
            </div>
          </div>
          <!-- Recommendations accordion -->
          <details class="mt-auto bg-zinc-900 border border-orange-700 rounded-lg">
            <summary
              class="cursor-pointer py-2 px-4 text-sm font-medium text-orange-300
                     transition-colors duration-150 flex items-center gap-2"
            >
              <!-- Icon: Lightbulb -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 3a7 7 0 00-7 7c0 3.07 1.64 5.64 4 6.32V18a1 1 0 001 1h4a1 1 0 001-1v-1.68c2.36-.68 4-3.25 4-6.32a7 7 0 00-7-7zm0 16v2m-4-2h8" />
              </svg>
              Recommendations
            </summary>
            <ul class="p-4 list-none text-sm text-orange-200 space-y-2">
              <li v-for="note in npkRecommendations[card.devicename].split('. ')" :key="note" class="flex items-start gap-2">
                <span class="text-lg">•</span>
                <span>{{ note }}</span>
              </li>
            </ul>
          </details>
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-32 text-orange-300 text-lg font-bold mb-8">
        Please select a device to get started.
      </div>


      <!-- 🔸 Soil Temperature -->
      <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Soil Temperature</h2>
      <div v-if="selected.length" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <div
          v-for="(device, idx) in selected"
          :key="device"
          class="bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6
           transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl flex flex-col orange-glow"
          style="will-change: transform;"
        >
          <!-- Chart Header with pill toggles -->
          <div class="flex items-center justify-between mb-2">
            <div class="flex gap-2">
              <button
                class="pill flex items-center gap-1 px-3 py-1 rounded-full bg-orange-900 text-orange-100 font-semibold text-xs border border-orange-500"
                :class="{ 'opacity-100': soilSeriesVisible[device][0], 'opacity-50': !soilSeriesVisible[device][0] }"
                @click="toggleSeries(device, 0)"
              >
                <span class="swatch w-3 h-3 rounded-full bg-orange-400 inline-block"></span>
                Raw
              </button>
              <button
                class="pill flex items-center gap-1 px-3 py-1 rounded-full bg-blue-900 text-blue-100 font-semibold text-xs border border-blue-500"
                :class="{ 'opacity-100': soilSeriesVisible[device][1], 'opacity-50': !soilSeriesVisible[device][1] }"
                @click="toggleSeries(device, 1)"
              >
                <span class="swatch w-3 h-3 rounded-full bg-blue-400 inline-block border-dashed border-2 border-blue-400"></span>
                Smthd.
              </button>
              <button
                class="pill flex items-center gap-1 px-3 py-1 rounded-full bg-yellow-900 text-yellow-100 font-semibold text-xs border border-yellow-500"
                :class="{ 'opacity-100': soilSeriesVisible[device][2], 'opacity-50': !soilSeriesVisible[device][2] }"
                @click="toggleSeries(device, 2)"
              >
                <span class="swatch w-3 h-3 rounded-full bg-yellow-400 inline-block border-dotted border-2 border-yellow-400"></span>
                Avg
              </button>
            </div>
            <button
              @click="downloadSingleSoilChart(idx, device)"
              class="download-btn flex items-center gap-2 px-2 py-1 rounded bg-transparent border border-orange-500 text-orange-500 font-semibold hover:bg-orange-700 hover:text-white transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 download-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" />
              </svg>
              Download
            </button>
          </div>
          <LineChart
            :chart-data="soilChartDataSingleDeviceWithToggle(device, 'Soil Temp (°C)')"
            :chart-options="soilOptions"
            class="h-60"
            :ref="el => setSoilTempChartRef(el, idx)"
            :id="`soil-temp-chart-${idx}`"
          />
          <div class="mt-2 flex items-center justify-between w-full">
            <div class="text-center text-orange-400 font-semibold text-base">Chart: Soil Temp - {{ device }}</div>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-32 text-orange-300 text-lg font-bold">
        Please select a device to get started.
      </div>

      <!-- 🔸 CO₂ Chart (Actual Only) -->
      <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">CO₂ Levels</h2>
      <div v-if="selected.length"
        class="bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6 mb-12 transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl flex flex-col orange-glow"
        style="will-change: transform;">
        <!-- Pills and Download button aligned in one row -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex flex-wrap gap-2">
            <span
              v-for="(device, idx) in co2ChartDevices"
              :key="device"
              class="co2-pill font-semibold text-xs rounded-full px-4 py-1 flex items-center border"
              :style="{
                background: co2DeviceColorMap[device],
                color: '#fff',
                borderColor: co2DeviceColorMap[device],
                opacity: co2ChartDevices.includes(device) ? 1 : 0.5
              }"
              @click="toggleCo2Device(device)"
            >
              {{ device }}
            </span>
          </div>
          <button
            @click="downloadChartImage('co2Chart')"
            class="download-btn flex items-center gap-2 px-2 py-1 rounded bg-transparent border border-orange-500 text-orange-500 font-semibold hover:bg-orange-700 hover:text-white transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 download-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" />
            </svg>
            Download
          </button>
        </div>
        <LineChart
          :chart-data="co2Data"
          :chart-options="co2Options"
          ref="co2Chart"
          id="co2-chart"
          class="h-60"
        />
      </div>
      <div v-else class="flex items-center justify-center h-32 text-orange-300 text-lg font-bold">
        Please select a device to get started.
      </div>
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
  Menu, 
  MenuButton, 
  MenuItem, 
  MenuItems, 
} from '@headlessui/vue'
import { ref, computed, watchEffect, onMounted, nextTick, reactive } from 'vue'
import type { ChartData, ChartOptions } from 'chart.js'
import 'chartjs-adapter-date-fns'
import { Transition } from 'vue'
import { Button } from '@/components/ui/button'

// On mount, record the page load time in “HH:mm DD/MM/YYYY” format
const lastRefresh = ref('')

onMounted(() => {
  // Format as “HH:mm DD/MM/YYYY”
  const now = new Date()
  const hours   = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const day     = String(now.getDate()).padStart(2, '0')
  const month   = String(now.getMonth() + 1).padStart(2, '0')
  const year    = now.getFullYear()
  lastRefresh.value = `${hours}:${minutes} ${day}/${month}/${year}`
})

/* ── Types ───────────────────────── */
interface NPKReading { timestamp: string; nitrogen: number | null; phosphorus: number | null; potassium: number | null; devicename: string }
interface SoilReading { timestamp: string; soil_temp: number | null; devicename: string }
interface CO2Reading   { timestamp: string; co2: number | null; devicename: string;  }

/* ── State ───────────────────────── */
const SELECTED_DEVICES_KEY = 'dashboard_selected_devices'
const selected = ref<string[]>([])

// Make device names reactive
const allDeviceNamesRaw = ref<string[]>([])

onMounted(async () => {
  try {
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices')
  } catch {
    allDeviceNamesRaw.value = []
  }
})

/* ── NPK helpers ─────────────────── */
// 1) Re‑use your existing thresholds & status function
const NPK_UNIT = 'ppm'
type NPKKey = 'nitrogen' | 'phosphorus' | 'potassium'
interface NPKThreshold { low: number; high: number }
const NPK_THRESHOLDS: Record<NPKKey, NPKThreshold> = {
  nitrogen:   { low: 200, high: 500 },
  phosphorus: { low: 330, high: 880 },
  potassium:  { low: 330, high: 880 }
}
function npkStatus(key: NPKKey, val: string) {
  const v = Number(val)
  const { low, high } = NPK_THRESHOLDS[key]
  if (isNaN(v)) return '—'
  if (v < low) return 'Low'
  if (v > high) return 'High'
  return 'Optimal'
}
function statusClass(status: string) {
  switch (status) {
    case 'Low':
      return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200'
    case 'High':
      return 'bg-red-100 text-red-800 hover:bg-red-200'
    case 'Optimal':
      return 'bg-green-100 text-green-800 hover:bg-green-200'
    default:
      return 'bg-gray-100 text-gray-600 hover:bg-gray-200'
  }
}
/* ── NPK fetch/avg ───────────────── */
const npkData = ref<NPKReading[]>([])

watchEffect(async () => {
  const bucket = 60    // minutes per bucket
  const windowMin = 1440  // minutes back (24 hrs)

  const url = `http://localhost:3001/compost-npk?bucket_min=${bucket}&window_min=${windowMin}`
  npkData.value = await $fetch<NPKReading[]>(url)
})

const filteredNpkData = computed(() => {
  if (!selected.value.length) return npkData.value
  // npkData rows have devicename
  return npkData.value.filter(row => selected.value.includes((row as any).devicename))
})

// Compute average NPK per device
const avgPerDevice = computed(() => {
  if (!selected.value.length) {
    // Show overall average if no device selected
    const data = npkData.value
    if (!data.length) return []
    const avgField = (f: keyof NPKReading) => (
      data.reduce((sum, d) => sum + (Number(d[f]) || 0), 0) / data.length
    ).toFixed(1)
    return [{
      devicename: 'All Devices',
      nitrogen: avgField('nitrogen'),
      phosphorus: avgField('phosphorus'),
      potassium: avgField('potassium')
    }]
  }
  // Per device
  return selected.value.map(device => {
    const data = npkData.value.filter(row => row.devicename === device)
    if (!data.length) return {
      devicename: device,
      nitrogen: '-', phosphorus: '-', potassium: '-'
    }
    const avgField = (f: keyof NPKReading) => (
      data.reduce((sum, d) => sum + (Number(d[f]) || 0), 0) / data.length
    ).toFixed(1)
    return {
      devicename: device,
      nitrogen: avgField('nitrogen'),
      phosphorus: avgField('phosphorus'),
      potassium: avgField('potassium')
    }
  })
})

// Computed recommendations based on NPK levels
const npkRecommendations = computed<Record<string,string>>(() => {
  const recs: Record<string,string> = {}

  avgPerDevice.value.forEach(card => {
    const notes: string[] = []
    const name = card.devicename
    const nStatus = npkStatus('nitrogen',   card.nitrogen)
    const pStatus = npkStatus('phosphorus', card.phosphorus)
    const kStatus = npkStatus('potassium',  card.potassium)

    // Nitrogen
    if (nStatus === 'Low') {
      notes.push('🟢 Low N: Add more green compost materials (vegetable scraps, coffee grounds, fresh grass clippings).')
    } else if (nStatus === 'High') {
      notes.push('🟠 High N: Mix in more brown materials (dried leaves, straw, shredded paper) to balance.')
    }

    // Phosphorus
    if (pStatus === 'Low') {
      notes.push('🟢 Low P: Toss in bone meal or crushed eggshells to boost phosphorus levels.')
    } else if (pStatus === 'High') {
      notes.push('🟠 High P: Reduce high‑P inputs (e.g. poultry manure) and add carbon‑rich browns.')
    }

    // Potassium
    if (kStatus === 'Low') {
      notes.push('🟢 Low K: Add wood ash or banana peels for a potassium boost.')
    } else if (kStatus === 'High') {
      notes.push('🟠 High K: Cut back on wood ash; mix in more greens or browns without K.')
    }

    recs[name] = notes.length
      ? notes.join(' ')
      : '✅ All nutrients are in good range for healthy composting.'
  })

  return recs
})
/* ── Soil helpers ─────────────────── */
const TEMP_RANGE  = { low: 25, high: 32 }

/* ── Soil charts ─────────────────── */
const soilRaw = ref<SoilReading[]>([])

watchEffect(async () => {
  const bucket = 60    // 1‑hour buckets
  const windowMin = 1440  // last 1440 minutes = 24 hours

  const url = `http://localhost:3001/soil-temp-co2?bucket_min=${bucket}&window_min=${windowMin}`
  soilRaw.value = await $fetch<SoilReading[]>(url)
})

const filteredSoilRaw = computed<SoilReading[]>(() => {
  if (!selected.value.length) return soilRaw.value;
  return soilRaw.value.filter(row =>
    selected.value.includes(row.devicename)
  );
});

function movingAvg(values: (number | null)[], windowMin = 5): (number | null)[] {
  const out: (number | null)[] = []
  for (let i = 0; i < values.length; i++) {
    const slice = values
      .slice(Math.max(0, i - windowMin + 1), i + 1)
      .filter(v => v != null) as number[]
    out.push(slice.length ? slice.reduce((a, b) => a + b, 0) / slice.length : null)
  }
  return out
}

function cleanZeros(arr: (number | null)[], minValid = 1): (number | null)[] {
  return arr.map(v => (v == null || v <= minValid ? null : v))
}

// Soil chart: single device per chart (for recent readings style)
function soilChartDataSingleDevice(device: string, label: string): ChartData<'line'> {
  const deviceData = soilRaw.value.filter(r => r.devicename === device)
  const allTimestamps = deviceData.map(r => r.timestamp).sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
  const labels = allTimestamps.map(ts => {
    const dt = new Date(ts)
    return `${dt.getHours()}:${String(dt.getMinutes()).padStart(2, '0')}`
  })
  const temps = deviceData.map(d => d.soil_temp ?? 0)
  const cleaned = cleanZeros(temps)
  const smoothed = movingAvg(cleaned, 5)
  const valid = cleaned.filter(v => v != null) as number[]
  const avgVal = valid.length ? Math.round(valid.reduce((a, b) => a + b, 0) / valid.length) : 0
  return {
    labels,
    datasets: [
      {
        label: `${device} ${label}`,
        data: cleaned,
        borderColor: `hsl(30, 80%, 50%)`,
        pointRadius: 6, // Increased marker size
        spanGaps: true,
        fill: false,
      },
      {
        label: `${device} Smoothed ${label}`,
        data: smoothed,
        borderColor: `hsl(210, 80%, 60%)`,
        borderDash: [6, 6],
        pointRadius: 0,
        spanGaps: true,
        fill: false,
      },
      {
        label: `${device} Avg ${label}`,
        data: Array(labels.length).fill(avgVal),
        borderColor: `hsl(60, 80%, 40%)`,
        borderDash: [4, 4],
        pointRadius: 0,
        fill: false,
      }
    ]
  }
}

// Add reactive state for series visibility per device
const soilSeriesVisible = reactive<Record<string, [boolean, boolean, boolean]>>({})

// Initialize series visibility for each device
watchEffect(() => {
  for (const device of selected.value) {
    if (!soilSeriesVisible[device]) {
      soilSeriesVisible[device] = [true, true, true]
    }
  }
})

// Toggle handler
function toggleSeries(device: string, idx: number) {
  if (!soilSeriesVisible[device]) return
  soilSeriesVisible[device][idx] = !soilSeriesVisible[device][idx]
}

// Chart data builder with toggles
function soilChartDataSingleDeviceWithToggle(device: string, label: string): ChartData<'line'> {
  const deviceData = soilRaw.value.filter(r => r.devicename === device)
  const allTimestamps = deviceData.map(r => r.timestamp).sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
  const labels = allTimestamps.map(ts => {
    const dt = new Date(ts)
    return `${dt.getHours()}:${String(dt.getMinutes()).padStart(2, '0')}`
  })
  const temps = deviceData.map(d => d.soil_temp ?? 0)
  const cleaned = cleanZeros(temps)
  const smoothed = movingAvg(cleaned, 5)
  const valid = cleaned.filter(v => v != null) as number[]
  const avgVal = valid.length ? Math.round(valid.reduce((a, b) => a + b, 0) / valid.length) : 0
  const visible = soilSeriesVisible[device] || [true, true, true]
  const datasets: ChartData<'line'>['datasets'] = []
  if (visible[0]) {
    datasets.push({
      label: `${device} Raw`,
      data: cleaned,
      borderColor: `hsl(30, 80%, 50%)`,
      pointRadius: 6,
      spanGaps: true,
      fill: false,
    })
  }
  if (visible[1]) {
    datasets.push({
      label: `${device} Smoothed`,
      data: smoothed,
      borderColor: `hsl(210, 80%, 60%)`,
      borderDash: [6, 6],
      pointRadius: 0,
      spanGaps: true,
      fill: false,
    })
  }
  if (visible[2]) {
    datasets.push({
      label: `${device} Avg`,
      data: Array(labels.length).fill(avgVal),
      borderColor: `hsl(60, 80%, 40%)`,
      borderDash: [4, 4],
      pointRadius: 0,
      fill: false,
    })
  }
  return {
    labels,
    datasets
  }
}

const soilOptions: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'category',      // now using string categories
      ticks: {
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 12,
      },
    },
    y: {
      // your y‑axis settings…
    },
  },
  plugins: {
    decimation: { enabled: true, algorithm: 'lttb', samples: 60 },
    tooltip: {
      callbacks: {
        afterBody(items) {
          const item = items?.[0]
          if (!item) return ''
          const lbl = String(item.dataset?.label ?? '')
          const v = item.parsed?.y
          if (v == null) return ''
          const isTemp = lbl.includes('Temp')
          const range = TEMP_RANGE
          if (v < range.low)  return isTemp ? 'Below ideal range' : 'Too dry'
          if (v > range.high) return isTemp ? 'Above ideal range' : 'Too wet'
          return isTemp ? 'Within ideal range' : 'Healthy moisture'
        },
      },
    },
  },
}

/* ── CO₂ Forecast ─────────────────── */
const CO2_UNIT = 'ppm'
const FORECAST_RATIO = 0.25
const co2Raw = ref<CO2Reading[]>([])
const bucket = 60    // minutes per bucket
const windowMin = 1440  // minutes back (24 hrs)

watchEffect(async () => {
  const qs = new URLSearchParams({
    bucket_min: bucket.toString(),
    window_min: windowMin.toString(),
  }).toString()

  // now you get one averaged co2 point per hour for the past day
  co2Raw.value = await $fetch<CO2Reading[]>(
    `http://localhost:3001/soil-temp-co2?${qs}`
  )
})

function movingCo2Avg(data: number[], windowSize: number): number[] {
  const result = []
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - windowSize + 1)
    const slice = data.slice(start, i + 1)
    const avg = slice.reduce((a, b) => a + b, 0) / slice.length
    result.push(+avg.toFixed(2))
  }
  return result
}

const filteredCo2Raw = computed(() => {
  if (!selected.value.length) return co2Raw.value
  return co2Raw.value.filter(row => selected.value.includes(row.devicename))
})

// CO2 chart: only actual lines for each device
const co2Data = computed<ChartData<'line'>>(() => {
  // Use selected devices only
  const devices = co2ChartDevices.value.length ? co2ChartDevices.value : Array.from(new Set(co2Raw.value.map(r => r.devicename)));
  // Collect all timestamps for x-axis
  const allTimestamps = Array.from(new Set(co2Raw.value.map(r => r.timestamp))).sort((a, b) => new Date(a).getTime() - new Date(b).getTime())
  const labels = allTimestamps.map(ts => {
    const dt = new Date(ts)
    return `${dt.getHours()}:${String(dt.getMinutes()).padStart(2, '0')}`
  })
  // Build dataset for each device
  const datasets = devices.map((device) => {
    const deviceData = co2Raw.value.filter(r => r.devicename === device)
    // Map to all timestamps
    const dataMap = Object.fromEntries(deviceData.map(r => [r.timestamp, r.co2 ?? null]))
    const values = allTimestamps.map(ts => dataMap[ts] ?? null)
    return {
      label: `${device} CO₂ (Actual) (${CO2_UNIT})`,
      data: values,
      borderColor: co2DeviceColorMap.value[device], // <-- use color map by device name
      pointRadius: 6,
      fill: false
    }
  })
  return { labels, datasets }
})

const co2Options: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'category',
      ticks: { autoSkip: true, maxTicksLimit: 8, maxRotation: 0 }
    },
    y: {
      title: { display: true, text: `CO₂ (${CO2_UNIT})` }
    }
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
function buildSoilRows(label: 'Soil Temp (°C') {
  // This function is currently unused in the UI, but kept for export helpers
  // If you want to export per-device data, you can loop over selected devices and use soilChartDataSingleDevice
  // For now, just return an empty array to avoid lint errors
  return []
}

function buildNPKRowsFiltered() {
  return filteredNpkData.value.map(r => ({
    timestamp: r.timestamp,
    devicename: r.devicename,
    nitrogen: r.nitrogen ?? '',
    phosphorus: r.phosphorus ?? '',
    potassium: r.potassium ?? ''
  }))
}

function buildSoilRowsFiltered() {
  return filteredSoilRaw.value.map(r => ({
    timestamp: r.timestamp,
    devicename: r.devicename,
    soil_temp: r.soil_temp ?? ''
  }))
}

function buildCO2RowsFiltered() {
  return filteredCo2Raw.value.map(r => ({
    timestamp: r.timestamp,
    devicename: r.devicename,
    co2: r.co2 ?? ''
  }))
}

/* new export panel */
type ExportFmt = 'csv' | 'xlsx'


async function exportSelected(fmt: ExportFmt) {
  const npkRows = buildNPKRowsFiltered()
  const soilRows = buildSoilRowsFiltered()
  const co2Rows = buildCO2RowsFiltered()

  if (fmt === 'csv') {
    downloadBlob('npk.csv', toCSV(npkRows, ['timestamp', 'devicename', 'nitrogen', 'phosphorus', 'potassium']))
    downloadBlob('soil_temp.csv', toCSV(soilRows, ['timestamp', 'devicename', 'soil_temp']))
    downloadBlob('co2.csv', toCSV(co2Rows, ['timestamp', 'devicename', 'co2']))
    return
  }

  const XLSX = await import(/* @vite-ignore */ 'xlsx')
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(npkRows), 'NPK')
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(soilRows), 'Soil Temp')
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(co2Rows), 'CO2')

  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  downloadBlob('selected_data.xlsx', wbout, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
}

async function downloadFullReport() {
  // Gather all filtered data
  const npkRows = buildNPKRowsFiltered()
  const soilRows = buildSoilRowsFiltered()
  const co2Rows = buildCO2RowsFiltered()

  // Build a map for quick lookup
  const key = (row: any) => `${row.timestamp}|${row.devicename}`
  const merged: Record<string, any> = {}

  npkRows.forEach(row => {
    merged[key(row)] = {
      timestamp: row.timestamp,
      devicename: row.devicename,
      nitrogen: row.nitrogen,
      phosphorus: row.phosphorus,
      potassium: row.potassium,
      soil_temp: '',
      co2: ''
    }
  })

  soilRows.forEach(row => {
    const k = key(row)
    if (!merged[k]) {
      merged[k] = {
        timestamp: row.timestamp,
        devicename: row.devicename,
        nitrogen: '',
        phosphorus: '',
        potassium: '',
        soil_temp: row.soil_temp,
        co2: ''
      }
    } else {
      merged[k].soil_temp = row.soil_temp
    }
  })

  co2Rows.forEach(row => {
    const k = key(row)
    if (!merged[k]) {
      merged[k] = {
        timestamp: row.timestamp,
        devicename: row.devicename,
        nitrogen: '',
        phosphorus: '',
        potassium: '',
        soil_temp: '',
        co2: row.co2
      }
    } else {
      merged[k].co2 = row.co2
    }
  })

  // Convert merged object to array
  const allRows = Object.values(merged)

  // Export as CSV
  const csvContent = toCSV(
    allRows,
    ['timestamp', 'devicename', 'nitrogen', 'phosphorus', 'potassium', 'soil_temp', 'co2']
  );
  downloadBlob('full_report.csv', csvContent);
}


/* ── Chart Download Functions ─────────────────── */
const soilTempChartRefs = ref<any[]>([])

function setSoilTempChartRef(el: any, idx: number) {
  if (!el) return
  soilTempChartRefs.value[idx] = el
}

function downloadSingleSoilChart(idx: number, device: string) {
  // Use canvas ID to get the chart image, matching live-plant.vue
  const canvasId = `soil-temp-chart-${idx}`;
  const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
  if (!canvas) {
    alert('Chart image could not be generated. Please ensure the chart is visible.');
    return;
  }
  const link = document.createElement('a');
  link.download = `Soil_Temp_${device}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

function downloadChartImage(chartRef: string) {
  // Use canvas ID for CO2 chart
  let canvasId = '';
  if (chartRef === 'co2Chart') canvasId = 'co2-chart';
  const canvas = document.getElementById(canvasId) as HTMLCanvasElement;
  if (!canvas) {
    alert('Chart image could not be generated. Please ensure the chart is visible.');
    return;
  }
  const link = document.createElement('a');
  link.download = 'CO2_Chart.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
}

/* ── Refs for Chart Instances ─────────────────── */
import type { ComponentPublicInstance } from 'vue'

type ChartComponentRef = ComponentPublicInstance<{ chartInstance?: any }>

const soilTempChart = ref<ChartComponentRef | null>(null)
const co2Chart = ref<ChartComponentRef | null>(null)


/* ── Device slicer ─────────────────── */
const options = computed(() => allDeviceNamesRaw.value.filter(d => !selected.value.includes(d)))
const allSelected = computed(() =>
  allDeviceNamesRaw.value.length > 0 && selected.value.length === allDeviceNamesRaw.value.length
)

// Modal filter state
const showDeviceModal = ref(false)
const deviceSearch = ref('')
const modalSelected = ref<string[]>([])

const filteredDeviceOptions = computed(() => {
  const search = deviceSearch.value.trim().toLowerCase()
  if (!search) return allDeviceNamesRaw.value
  return allDeviceNamesRaw.value.filter(d => d.toLowerCase().includes(search))
})

function selectAllDevices() {
  modalSelected.value = [...filteredDeviceOptions.value]
}
function clearAllDevices() {
  modalSelected.value = []
}
function confirmDeviceSelection() {
  selected.value = [...modalSelected.value]
  co2ChartDevices.value = [...selected.value]
  showDeviceModal.value = false
}

// Keep modalSelected in sync with selected when opening modal
watchEffect(() => {
  if (showDeviceModal.value) {
    modalSelected.value = [...selected.value]
  }
})

function toggleDevice(dev: string) {
  if (selected.value.includes(dev)) {
    selected.value = selected.value.filter(d => d !== dev)
  } else {
    selected.value = [...selected.value, dev]
  }
}

function remove(dev: string) { 
  selected.value = selected.value.filter(d => d !== dev)
  co2ChartDevices.value = [...selected.value]
}
function clearAll() {
  selected.value = []
  co2ChartDevices.value = []
}

// State for CO₂ chart device filter
const co2ChartDevices = ref<string[]>([]);

// Initialize with all selected devices
watchEffect(() => {
  if (!co2ChartDevices.value.length && selected.value.length) {
    co2ChartDevices.value = [...selected.value]
  }
})

// Toggle device filter for CO₂ chart
function toggleCo2Device(dev: string) {
  if (co2ChartDevices.value.includes(dev)) {
    co2ChartDevices.value = co2ChartDevices.value.filter(d => d !== dev)
    // If none selected, show all
    if (co2ChartDevices.value.length === 0) {
      co2ChartDevices.value = [...selected.value]
    }
  } else {
    co2ChartDevices.value.push(dev)
  }
}

function getDeviceColor(idx: number) {
  // Generates visually distinct HSL colors
  return `hsl(${(idx * 47) % 360}, 80%, 55%)`
}

// Map device name to color based on its index in selected

const co2DeviceColorMap = computed(() => {
  const map = {} as Record<string, string>
  const devices = co2ChartDevices.value.length
    ? co2ChartDevices.value
    : selected.value
  devices.forEach((dev, idx) => {
    map[dev] = getDeviceColor(idx)
  })
  return map
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
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
.pill {
  transition: opacity 0.2s;
  cursor: pointer;
}
.swatch {
  display: inline-block;
  vertical-align: middle;
}
.swatch.dashed {
  border-style: dashed;
}
.swatch.dot {
  border-style: dotted;
}
.download-btn:hover {
  background: #c2410c;
  color: #fff;
  border-color: #ea580c;
  cursor: pointer;
}
.download-btn:hover .download-icon {
  color: #fff;
  stroke: #fff;
}
.download-icon {
  color: #ea580c;
  stroke: #ea580c;
  transition: color 0.2s, stroke 0.2s;
}
.clear-all-btn:hover {
  cursor: pointer;
}
.export-data-btn:hover {
  cursor: pointer;
}
.export-summary-btn:hover {
  cursor: pointer;
}
.pill-remove-btn:hover {
  cursor: pointer;
}
.co2-pill {
  border-style: solid;
  box-shadow: 0 0 0 1.5px #fff2;
  cursor: pointer;
}
.co2-pill:hover {
  box-shadow: 0 0 0 2px #fff3, 0 2px 8px #0002;
  opacity: 1;
}
.orange-glow {
  box-shadow:
    0 2px 16px 0 #ea580c33,
    0 0 0 1.5px #fff2,
    0 1px 8px #0002;
  transition: box-shadow 0.3s cubic-bezier(0.4,0,0.2,1);
}
.orange-glow:hover {
  box-shadow:
    0 4px 32px 0 #ea580c66,
    0 0 0 2px #ea580c99,
    0 2px 16px #0004;
}
</style>


