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
  
      <!-- Sidebar (fixed) -->
      <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30 border-r-2 border-orange-800 shadow-xl">
        <Sidebar />
      </div>
  
      <!-- Main dashboard content -->
      <div class="min-h-screen relative z-20 px-6 md:px-12 py-8" style="margin-left: 16rem;">
        <div class="w-full max-w-5xl mx-auto">
          <!-- Header -->
          <div class="flex items-center gap-6 mb-2">
            <h1 class="text-3xl font-bold text-orange-400 font-roboto-slab">Sensor Data Viewer</h1>
            <div class="ml-auto">
              <Menu as="div" class="relative inline-block text-left">
                <div>
                  <MenuButton>
                    <button class="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-4 rounded transition-colors export-data-btn">
                      Export Data ▼
                    </button>
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
                  <MenuItems class="origin-top-right absolute right-0 mt-2 w-64 rounded-md shadow-lg bg-zinc-900 ring-1 ring-orange-700 ring-opacity-70 focus:outline-none z-50">
                    <div class="py-1">
                      <MenuItem>
                        <div class="px-4 py-2 text-sm text-orange-200 font-semibold">Full Report</div>
                      </MenuItem>
                      <MenuItem as="button"
                        @click="exportSelected('csv')"
                        class="w-full px-4 py-2 text-sm text-orange-100 hover:bg-orange-800 export-summary-btn"
                      >
                        Download All Charts + Summary (CSV)
                      </MenuItem>
                      <MenuItem as="button"
                        @click="exportSelected('xlsx')"
                        class="w-full px-4 py-2 text-sm text-orange-100 hover:bg-orange-800 export-summary-btn"
                      >
                        Download All Charts + Summary (Excel)
                      </MenuItem>
                    </div>
                  </MenuItems>
                </Transition>
              </Menu>
            </div>
          </div>
          
          <!-- Divider line below header -->
          <hr class="border-t border-orange-700 mb-6" />
  
          <!-- Filter Devices -->
          <div class="mb-6 flex items-center gap-4 w-full">
            <label for="device-filter" class="text-orange-300 font-medium">Filter Devices:</label>
            <select
              id="device-filter"
              v-model="selectedDevice"
              class="bg-zinc-800 border border-orange-300/20 rounded px-3 py-2 text-orange-400"
            >
              <option value="">All Devices</option>
              <option v-for="device in deviceList" :key="device" :value="device">{{ device }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
  import { ref, Transition, onMounted, watch, defineComponent } from 'vue'
  import Sidebar from '../components/Sidebar/index.vue'
//   TODO: Add Papa.js for CSV export
//   import Papa from 'papaparse'
  import { Line } from 'vue-chartjs'
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    PointElement,
    CategoryScale,
    LinearScale
  } from 'chart.js'
  
  ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)
  
  // Chart wrapper component - simplified to avoid crashes
  const LineChart = {
    props: ['chartData', 'chartOptions'],
    components: { Line },
    template: `<div class="chart-container" style="position: relative; height: 400px; width: 100%;"><Line :data="chartData" :options="chartOptions" /></div>`
  }
  
  // Placeholder device list - will be populated from actual data
  const deviceList = ref<string[]>([])
  const selectedDevice = ref('')
  
  // Export dropdown logic
  function exportSelected(type: string) {
    alert(`Exporting as ${type.toUpperCase()} (feature coming soon!)`)
  }
  
  
  
  </script>
  
  <style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Slab:wght@700&display=swap');
  </style>