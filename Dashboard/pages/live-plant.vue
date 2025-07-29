<template>
  <div class="relative min-h-screen">
    <!-- Blurred plant background with black overlay -->
    <img src="public/home.jpg" alt="Plant background" class="fixed top-0 left-0 w-full h-full object-cover z-0 blur-md opacity-70 pointer-events-none select-none" />
    <div class="fixed top-0 left-0 w-full h-full bg-black/80 z-10 pointer-events-none" />
    <!-- Sidebar absolutely positioned, flush with all edges, above overlay -->
    <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30 border-r-2 border-orange-800 shadow-xl">
      <Sidebar />
    </div>
    <!-- Main content centered and padded -->
    <div class="min-h-screen relative z-20 flex flex-col px-6 md:px-12 py-8">
      
      <!-- 🔝 Header with Sticky Filter Bar -->
      <div class="sticky z-40 shadow-md border-b border-orange-700 pb-4 mb-8">
        <div class="flex items-baseline justify-between mb-4">
          <!-- LEFT: Title + Last refreshed -->
          <div class="flex items-baseline gap-6">
            <h1 class="text-3xl font-bold text-orange-400 font-roboto-slab">Soil Moisture Forecast</h1>
            <p class="text-sm text-orange-300 whitespace-nowrap">Last refreshed: {{ lastRefresh }}</p>
          </div>
          <!-- RIGHT: Time Range + Export -->
          <div class="flex flex-row gap-4 items-center">
            <div class="flex items-center gap-2">
              <label class="font-medium text-orange-300">Time Range:</label>
              <select v-model="selectedRange" class="border border-orange-500 rounded p-2 text-sm bg-zinc-900 text-orange-200">
                <option value="short">Short (1 Day)</option>
                <option value="medium">Medium (3 Days)</option>
                <option value="long">Long (7 Days)</option>
              </select>
            </div>
          </div>
          <!-- Export Dropdown -->
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

      <!-- 🔹 Combined Location and Device Filter -->
      <section class="pl-0 mb-10">
        <div class="flex items-center justify-between mb-2">
          <label class="font-medium text-orange-300">Filter by Location & Device</label>
          <div class="flex gap-2">
            <button 
              @click="selectAllDevices" 
              class="text-sm px-3 py-1 rounded border border-orange-500 text-orange-400 hover:bg-orange-500 hover:text-white transition-colors"
            >
              Select All
            </button>
            <button 
              @click="clearAllDevices" 
              class="text-sm px-3 py-1 rounded border border-orange-500 text-orange-400 hover:bg-orange-500 hover:text-white transition-colors"
            >
              Clear All
            </button>
          </div>
        </div>
        
        <!-- Combined Filter Dropdown -->
        <div class="relative w-full" ref="dropdownRef">
          <button 
            @click="toggleFilterDropdown" 
            class="w-full border border-orange-500 rounded p-3 bg-zinc-900 text-left text-orange-200 flex items-center justify-between hover:border-orange-400 transition-colors"
          >
            <div class="flex flex-col gap-1">
              <span class="text-orange-300 text-sm font-medium">
                {{ selectedDevices.length }} device{{ selectedDevices.length !== 1 ? 's' : '' }} selected
              </span>
              <span class="text-orange-100 text-xs truncate max-w-md" v-if="selectedDevices.length > 0">
                {{ getSelectedDevicesPreview() }}
              </span>
              <span class="text-orange-400 text-xs" v-else>
                Click to select locations and devices
              </span>
            </div>
            <svg 
              :class="{'rotate-180': isFilterDropdownOpen}" 
              class="w-5 h-5 ml-2 transition-transform text-orange-400" 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          
          <transition name="fade">
            <div v-if="isFilterDropdownOpen" class="absolute left-0 mt-2 w-full max-h-96 overflow-hidden bg-zinc-900 border border-orange-500 rounded-lg shadow-xl z-50">
              <!-- Search Bar -->
              <div class="p-3 border-b border-orange-700">
                <input 
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search locations or devices..."
                  class="w-full px-3 py-2 bg-zinc-800 border border-orange-600 rounded text-orange-100 placeholder-orange-400 focus:outline-none focus:border-orange-400 text-sm"
                />
              </div>
              
              <!-- Filter Options -->
              <div class="overflow-y-auto max-h-80">
                <div v-for="location in filteredLocations" :key="location" class="border-b border-orange-800/50 last:border-b-0">
                  <!-- Location Header -->
                  <div class="flex items-center gap-2 p-3 bg-zinc-800/50 hover:bg-zinc-800 transition-colors">
                    <button 
                      @click="toggleLocationExpansion(location)"
                      class="flex items-center gap-2 flex-1 text-left"
                    >
                      <div class="flex items-center gap-2">
                        <!-- Expandable Arrow -->
                        <svg 
                          :class="{'rotate-90': expandedLocations.includes(location)}" 
                          class="w-3 h-3 text-orange-400 transition-transform" 
                          fill="none" 
                          stroke="currentColor" 
                          stroke-width="2" 
                          viewBox="0 0 24 24"
                        >
                          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                        </svg>
                        <svg class="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                        </svg>
                        <span class="font-medium text-orange-300 text-sm">{{ location }}</span>
                      </div>
                    </button>
                    <div class="flex items-center gap-2">
                      <span class="text-xs text-orange-400">
                        {{ getSelectedDevicesInLocation(location) }}/{{ getDevicesInLocation(location).length }}
                      </span>
                      <button 
                        @click.stop="toggleAllDevicesInLocation(location)"
                        class="text-xs px-2 py-1 rounded border border-orange-600 text-orange-400 hover:bg-orange-600 hover:text-white transition-colors"
                      >
                        {{ areAllDevicesSelectedInLocation(location) ? 'Deselect' : 'Select' }} All
                      </button>
                    </div>
                  </div>
                  
                  <!-- Devices in Location (Collapsible) -->
                  <transition name="slide-down">
                    <div v-if="expandedLocations.includes(location)" class="pl-4 bg-zinc-900/50">
                      <div 
                        v-for="device in getFilteredDevicesInLocation(location)" 
                        :key="device"
                        class="flex items-center gap-2 p-2 hover:bg-zinc-800/30 transition-colors border-l-2 border-orange-700/30"
                      >
                        <label class="flex items-center gap-3 cursor-pointer flex-1">
                          <input 
                            type="checkbox" 
                            :value="device" 
                            :checked="selectedDevices.includes(device)" 
                            @change="toggleDevice(device)" 
                            class="accent-orange-500 w-4 h-4" 
                          />
                          <div class="flex items-center gap-2">
                            <svg class="w-3 h-3 text-orange-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                            </svg>
                            <span class="text-orange-100 text-sm">{{ device }}</span>
                          </div>
                          <!-- Device Status Indicator -->
                          <div class="ml-auto">
                            <span 
                              :class="{
                                'bg-red-500': getDeviceStatus(device) === 'Dry',
                                'bg-green-500': getDeviceStatus(device) === 'Healthy',
                                'bg-blue-500': getDeviceStatus(device) === 'Too Wet',
                                'bg-gray-500': getDeviceStatus(device) === 'Unknown'
                              }"
                              class="w-2 h-2 rounded-full inline-block"
                              :title="getDeviceStatus(device)"
                            ></span>
                          </div>
                        </label>
                      </div>
                      <!-- Show message if no devices match search in this location -->
                      <div v-if="getFilteredDevicesInLocation(location).length === 0 && searchQuery.trim()" 
                           class="p-2 text-xs text-orange-400 italic border-l-2 border-orange-700/30">
                        No devices match "{{ searchQuery }}" in this location
                      </div>
                    </div>
                  </transition>
                </div>
                
                <!-- No Results -->
                <div v-if="filteredLocations.length === 0" class="p-4 text-center text-orange-400">
                  No locations or devices found matching "{{ searchQuery }}"
                </div>
              </div>
              
              <!-- Footer Actions -->
              <div class="p-3 border-t border-orange-700 bg-zinc-800/50 flex justify-between items-center">
                <span class="text-xs text-orange-400">
                  {{ selectedDevices.length }} selected
                </span>
                <button 
                  @click="isFilterDropdownOpen = false" 
                  class="text-sm px-3 py-1 rounded bg-orange-600 text-white hover:bg-orange-700 transition-colors"
                >
                  Done
                </button>
              </div>
            </div>
          </transition>
        </div>
        
        <!-- Selected Devices Tags -->
        <div v-if="selectedDevices.length > 0" class="mt-3 flex flex-wrap gap-2">
          <div 
            v-for="device in selectedDevices.slice(0, 6)" 
            :key="device"
            class="flex items-center gap-1 px-2 py-1 bg-orange-600/20 border border-orange-600/50 rounded text-orange-200 text-xs"
          >
            <span>{{ device }}</span>
            <button 
              @click="removeDevice(device)"
              class="ml-1 text-orange-400 hover:text-orange-200 transition-colors"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div v-if="selectedDevices.length > 6" class="px-2 py-1 bg-orange-600/10 border border-orange-600/30 rounded text-orange-300 text-xs">
            +{{ selectedDevices.length - 6 }} more
          </div>
        </div>
      </section>

      <!-- 📊 Moisture Summary Cards -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold mb-4 text-orange-400">Moisture Summary</h2>
        <div v-if="selectedDevices.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          <MoistureCard
            v-for="device in selectedDevices"
            :key="device + '-latest'"
            :device="device"
            :title="`${device} Latest`"
            :value="latestMoisture[device] ?? 0"
            :change="round(latestMoisture[device] - forecastValues[device]?.[29])"
            :changeLabel="'vs forecast'"
            :status="statusTag(latestMoisture[device])"
            :isForecast="false"
            class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl orange-glow transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl"
          >
            <template #title>
              <span style="color: #f0d5af;">{{ device }} Latest</span>
            </template>
            <template #changeLabel>
              <span style="color: #f0d5af;">vs forecast</span>
            </template>
            <template #footer>
              <p class="mt-2 text-sm text-orange-200">
                {{ deviceRecommendations[device] }}
              </p>
            </template>
          </MoistureCard>
        </div>
        <div v-else class="w-full flex items-center justify-center h-32 text-orange-300 text-lg font-bold">
          Please select a device to get started.
        </div>
      </section>

      <!-- 📈 Historical Charts -->
      <section class="mb-12">
        <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Recent Soil Moisture Readings</h2>
        <template v-if="selectedDevices.length">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 justify-start items-start w-full">
            <div
              v-for="(device, idx) in selectedDevices"
              :key="device + '-chart'"
              class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl orange-glow flex flex-col gap-2 transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl p-6"
              style="will-change: transform;"
            >
              <!-- Download button above chart, right aligned -->
              <div class="flex justify-end mb-2">
                <button
                  @click="downloadChartImage(`historical-${device}`, `${device}-historical.png`)"
                  class="flex items-center gap-2 px-3 py-1 rounded bg-transparent border border-orange-500 text-orange-500 font-semibold hover:bg-orange-500 hover:text-white group cursor-pointer"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-400 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" />
                  </svg>
                  Download
                </button>
              </div>
              <div class="relative max-h-[420px] overflow-hidden">
                <Line :id="`historical-${device}`" :data="historicalChart(deviceData[device] ?? [], device, idx)" :options="getChartOptions()" class="h-72" />
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="flex items-center justify-center h-32 text-orange-300 text-lg font-bold">
            Please select a device to get started.
          </div>
        </template>
      </section>

      <!-- 📉 Forecast Chart -->
      <section class="w-full mb-8 flex flex-col items-start">
        <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Moisture Forecast (Next 30 Days)</h2>
        <template v-if="selectedDevices.length && forecastChart">
          <div
            class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl orange-glow w-full flex flex-col gap-2 max-w-full transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl pt-6 pr-6"
            style="will-change: transform;"
          >
            <div class="flex justify-end items-center w-full">
              <button @click="downloadChartImage('forecast-chart', 'forecast-30day.png')" class="flex items-center gap-2 px-3 py-1 rounded bg-transparent border border-orange-500 text-orange-500 font-semibold hover:bg-orange-500 hover:text-white group cursor-pointer">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-400 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" />
                </svg>
                Download
              </button>
            </div>
            <div class="max-h-[340px] overflow-hidden w-full">
              <Line id="forecast-chart" :data="forecastChart" :options="forecastOptions" class="h-64 w-full" />
            </div>
          </div>
        </template>
        <template v-else>
          <div class="w-full flex items-center justify-center h-32 text-orange-300 text-lg font-bold">
            Please select a device to get started.
          </div>
        </template>
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
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Transition } from 'vue'
import * as XLSX from 'xlsx-js-style'

