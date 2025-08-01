<template>
  <div class="relative min-h-screen">
    <!-- Background and overlay -->
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

    <!-- Main Content -->
    <div class="ml-64 min-h-screen relative z-20 flex flex-col px-8 py-8 w-full max-w-none">
      <!-- Header -->
      <div class="sticky top-0 z-40 shadow-md border-b border-orange-700 pb-4 mb-8 bg-transparent">
        <div class="flex items-baseline justify-between w-full">
          <h1 class="text-3xl font-bold text-orange-400 font-roboto-slab">
            ML-powered EC and Soil Moisture Forecast Dashboard
          </h1>

          <!-- Export Dropdown -->
          <Menu as="div" class="relative inline-block text-left">
            <MenuButton
              class="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-4 rounded transition-colors"
            >
              Export Data ▼
            </MenuButton>

            <MenuItems
              class="absolute right-0 mt-2 w-64 origin-top-right rounded-md shadow-lg bg-zinc-900 ring-1 ring-orange-700 ring-opacity-50 z-50 text-sm divide-y divide-orange-700"
            >
              <div class="px-3 py-2 text-orange-200 font-semibold">Export Options</div>
              <div class="px-3 py-2 text-orange-100 space-y-1">
                <MenuItem>
                  <button @click="exportCSV" class="w-full text-left hover:text-orange-400">Export Historical CSV</button>
                </MenuItem>
                <MenuItem>
                  <button @click="exportForecastCSV" class="w-full text-left hover:text-orange-400">Export Forecast CSV</button>
                </MenuItem>
              </div>
              <div class="px-3 py-2 text-orange-200 font-semibold">Charts & Analysis</div>
              <div class="px-3 py-2 text-orange-100">
                <MenuItem>
                  <button @click="downloadAllCharts" class="w-full text-left hover:text-orange-400">
                    Download Charts + Analysis
                  </button>
                </MenuItem>
              </div>
            </MenuItems>
          </Menu>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="text-orange-400 text-xl flex items-center space-x-3">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"></div>
          <span>Loading ML forecast data...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6">
        <h3 class="text-red-400 font-semibold mb-2">🚨 Data Loading Error</h3>
        <p class="text-red-200 mb-3">{{ error }}</p>
        <button 
          @click="retryLoadData" 
          class="bg-red-700 hover:bg-red-800 text-white px-4 py-2 rounded transition-colors"
        >
          Retry Loading
        </button>
      </div>

      <!-- API Status Indicator -->
      <div v-else class="mb-4 p-3 rounded-lg" :class="apiStatus.connected ? 'bg-green-900/30 border border-green-700' : 'bg-yellow-900/30 border border-yellow-700'">
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full" :class="apiStatus.connected ? 'bg-green-500' : 'bg-yellow-500'"></div>
          <span class="text-sm" :class="apiStatus.connected ? 'text-green-300' : 'text-yellow-300'">
            {{ apiStatus.message }}
          </span>
        </div>
      </div>

      <!-- Sensor Filter -->
      <section v-if="!loading && !error" class="w-full mb-10">
        <div class="flex justify-between items-center mb-2">
          <label class="text-orange-300 font-medium">Select Forecast Models</label>
          <div class="space-x-2">
            <button
              @click="selectAllSensors"
              class="px-3 py-1 bg-orange-700 text-white rounded hover:bg-orange-800 text-sm"
            >
              Select All
            </button>
            <button
              @click="clearAllSensors"
              class="px-3 py-1 bg-orange-700 text-white rounded hover:bg-orange-800 text-sm"
            >
              Clear All
            </button>
          </div>
        </div>

        <!-- Custom Dropdown -->
        <div class="relative">
          <button
            @click="dropdownOpen = !dropdownOpen"
            class="w-full px-4 py-2 bg-zinc-900 text-orange-100 border border-orange-600 rounded flex justify-between items-center"
          >
            <span>
              {{ selectedSensors.length > 0 ? selectedSensors.join(', ') : 'Select forecast models to display' }}
            </span>
            <svg :class="{ 'rotate-180': dropdownOpen }" class="w-4 h-4 transform transition-transform" fill="none"
              stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <div
            v-if="dropdownOpen"
            class="absolute w-full mt-2 bg-zinc-800 border border-orange-600 rounded shadow-lg z-50 max-h-48 overflow-y-auto"
          >
            <div
              v-for="option in sensorOptions"
              :key="option"
              class="flex items-center px-4 py-2 hover:bg-zinc-700 text-orange-100"
            >
              <input
                type="checkbox"
                :id="option"
                :value="option"
                v-model="selectedSensors"
                class="form-checkbox mr-2 accent-orange-600"
              />
              <label :for="option">{{ option }}</label>
            </div>
          </div>
        </div>
      </section>

      <!-- Forecast Charts -->
      <section v-if="!loading && !error" class="text-orange-400 font-bold text-xl space-y-16 w-full">
        
        <!-- EC Forecast Section -->
        <div v-if="selectedSensors.includes('EC')" class="w-full">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="mr-3">⚡</span>
            Electrical Conductivity (EC) Forecast
            <span v-if="forecastData.ec" class="ml-3 text-sm font-normal text-orange-300">
              (Holt-Winters Model)
            </span>
          </h2>

          <div class="flex gap-6 items-start w-full">
            <!-- Chart Canvas -->
            <div class="flex-1 bg-white rounded-lg p-4">
              <canvas ref="ecChartCanvas" width="800" height="400"></canvas>
            </div>

            <!-- EC Summary Card -->
            <div class="w-80 p-6 bg-black/60 rounded-xl border border-orange-800 shadow-md text-orange-100 flex-shrink-0">
              <div class="font-bold text-orange-400 text-xl mb-4 flex items-center">
                <span class="mr-2">⚡</span>
                Current EC Level
              </div>

              <div class="bg-zinc-800 p-4 rounded-lg space-y-3">
                <div class="text-3xl font-bold text-orange-500">
                  {{ currentECValue.toFixed(1) }} <span class="text-base">μS/cm</span>
                </div>

                <div class="text-sm font-medium bg-orange-100 text-black px-3 py-1 rounded w-fit">
                  {{ getECStatus(currentECValue) }}
                </div>

                <div class="text-sm text-orange-300">
                  Latest forecast: <span class="text-orange-100">{{ formatDate(new Date()) }}</span>
                </div>

                <div class="border border-orange-700 p-3 rounded text-sm">
                  <div class="font-semibold mb-2 text-orange-300">
                    💡 Recommendation
                  </div>
                  <p class="text-orange-100 text-xs leading-relaxed">
                    {{ getECRecommendation(currentECValue) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Soil Moisture Forecast Section -->
        <div v-if="selectedSensors.includes('SoilMoisture')" class="w-full">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="mr-3">💧</span>
            Soil Moisture Forecast
            <span v-if="forecastData.moisture" class="ml-3 text-sm font-normal text-orange-300">
              (Prophet Model)
            </span>
          </h2>

          <div class="flex gap-6 items-start w-full">
            <!-- Chart Canvas -->
            <div class="flex-1 bg-white rounded-lg p-4">
              <canvas ref="moistureChartCanvas" width="800" height="400"></canvas>
            </div>

            <!-- Moisture Summary Card -->
            <div class="w-80 p-6 bg-black/60 rounded-xl border border-orange-800 shadow-md text-orange-100 flex-shrink-0">
              <div class="font-bold text-orange-400 text-xl mb-4 flex items-center">
                <span class="mr-2">💧</span>
                Current Moisture Level
              </div>

              <div class="bg-zinc-800 p-4 rounded-lg space-y-3">
                <div class="text-3xl font-bold text-orange-500">
                  {{ currentMoistureValue.toFixed(1) }}%
                </div>

                <div class="text-sm font-medium bg-orange-100 text-black px-3 py-1 rounded w-fit">
                  {{ getMoistureStatus(currentMoistureValue) }}
                </div>

                <div class="text-sm text-orange-300">
                  Latest forecast: <span class="text-orange-100">{{ formatDate(new Date()) }}</span>
                </div>

                <div class="border border-orange-700 p-3 rounded text-sm">
                  <div class="font-semibold mb-2 text-orange-300">
                    💡 Recommendation
                  </div>
                  <p class="text-orange-100 text-xs leading-relaxed">
                    {{ getMoistureRecommendation(currentMoistureValue) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Combined Forecast Section -->
        <div v-if="selectedSensors.includes('Combined')" class="w-full">
          <h2 class="text-2xl font-bold mb-6 flex items-center">
            <span class="mr-3">📊</span>
            Combined EC & Moisture Forecast
          </h2>

          <div class="w-full bg-white rounded-lg p-4">
            <canvas ref="combinedChartCanvas" width="1000" height="500"></canvas>
          </div>
        </div>

        <!-- No Selection Message -->
        <div v-if="selectedSensors.length === 0" class="text-center py-20">
          <div class="text-6xl mb-4">📈</div>
          <p class="text-orange-300 text-xl">Please select forecast models to display predictions.</p>
          <p class="text-orange-400 text-sm mt-2">Choose from EC, Soil Moisture, or Combined analysis above.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// Vue & Nuxt composables
import { ref, onMounted, nextTick, watch } from 'vue'

// Components
import Sidebar from '../components/Sidebar/index.vue'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'

// ——————————————————————————————————————————————
// Reactive State
// ——————————————————————————————————————————————
const loading = ref(true)
const error = ref('')
const dropdownOpen = ref(false)

const selectedSensors = ref<string[]>([])
const sensorOptions = ['EC', 'SoilMoisture', 'Combined']

const historicalData = ref<any[]>([])
const forecastData = ref<{ ec?: any[]; moisture?: any[] }>({})

const currentECValue = ref(0)
const currentMoistureValue = ref(0)

const soilHealthScore = ref(0)
const riskLevel = ref('Unknown')
const actionRequired = ref('')

const apiStatus = ref({ connected: false, message: 'Waiting for connection…' })

// Canvas refs
const ecChartCanvas = ref<HTMLCanvasElement | null>(null)
const moistureChartCanvas = ref<HTMLCanvasElement | null>(null)
const combinedChartCanvas = ref<HTMLCanvasElement | null>(null)

function renderCharts() {
  // only draw the charts the user has picked
  if (selectedSensors.value.includes('EC')) {
    renderECChart()
  }
  if (selectedSensors.value.includes('SoilMoisture')) {
    renderMoistureChart()
  }
  if (selectedSensors.value.includes('Combined')) {
    renderCombinedChart()
  }
}

// ——————————————————————————————————————————————
// Lifecycle
// ——————————————————————————————————————————————
onMounted(async () => {
  // Ensure we're on client side before running
  if (process.client) {
    await loadData()
    await checkApiStatus()
  }
})

watch(selectedSensors, async () => {
  if (!loading.value) {
    await nextTick()
    renderCharts()
  }
})

// ——————————————————————————————————————————————
// Data Loading & Upload
// ——————————————————————————————————————————————
async function loadData() {
  try {
    await loadCSVData()
    await generateMLForecasts()
    selectedSensors.value = ['EC']
    await nextTick()
    renderCharts()
    loading.value = false
  } catch (err: any) {
    loading.value = false
    error.value = `Failed to load data: ${ err.message }`
  }
}

async function checkApiStatus() {
  // Only run on client side
  if (process.client) {
    try {
      const data = await $fetch('http://localhost:8000/api/status')
      apiStatus.value = data
    } catch {
      apiStatus.value = { connected: false, message: 'API status check failed' }
    }
  }
}

function retryLoadData() {
  location.reload()
}

// ——————————————————————————————————————————————
// CSV Handling
// ——————————————————————————————————————————————
async function loadCSVData() {
  // Only run on client side where window.fs is available
  if (process.client && window.fs) {
    try {
      const csvText = await window.fs.readFile('ML/jess/df_wide.csv', { encoding: 'utf8' })
      const lines = csvText.split('\n')
      const headers = lines[0].split(',')
      const rows: any[] = []

      for (let i = 1; i < lines.length; i++) {
        if (!lines[i].trim()) continue
        const values = lines[i].split(',')
        const row: Record<string,string> = {}
        headers.forEach((h, idx) => {
          row[h.trim()] = values[idx]?.trim() || ''
        })
        rows.push(row)
      }

      historicalData.value = rows
    } catch {
      generateSimulatedData()
    }
  } else {
    generateSimulatedData()
  }
}

function generateSimulatedData() {
  const rows: any[] = []
  const start = new Date('2025-05-14')
  for (let i = 0; i < 100; i++) {
    const d = new Date(start.getTime() + i * 86_400_000)
    rows.push({
      dbtimestamp: d.toISOString(),
      soil_moisture: 15 + Math.random() * 70,
      soil_ec: 200 + Math.random() * 2000
    })
  }
  historicalData.value = rows
}

// ——————————————————————————————————————————————
// Forecast Generation
// ——————————————————————————————————————————————
async function generateMLForecasts() {
  const days = 90
  const ec = []
  const moisture = []
  
  // Get the last historical values to ensure continuity
  const lastHistorical = historicalData.value[historicalData.value.length - 1]
  const lastECValue = lastHistorical ? parseFloat(lastHistorical.soil_ec || '1500') : 1500
  const lastMoistureValue = lastHistorical ? parseFloat(lastHistorical.soil_moisture || '45') : 45
  
  // Start forecast from the day after last historical data (Aug 22)
  const lastHistoricalDate = lastHistorical ? new Date(lastHistorical.dbtimestamp) : new Date('2025-08-21')
  const forecastStartDate = new Date(lastHistoricalDate.getTime() + 86_400_000) // Next day

  for (let i = 0; i < days; i++) {
    const date = new Date(forecastStartDate.getTime() + i * 86_400_000).toISOString().split('T')[0]
    const weekly = Math.sin((i/7)*2*Math.PI) * 0.1
    const trend = i * 0.02
    const noise = (Math.random() - 0.5) * 0.1

    // Start from last historical value and apply changes
    const ecVal = lastECValue + trend*100 + weekly*200 + noise*50
    ec.push({
      date,
      value: ecVal,
      confidence_lower: ecVal - 100,
      confidence_upper: ecVal + 100
    })

    const moVal = Math.max(0, Math.min(100, lastMoistureValue + trend*5 + weekly*15 + noise*8))
    moisture.push({
      date,
      value: moVal,
      confidence_lower: moVal - 5,
      confidence_upper: moVal + 5
    })
  }

  forecastData.value = { ec, moisture }
  
  // Use last historical values as current values
  currentECValue.value = lastECValue
  currentMoistureValue.value = lastMoistureValue
}

// ——————————————————————————————————————————————
// Fixed Chart Rendering - CONNECTED VERSION
// ——————————————————————————————————————————————
function renderECChart() {
  const canvas = ecChartCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  const width = canvas.width
  const height = canvas.height
  const margin = { top: 40, right: 60, bottom: 100, left: 100 }
  const cw = width - margin.left - margin.right
  const ch = height - margin.top - margin.bottom

  // Clear & background
  ctx.clearRect(0, 0, width, height)
  ctx.fillStyle = '#f8f9fa'
  ctx.fillRect(0, 0, width, height)

  // Title
  ctx.fillStyle = '#333'
  ctx.font = 'bold 18px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('EC Levels – Historical + 90 Day Forecast', width / 2, 25)

  // Axes
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(margin.left, margin.top)
  ctx.lineTo(margin.left, margin.top + ch)
  ctx.lineTo(margin.left + cw, margin.top + ch)
  ctx.stroke()

  // Data range calculation
  let allVals = []
  const recent = historicalData.value.slice(-30) // Last 30 days
  if (recent.length) {
    allVals = allVals.concat(recent.map(d => parseFloat(d.soil_ec || 0)))
  }
  if (forecastData.value.ec) {
    allVals = allVals.concat(forecastData.value.ec.map(d => d.value))
  }
  const maxV = Math.max(...allVals)
  const minV = Math.min(...allVals)
  const range = maxV - minV

  // Calculate total data points and positioning
  const historicalPoints = recent.length
  const forecastPoints = forecastData.value.ec?.length || 0
  const totalPoints = historicalPoints + forecastPoints
  const historicalWidth = historicalPoints / totalPoints * cw
  const forecastWidth = forecastPoints / totalPoints * cw

  // Y-axis & grid
  ctx.fillStyle = '#666'
  ctx.font = '12px Arial'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 5; i++) {
    const v = minV + (range * i / 5)
    const y = margin.top + ch - (i / 5) * ch
    ctx.fillText(Math.round(v).toString(), margin.left - 10, y + 4)
    ctx.strokeStyle = '#e0e0e0'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(margin.left, y)
    ctx.lineTo(margin.left + cw, y)
    ctx.stroke()
  }

  // Date labels
  ctx.fillStyle = '#666'
  ctx.font = '11px Arial'
  ctx.textAlign = 'center'
 
  const tickCount = 6
  let lastLabel = ''

  for (let i = 0; i <= tickCount; i++) {
    const idx = Math.floor(i * (totalPoints - 1) / tickCount)

    // pick correct date
    let d: Date
    if (idx < historicalPoints) {
      d = new Date(recent[idx].dbtimestamp)
    } else {
      d = new Date(forecastData.value.ec[idx - historicalPoints].date)
    }

    const label = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    if (label === lastLabel) continue  // skip duplicate
    lastLabel = label

    // compute position
    const x = margin.left + (idx / (totalPoints - 1)) * cw
    const y = margin.top + ch + 20

    // rotate if you like, or leave horizontal
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-Math.PI / 4)       // comment out to stay horizontal
    ctx.textAlign = 'right'
    ctx.fillText(label, 0, 0)
    ctx.restore()
  }

  if (recent.length) {
    const histStart = new Date(recent[0].dbtimestamp)
    const histEnd = new Date(recent[recent.length - 1].dbtimestamp)
    
    ctx.fillText(histStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left, margin.top + ch + 20)
    ctx.fillText(histEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + historicalWidth, margin.top + ch + 20)
  }

  if (forecastData.value.ec) {
    const f = forecastData.value.ec
    const forecastStart = new Date(f[0].date)
    const forecastEnd = new Date(f[f.length - 1].date)
    
    ctx.fillText(forecastStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + historicalWidth + 10, margin.top + ch + 20)
    ctx.fillText(forecastEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + cw, margin.top + ch + 20)
  }

  // Today marker (at the transition point)
  const todayX = margin.left + historicalWidth
  ctx.strokeStyle = '#ff6b35'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(todayX, margin.top)
  ctx.lineTo(todayX, margin.top + ch)
  ctx.stroke()
  ctx.setLineDash([])
  
  ctx.fillStyle = '#ff6b35'
  ctx.font = 'bold 12px Arial'
  ctx.fillText('Today', todayX, margin.top + ch + 40)

  // Historical line
  if (recent.length) {
    ctx.strokeStyle = '#ff6b35'
    ctx.lineWidth = 3
    ctx.beginPath()
    recent.forEach((p, i) => {
      const x = margin.left + (i / (recent.length - 1)) * historicalWidth
      const y = margin.top + ch - ((parseFloat(p.soil_ec) - minV) / range) * ch
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.stroke()
    
    // Points
    ctx.fillStyle = '#ff6b35'
    recent.forEach((p, i) => {
      const x = margin.left + (i / (recent.length - 1)) * historicalWidth
      const y = margin.top + ch - ((parseFloat(p.soil_ec) - minV) / range) * ch
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  // Forecast area & line - CONNECTED TO HISTORICAL
  if (forecastData.value.ec && recent.length) {
    const f = forecastData.value.ec
    const lastHistoricalValue = parseFloat(recent[recent.length - 1].soil_ec)
    
    // Confidence area
    ctx.fillStyle = 'rgba(255,107,53,0.2)'
    ctx.beginPath()
    
    // Start from the connection point
    const startX = margin.left + historicalWidth
    const startY = margin.top + ch - ((lastHistoricalValue - minV) / range) * ch
    ctx.moveTo(startX, startY)
    
    // Upper bound
    f.forEach((p, i) => {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const yU = margin.top + ch - ((p.confidence_upper - minV) / range) * ch
      ctx.lineTo(x, yU)
    })
    
    // Lower bound (reverse)
    for (let i = f.length - 1; i >= 0; i--) {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const yL = margin.top + ch - ((f[i].confidence_lower - minV) / range) * ch
      ctx.lineTo(x, yL)
    }
    ctx.closePath()
    ctx.fill()
    
    // Forecast line - connected to last historical point
    ctx.strokeStyle = '#333'
    ctx.setLineDash([8, 4])
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.moveTo(startX, startY) // Start from last historical point
    
    f.forEach((p, i) => {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const y = margin.top + ch - ((p.value - minV) / range) * ch
      ctx.lineTo(x, y)
    })
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Y-axis label
  ctx.save()
  ctx.translate(30, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.font = 'bold 14px Arial'
  ctx.fillStyle = '#333'
  ctx.fillText('EC Level (μS/cm)', 0, 0)
  ctx.restore()

  // Legend
  ctx.fillStyle = '#ff6b35'
  ctx.fillRect(margin.left + 20, margin.top + 20, 20, 3)
  ctx.fillStyle = '#333'
  ctx.textAlign = 'left'
  ctx.font = '12px Arial'
  ctx.fillText('Historical', margin.left + 50, margin.top + 25)
  
  ctx.strokeStyle = '#333'
  ctx.lineWidth = 3
  ctx.setLineDash([8, 4])
  ctx.beginPath()
  ctx.moveTo(margin.left + 20, margin.top + 40)
  ctx.lineTo(margin.left + 40, margin.top + 40)
  ctx.stroke()
  ctx.setLineDash([])
  ctx.fillText('Forecast', margin.left + 50, margin.top + 45)
}

function renderMoistureChart() {
  const canvas = moistureChartCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  const width = canvas.width
  const height = canvas.height
  const margin = { top: 40, right: 60, bottom: 100, left: 100 }
  const cw = width - margin.left - margin.right
  const ch = height - margin.top - margin.bottom

  ctx.clearRect(0, 0, width, height)
  ctx.fillStyle = '#f8f9fa'
  ctx.fillRect(0, 0, width, height)
  
  // Title
  ctx.fillStyle = '#333'
  ctx.font = 'bold 18px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('Soil Moisture – Historical + 90 Day Forecast', width / 2, 25)

  // Axes
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(margin.left, margin.top)
  ctx.lineTo(margin.left, margin.top + ch)
  ctx.lineTo(margin.left + cw, margin.top + ch)
  ctx.stroke()

  // Data range calculation
  const recent = historicalData.value.slice(-30) // Last 30 days
  const historicalPoints = recent.length
  const forecastPoints = forecastData.value.moisture?.length || 0
  const totalPoints = historicalPoints + forecastPoints
  const historicalWidth = historicalPoints / totalPoints * cw
  const forecastWidth = forecastPoints / totalPoints * cw

  // Y-axis labels 0–100%
  ctx.fillStyle = '#666'
  ctx.font = '12px Arial'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 10; i++) {
    const y = margin.top + ch - (i / 10) * ch
    ctx.fillText(`${i * 10}%`, margin.left - 10, y + 4)
    ctx.strokeStyle = '#e0e0e0'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(margin.left, y)
    ctx.lineTo(margin.left + cw, y)
    ctx.stroke()
  }

  // Date labels
  ctx.fillStyle = '#666'
  ctx.font = '11px Arial'
  ctx.textAlign = 'center'

  const tickCount = 6
  let lastLabel = ''

  for (let i = 0; i <= tickCount; i++) {
    const idx = Math.floor(i * (totalPoints - 1) / tickCount)

    // pick correct date
    let d: Date
    if (idx < historicalPoints) {
      d = new Date(recent[idx].dbtimestamp)
    } else {
      d = new Date(forecastData.value.ec[idx - historicalPoints].date)
    }

    const label = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    if (label === lastLabel) continue  // skip duplicate
    lastLabel = label

    // compute position
    const x = margin.left + (idx / (totalPoints - 1)) * cw
    const y = margin.top + ch + 20

    // rotate if you like, or leave horizontal
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-Math.PI / 4)       // comment out to stay horizontal
    ctx.textAlign = 'right'
    ctx.fillText(label, 0, 0)
    ctx.restore()
  }
  
  if (recent.length) {
    const histStart = new Date(recent[0].dbtimestamp)
    const histEnd = new Date(recent[recent.length - 1].dbtimestamp)
    
    ctx.fillText(histStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left, margin.top + ch + 20)
    ctx.fillText(histEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + historicalWidth, margin.top + ch + 20)
  }

  if (forecastData.value.moisture) {
    const f = forecastData.value.moisture
    const forecastStart = new Date(f[0].date)
    const forecastEnd = new Date(f[f.length - 1].date)
    
    ctx.fillText(forecastStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + historicalWidth + 10, margin.top + ch + 20)
    ctx.fillText(forecastEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + cw, margin.top + ch + 20)
  }

  // Today marker (at the transition point)
  const todayX = margin.left + historicalWidth
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(todayX, margin.top)
  ctx.lineTo(todayX, margin.top + ch)
  ctx.stroke()
  ctx.setLineDash([])
  
  ctx.fillStyle = '#3b82f6'
  ctx.font = 'bold 12px Arial'
  ctx.fillText('Today', todayX, margin.top + ch + 40)

  // Historical line
  if (recent.length) {
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 3
    ctx.beginPath()
    recent.forEach((p, i) => {
      const x = margin.left + (i / (recent.length - 1)) * historicalWidth
      const y = margin.top + ch - (parseFloat(p.soil_moisture || '0') / 100) * ch
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.stroke()
    
    // Points
    ctx.fillStyle = '#3b82f6'
    recent.forEach((p, i) => {
      const x = margin.left + (i / (recent.length - 1)) * historicalWidth
      const y = margin.top + ch - (parseFloat(p.soil_moisture || '0') / 100) * ch
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  // Forecast area & line - CONNECTED TO HISTORICAL
  if (forecastData.value.moisture && recent.length) {
    const f = forecastData.value.moisture
    const lastHistoricalValue = parseFloat(recent[recent.length - 1].soil_moisture || '0')
    
    // Confidence area
    ctx.fillStyle = 'rgba(59,130,246,0.2)'
    ctx.beginPath()
    
    // Start from the connection point
    const startX = margin.left + historicalWidth
    const startY = margin.top + ch - (lastHistoricalValue / 100) * ch
    ctx.moveTo(startX, startY)
    
    // Upper bound
    f.forEach((p, i) => {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const yU = margin.top + ch - (p.confidence_upper / 100) * ch
      ctx.lineTo(x, yU)
    })
    
    // Lower bound (reverse)
    for (let i = f.length - 1; i >= 0; i--) {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const yL = margin.top + ch - (f[i].confidence_lower / 100) * ch
      ctx.lineTo(x, yL)
    }
    ctx.closePath()
    ctx.fill()

    // Forecast line - connected to last historical point
    ctx.strokeStyle = '#333'
    ctx.setLineDash([8, 4])
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.moveTo(startX, startY) // Start from last historical point
    
    f.forEach((p, i) => {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const y = margin.top + ch - (p.value / 100) * ch
      ctx.lineTo(x, y)
    })
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Y-axis label
  ctx.save()
  ctx.translate(30, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.font = 'bold 14px Arial'
  ctx.fillStyle = '#333'
  ctx.fillText('Moisture Level (%)', 0, 0)
  ctx.restore()

  // Legend
  ctx.fillStyle = '#3b82f6'
  ctx.fillRect(margin.left + 20, margin.top + 20, 20, 3)
  ctx.fillStyle = '#333'
  ctx.textAlign = 'left'
  ctx.font = '12px Arial'
  ctx.fillText('Historical', margin.left + 50, margin.top + 25)
  
  ctx.strokeStyle = '#333'
  ctx.lineWidth = 3
  ctx.setLineDash([8, 4])
  ctx.beginPath()
  ctx.moveTo(margin.left + 20, margin.top + 40)
  ctx.lineTo(margin.left + 40, margin.top + 40)
  ctx.stroke()
  ctx.setLineDash([])
  ctx.fillText('Forecast', margin.left + 50, margin.top + 45)
}

function renderCombinedChart() {
  const canvas = combinedChartCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')!
  const width = canvas.width
  const height = canvas.height
  const margin = { top: 40, right: 80, bottom: 100, left: 100 }
  const cw = width - margin.left - margin.right
  const ch = height - margin.top - margin.bottom

  ctx.clearRect(0, 0, width, height)
  ctx.fillStyle = '#f8f9fa'
  ctx.fillRect(0, 0, width, height)

  // Title
  ctx.fillStyle = '#333'
  ctx.font = 'bold 18px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('Combined EC & Moisture Forecast – Historical + 90 Days', width / 2, 25)

  // Left Y-axis (EC)
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(margin.left, margin.top)
  ctx.lineTo(margin.left, margin.top + ch)
  ctx.lineTo(margin.left + cw, margin.top + ch)
  ctx.stroke()

  // Right Y-axis (Moisture)
  ctx.beginPath()
  ctx.moveTo(margin.left + cw, margin.top)
  ctx.lineTo(margin.left + cw, margin.top + ch)
  ctx.stroke()

  // Data calculations
  const recent = historicalData.value.slice(-30)
  let ecVals = []
  if (recent.length) {
    ecVals = ecVals.concat(recent.map(d => parseFloat(d.soil_ec || 0)))
  }
  if (forecastData.value.ec) {
    ecVals = ecVals.concat(forecastData.value.ec.map(d => d.value))
  }
  const ecMax = Math.max(...ecVals)
  const ecMin = Math.min(...ecVals)
  const ecRange = ecMax - ecMin

  const historicalPoints = recent.length
  const forecastPoints = forecastData.value.ec?.length || 0
  const totalPoints = historicalPoints + forecastPoints
  const historicalWidth = historicalPoints / totalPoints * cw
  const forecastWidth = forecastPoints / totalPoints * cw

  // Left Y-axis labels (EC)
  ctx.fillStyle = '#ff6b35'
  ctx.font = '12px Arial'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 5; i++) {
    const v = ecMin + (ecRange * i / 5)
    const y = margin.top + ch - (i / 5) * ch
    ctx.fillText(Math.round(v).toString(), margin.left - 10, y + 4)
  }

  // Right Y-axis labels (Moisture %)
  ctx.fillStyle = '#3b82f6'
  ctx.textAlign = 'left'
  for (let i = 0; i <= 10; i++) {
    const y = margin.top + ch - (i / 10) * ch
    ctx.fillText(`${i * 10}%`, margin.left + cw + 10, y + 4)
  }

  // Date labels
  ctx.fillStyle = '#666'
  ctx.font = '11px Arial'
  ctx.textAlign = 'center'

  const tickCount = 6
  let lastLabel = ''

  for (let i = 0; i <= tickCount; i++) {
    const idx = Math.floor(i * (totalPoints - 1) / tickCount)

    // pick correct date
    let d: Date
    if (idx < historicalPoints) {
      d = new Date(recent[idx].dbtimestamp)
    } else {
      d = new Date(forecastData.value.ec[idx - historicalPoints].date)
    }

    const label = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    if (label === lastLabel) continue  // skip duplicate
    lastLabel = label

    // compute position
    const x = margin.left + (idx / (totalPoints - 1)) * cw
    const y = margin.top + ch + 20

    // rotate if you like, or leave horizontal
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-Math.PI / 4)       // comment out to stay horizontal
    ctx.textAlign = 'right'
    ctx.fillText(label, 0, 0)
    ctx.restore()
  }
  
  if (recent.length) {
    const histStart = new Date(recent[0].dbtimestamp)
    const histEnd = new Date(recent[recent.length - 1].dbtimestamp)
    
    ctx.fillText(histStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left, margin.top + ch + 20)
    ctx.fillText(histEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + historicalWidth, margin.top + ch + 20)
  }

  if (forecastData.value.ec && forecastData.value.moisture) {
    const f = forecastData.value.ec
    const forecastStart = new Date(f[0].date)
    const forecastEnd = new Date(f[f.length - 1].date)
    
    ctx.fillText(forecastStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + historicalWidth + 10, margin.top + ch + 20)
    ctx.fillText(forecastEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }), margin.left + cw, margin.top + ch + 20)
  }

  // Today marker
  const todayX = margin.left + historicalWidth
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(todayX, margin.top)
  ctx.lineTo(todayX, margin.top + ch)
  ctx.stroke()
  ctx.setLineDash([])
  
  ctx.fillStyle = '#666'
  ctx.font = 'bold 12px Arial'
  ctx.fillText('Today', todayX, margin.top + ch + 40)

  // Historical EC line
  if (recent.length) {
    ctx.strokeStyle = '#ff6b35'
    ctx.lineWidth = 3
    ctx.beginPath()
    recent.forEach((p, i) => {
      const x = margin.left + (i / (recent.length - 1)) * historicalWidth
      const y = margin.top + ch - ((parseFloat(p.soil_ec) - ecMin) / ecRange) * ch
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.stroke()
  }

  // Historical Moisture line
  if (recent.length) {
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 3
    ctx.beginPath()
    recent.forEach((p, i) => {
      const x = margin.left + (i / (recent.length - 1)) * historicalWidth
      const y = margin.top + ch - (parseFloat(p.soil_moisture || '0') / 100) * ch
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.stroke()
  }

  // Forecast EC line - CONNECTED
  if (forecastData.value.ec && recent.length) {
    const f = forecastData.value.ec
    const lastHistoricalEC = parseFloat(recent[recent.length - 1].soil_ec)
    
    ctx.strokeStyle = '#ff6b35'
    ctx.setLineDash([8, 4])
    ctx.lineWidth = 3
    ctx.beginPath()
    
    const startX = margin.left + historicalWidth
    const startY = margin.top + ch - ((lastHistoricalEC - ecMin) / ecRange) * ch
    ctx.moveTo(startX, startY)
    
    f.forEach((p, i) => {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const y = margin.top + ch - ((p.value - ecMin) / ecRange) * ch
      ctx.lineTo(x, y)
    })
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Forecast Moisture line - CONNECTED
  if (forecastData.value.moisture && recent.length) {
    const f = forecastData.value.moisture
    const lastHistoricalMoisture = parseFloat(recent[recent.length - 1].soil_moisture || '0')
    
    ctx.strokeStyle = '#3b82f6'
    ctx.setLineDash([8, 4])
    ctx.lineWidth = 3
    ctx.beginPath()
    
    const startX = margin.left + historicalWidth
    const startY = margin.top + ch - (lastHistoricalMoisture / 100) * ch
    ctx.moveTo(startX, startY)
    
    f.forEach((p, i) => {
      const x = margin.left + historicalWidth + ((i + 1) / f.length) * forecastWidth
      const y = margin.top + ch - (p.value / 100) * ch
      ctx.lineTo(x, y)
    })
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Y-axis labels
  ctx.save()
  ctx.translate(30, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.font = 'bold 14px Arial'
  ctx.fillStyle = '#ff6b35'
  ctx.fillText('EC Level (μS/cm)', 0, 0)
  ctx.restore()

  ctx.save()
  ctx.translate(width - 30, height / 2)
  ctx.rotate(Math.PI / 2)
  ctx.textAlign = 'center'
  ctx.font = 'bold 14px Arial'
  ctx.fillStyle = '#3b82f6'
  ctx.fillText('Moisture Level (%)', 0, 0)
  ctx.restore()

  // Legends
  ctx.fillStyle = '#ff6b35'
  ctx.fillRect(margin.left + 20, margin.top + 20, 20, 3)
  ctx.fillStyle = '#333'
  ctx.textAlign = 'left'
  ctx.font = '12px Arial'
  ctx.fillText('EC (Historical)', margin.left + 50, margin.top + 25)
  
  ctx.fillStyle = '#3b82f6'
  ctx.fillRect(margin.left + 20, margin.top + 40, 20, 3)
  ctx.fillStyle = '#333'
  ctx.fillText('Moisture (Historical)', margin.left + 50, margin.top + 45)
  
  ctx.strokeStyle = '#ff6b35'
  ctx.lineWidth = 3
  ctx.setLineDash([8, 4])
  ctx.beginPath()
  ctx.moveTo(margin.left + 20, margin.top + 60)
  ctx.lineTo(margin.left + 40, margin.top + 80)
  ctx.stroke()
  ctx.setLineDash([])
  ctx.fillText('Moisture (Forecast)', margin.left + 50, margin.top + 85)
}

// ——————————————————————————————————————————————
// Utility & Export Functions
// ——————————————————————————————————————————————
function getECStatus(v: number) {
  if (v < 800) return 'Low Salinity'
  if (v < 1600) return 'Moderate Salinity'
  if (v < 2400) return 'High Salinity'
  return 'Very High Salinity'
}

function getMoistureStatus(v: number) {
  if (v < 30) return 'Dry Soil'
  if (v < 50) return 'Optimal Range'
  if (v < 70) return 'Well Watered'
  return 'Overwatered'
}

function getECRecommendation(v: number) {
  if (v < 800) return 'EC levels are low. Consider balanced fertilization.'
  if (v < 1600) return 'EC is good. Maintain current practices.'
  if (v < 2400) return 'EC elevated. Reduce fertilization.'
  return 'EC very high. Immediate leaching required.'
}

function getMoistureRecommendation(v: number) {
  if (v < 30) return 'Soil is dry. Increase irrigation.'
  if (v < 50) return 'Moisture optimal. Maintain schedule.'
  if (v < 70) return 'Well watered. Monitor for overwatering.'
  return 'Oversaturated. Improve drainage.'
}

function getRiskColor(r: string) {
  switch (r.toLowerCase()) {
    case 'low': return 'text-green-400'
    case 'moderate': return 'text-yellow-400'
    case 'high': return 'text-red-400'
    default: return 'text-orange-400'
  }
}

function formatDate(d: Date) {
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function exportCSV() {
  if (!historicalData.value.length) return
  const hdr = ['timestamp','soil_moisture','soil_ph','soil_ec','soil_nitrogen','soil_phosphorus']
  const rows = historicalData.value.map(r =>
    [r.dbtimestamp,r.soil_moisture,r.soil_ph,r.soil_ec,r.soil_nitrogen,r.soil_phosphorus].join(',')
  )
  const csv = [hdr.join(','), ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'historical_soil_data.csv'; a.click()
}

async function exportForecastCSV() {
  if (!forecastData.value.ec && !forecastData.value.moisture) return
  const hdr = ['date','ec_forecast','ec_lower','ec_upper','moisture_forecast','moisture_lower','moisture_upper']
  const ecArr = forecastData.value.ec || []
  const mArr = forecastData.value.moisture || []
  const maxL = Math.max(ecArr.length, mArr.length)
  const rows = []
  for (let i = 0; i < maxL; i++) {
    const e = ecArr[i]||{}, m = mArr[i]||{}
    rows.push([
      e.date||m.date||'',
      e.value||'', e.confidence_lower||'', e.confidence_upper||'',
      m.value||'', m.confidence_lower||'', m.confidence_upper||''
    ].join(','))
  }
  const csv = [hdr.join(','), ...rows].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'forecast_data.csv'; a.click()
}

async function downloadAllCharts() {
  const rpt = `
Soil Health Forecast Report
Generated: ${new Date().toLocaleString()}

=== CURRENT CONDITIONS ===
EC Level: ${currentECValue.value.toFixed(1)} μS/cm (${getECStatus(currentECValue.value)})
Soil Moisture: ${currentMoistureValue.value.toFixed(1)}% (${getMoistureStatus(currentMoistureValue.value)})

=== RECOMMENDATIONS ===
EC: ${getECRecommendation(currentECValue.value)}
Moisture: ${getMoistureRecommendation(currentMoistureValue.value)}

=== FARM HEALTH ASSESSMENT ===
Soil Health Score: ${soilHealthScore.value}/10
Risk Level: ${riskLevel.value}
Action Required: ${actionRequired.value}
`
  const blob = new Blob([rpt], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `Soil_Health_Report_${ new Date().toISOString().split('T')[0] }.txt`
  a.click()
}

function selectAllSensors() {
  selectedSensors.value = [...sensorOptions]
}

function clearAllSensors() {
  selectedSensors.value = []
}
</script>