import Sidebar from '../components/Sidebar/index.vue'
import { Button } from '@/components/ui/button'
import { onClickOutside } from '@vueuse/core'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

// On mount, record the page load time in "HH:mm DD/MM/YYYY" format
const lastRefresh = ref('')

onMounted(() => {
  // Format as "HH:mm DD/MM/YYYY"
  const now = new Date()
  const hours   = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const day     = String(now.getDate()).padStart(2, '0')
  const month   = String(now.getMonth() + 1).padStart(2, '0')
  const year    = now.getFullYear()
  lastRefresh.value = `${hours}:${minutes} ${day}/${month}/${year}`
})

// 1️⃣ state to hold the recommendation text
const recommendation = ref('')

// 1️⃣ Build a map: device → recommendation string
const deviceRecommendations = computed<Record<string,string>>(() => {
  return selectedDevices.value.reduce((map, device) => {
    const stat = statusTag(latestMoisture.value[device])  // "Dry"/"Healthy"/"Too Wet"
    if (stat === 'Dry') {
      map[device] = 'Soil is too dry. Consider watering soon.'
    } else if (stat === 'Too Wet') {
      map[device] = 'Soil is too wet. Allow it to dry out before your next watering.'
    } else {
      map[device] = 'Moisture is healthy. Keep your current schedule.'
    }
    return map
  }, {} as Record<string,string>)
})

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
/* ── Download Selected Data ───────────────── */
function downloadSelectedData(format: 'csv' | 'xlsx') {
  if (!rawData.value.length || !selectedDevices.value.length) return;

  const filtered = rawData.value.filter(d => selectedDevices.value.includes(d.devicename));
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
  const summary: any[] = selectedDevices.value.map(device => {
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
  for (const device of selectedDevices.value) {
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
  for (const device of selectedDevices.value) {
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
      pointRadius: 4,
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
        grid: {
          color: '#666666' // ← Y-axis grid line color
        },
        ticks: {
          stepSize: 0.5,
          color: '#ff8800',
          font: { size: 16, weight: 'bold' },
          callback: value => `${Number(value).toFixed(1)}%`
        },
        title: { display: true, text: 'Moisture (%)', color: '#ff8800', font: { size: 16, weight: 'bold' } }
      },
      x: {
        grid: {
          color: '#666666' // ← X-axis grid line color
        },
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

  const datasets = selectedDevices.value.map((device, idx) => ({
    label: `${device} Forecast`,
    data: forecastValues.value[device],
    borderColor: chartPalette[idx % chartPalette.length],
    backgroundColor: chartPalette[idx % chartPalette.length] + '33',
    fill: true,
    pointRadius: 4,
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
      grid: {
          color: '#666666' // ← Y-axis grid line color
        },
      ticks: {
        callback: v => `${v}%`,
        color: '#ff8800',
        font: { size: 16, weight: 'bold' }
      },
      title: {
        display: true,
        text: 'Moisture (%)',
        color: '#ff8800',
        font: { size: 16, weight: 'bold' }
      }
    },
    x: {
      grid: {
          color: '#666666' // ← Y-axis grid line color
        },
      ticks: {
        color: '#ff8800',
        font: { size: 14, weight: 'bold' }
      },
      title: {
        display: true,
        text: 'Day',
        color: '#ff8800',
        font: { size: 14, weight: 'bold' }
      }
    }
  }
}))

const moistureYAxisRange = computed(() => {
  const allValues: number[] = []

  for (const device of selectedDevices.value) {
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

/* ── Device/Location mapping from CSV ---*/
const deviceLocationMap = [
  { devicename: "NDS005", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS002 TEST 03", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NUS04", locationname: "NUS RVRC" },
  { devicename: "NP DS Rack 0", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS007", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NP DS Rack 1", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "TRF Plant Pot 01", locationname: "The Red Box Outer Setup" },
  { devicename: "NDS006", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "TRF Plant Environment 01", locationname: "The Red Box Outer Setup" },
  { devicename: "NDS011", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NP003", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "Centre 03 West Tank 0", locationname: "Centre 03 West" },
  { devicename: "NP008", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS002 TEST 02", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS004", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "TRF Plant Pot 03", locationname: "The Red Box Outer Setup" },
  { devicename: "NP006", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "Centre 03 West Tank 0", locationname: "Centre 03 West" },
  { devicename: "NDS015", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS002", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NP004", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NP001", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "TRF The Little Red Farm", locationname: "The Red Box Outer Setup" },
  { devicename: "NP005", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "Centre 03 West Solar Monitor", locationname: "Centre 03 West" },
  { devicename: "TEST", locationname: "TEST" },
  { devicename: "NDS002 TEST 01", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "RC4 01", locationname: "NUS RC4" },
  { devicename: "NUS05", locationname: "NUS SAVE" },
  { devicename: "NUS01", locationname: "NUS RC4" },
  { devicename: "TRF Plant Pot 02", locationname: "The Red Box Outer Setup" },
  { devicename: "NDS012", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NUS03", locationname: "NUS Pioneer House" },
  { devicename: "NUS02", locationname: "NUS SAVE" },
  { devicename: "NDS010", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS009", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "TRF Earthie Wormie", locationname: "The Red Box Outer Setup" },
  { devicename: "NP007", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "NDS016", locationname: "NUS RC4" },
  { devicename: "NDS008", locationname: "Ngee Ann Polytechnic DS Composting Room" },
  { devicename: "RC4 02", locationname: "NUS RC4" },
  { devicename: "RC4 Compost Tank Environment", locationname: "NUS RC4" },
  { devicename: "RC4 04", locationname: "NUS RC4" },
  { devicename: "RC4 03", locationname: "NUS RC4" },
  { devicename: "NP Solar Monitor", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 1 Plant Pot 0", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 4 Plant Pot 0", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 3 Plant Pot 1", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 4 Plant Pot 1", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 2 Plant Pot 1", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 2 Plant Pot 0", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 1 Plant Pot 1", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Group 3 Plant Pot 0", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NP Outdoor Plant Rack Env", locationname: "Ngee Ann Polytechnic Outdoor Plant Rack" },
  { devicename: "NVSS Demo Unit", locationname: "North Vista Secondary School" }
]

// Build location → devices map
const locationDeviceMap = computed(() => {
  const map: Record<string, string[]> = {}
  for (const entry of deviceLocationMap) {
    if (!map[entry.locationname]) map[entry.locationname] = []
    map[entry.locationname].push(entry.devicename)
  }
  return map
})

const locationList = computed(() => Object.keys(locationDeviceMap.value).sort())

// Combined filter state
const selectedDevices = ref<string[]>([])
const isFilterDropdownOpen = ref(false)
const searchQuery = ref('')
const expandedLocations = ref<string[]>([])

// Dropdown ref for outside click detection
const dropdownRef = ref<HTMLElement | null>(null)

// Close dropdown on outside click
onMounted(() => {
  if (dropdownRef.value) {
    onClickOutside(dropdownRef, () => (isFilterDropdownOpen.value = false))
  }
})

// Filter functions
function toggleFilterDropdown() {
  isFilterDropdownOpen.value = !isFilterDropdownOpen.value
}

// Filtered locations based on search
const filteredLocations = computed(() => {
  if (!searchQuery.value.trim()) {
    return locationList.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return locationList.value.filter(location => {
    // Check if location name matches
    if (location.toLowerCase().includes(query)) {
      return true
    }
    
    // Check if any device in this location matches
    const devicesInLocation = locationDeviceMap.value[location] || []
    return devicesInLocation.some(device => 
      device.toLowerCase().includes(query)
    )
  })
})

// Get devices for a specific location, filtered by search
function getFilteredDevicesInLocation(location: string): string[] {
  const devices = locationDeviceMap.value[location] || []
  if (!searchQuery.value.trim()) {
    return devices
  }
  
  const query = searchQuery.value.toLowerCase()
  return devices.filter(device => device.toLowerCase().includes(query))
}

// Get all devices in a location (unfiltered)
function getDevicesInLocation(location: string): string[] {
  return locationDeviceMap.value[location] || []
}

// Get count of selected devices in a location
function getSelectedDevicesInLocation(location: string): number {
  const devicesInLocation = getDevicesInLocation(location)
  return devicesInLocation.filter(device => selectedDevices.value.includes(device)).length
}

// Check if all devices in a location are selected
function areAllDevicesSelectedInLocation(location: string): boolean {
  const devicesInLocation = getDevicesInLocation(location)
  return devicesInLocation.length > 0 && 
         devicesInLocation.every(device => selectedDevices.value.includes(device))
}

// Toggle location expansion (show/hide devices)
function toggleLocationExpansion(location: string) {
  if (expandedLocations.value.includes(location)) {
    expandedLocations.value = expandedLocations.value.filter(loc => loc !== location)
  } else {
    expandedLocations.value = [...expandedLocations.value, location]
  }
}

// Toggle all devices in a location
function toggleAllDevicesInLocation(location: string) {
  const devicesInLocation = getDevicesInLocation(location)
  const allSelected = areAllDevicesSelectedInLocation(location)
  
  if (allSelected) {
    // Remove all devices from this location
    selectedDevices.value = selectedDevices.value.filter(device => 
      !devicesInLocation.includes(device)
    )
  } else {
    // Add all devices from this location
    const newDevices = devicesInLocation.filter(device => 
      !selectedDevices.value.includes(device)
    )
    selectedDevices.value = [...selectedDevices.value, ...newDevices]
  }
}

// Toggle individual device
function toggleDevice(device: string) {
  if (selectedDevices.value.includes(device)) {
    selectedDevices.value = selectedDevices.value.filter(d => d !== device)
  } else {
    selectedDevices.value = [...selectedDevices.value, device]
  }
}

// Remove individual device
function removeDevice(device: string) {
  selectedDevices.value = selectedDevices.value.filter(d => d !== device)
}

// Select all devices
function selectAllDevices() {
  const allDevices = Object.values(locationDeviceMap.value).flat()
  selectedDevices.value = [...allDevices]
}

// Clear all devices
function clearAllDevices() {
  selectedDevices.value = []
  expandedLocations.value = [] // Also collapse all locations when clearing
}

// Get preview text for selected devices
function getSelectedDevicesPreview(): string {
  if (selectedDevices.value.length === 0) return ''
  if (selectedDevices.value.length <= 2) {
    return selectedDevices.value.join(', ')
  }
  return `${selectedDevices.value.slice(0, 2).join(', ')} and ${selectedDevices.value.length - 2} more`
}

// Get device status for status indicator
function getDeviceStatus(device: string): string {
  const moisture = latestMoisture.value[device]
  if (moisture === undefined || moisture === 0) return 'Unknown'
  return statusTag(moisture)
}

watchEffect(() => {
  // Set loading to false when all main data is loaded
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
.hover\:glow-orange:hover {
  box-shadow: 0 0 24px 0 rgba(255, 136, 0, 0.18), 0 0 2px 0 rgba(255, 136, 0, 0.12);
}

/* Slide down animation for device lists */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: top;
}

.slide-down-enter-from {
  opacity: 0;
  transform: scaleY(0);
  max-height: 0;
}

.slide-down-leave-to {
  opacity: 0;
  transform: scaleY(0);
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: scaleY(1);
  max-height: 500px;
}
</style>