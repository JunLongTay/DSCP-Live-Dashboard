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

      <!-- 🔹 Combined Location and Device Filter -->
      <section class="w-full mb-8">
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

      <!-- 🔹 Average NPK Levels -->
      <h2 class="text-xl font-semibold mt-6 mb-4 text-orange-400">Average NPK Levels</h2>
      <div v-if="selected.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <!-- NPK Cards -->
        <div
          v-for="card in avgPerDevice"
          :key="card.devicename"
          class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6
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
                  'bg-green-500': npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) /1000)==='Optimal',
                  'bg-yellow-500': npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) /1000)==='Low',
                  'bg-blue-500': npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) /1000)==='Harvest Immediately'
                }"
                :style="{
                  height: '40px',
                  transition: 'height 0.8s cubic-bezier(0.4,0,0.2,1)',
                  boxShadow:
                    npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) / 1000)==='Optimal'
                      ? '0 0 8px 2px #22c55e'
                      : npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) / 1000)==='Low'
                        ? '0 0 8px 2px #facc15'
                        : npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) / 1000)==='Harvest Immediately'
                          ? '0 0 8px 2px #3b82f6'
                          : ''
                }"
              ></div>
              <span class="mt-1 text-xs text-zinc-400 font-semibold text-center">
                {{ npkStatus(nutrient as NPKKey, Number(card[nutrient as keyof typeof card]) / 1000) }}
              </span>
            </div>
            <!-- Value & label -->
            <div class="flex-1 flex flex-col min-w-0">
              <span class="text-sm font-medium text-orange-300 capitalize mb-1" style="opacity:0.8;">
                {{ nutrient }}
              </span>
              <span class="text-3xl font-bold text-orange-400 leading-tight">
                <template v-if="['nitrogen', 'phosphorus', 'potassium'].includes(nutrient)">
                  {{ (Number(card[nutrient as keyof typeof card]) / 1000).toFixed(3) }} g/kg soil
                </template>
                <template v-else>
                  {{ card[nutrient as keyof typeof card] }} {{ NPK_UNIT }}
                </template>
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
          class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6
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
          <!-- Chart Container with Info Overlay -->
          <div class="relative" style="height: 350px;">
            <LineChart
              :chart-data="soilChartDataSingleDeviceWithToggle(device, 'Soil Temp (°C)')"
              :chart-options="soilOptions"
              class="w-full h-full"
              :ref="el => setSoilTempChartRef(el, idx)"
              :id="`soil-temp-chart-${idx}`"
            />
            
            <!-- Enhanced Stats Container with Sparkline and Trend Analysis -->
            <div class="absolute top-13 right-2 bg-zinc-900/95 border border-orange-500/50 rounded-lg backdrop-blur-sm z-10 min-w-[200px]"
                @mouseenter="handleInfoHover(device, true)"
                @mouseleave="handleInfoHover(device, false)">
              
              <!-- Alert indicator -->
              <div v-if="getChartStats(device)?.alertLevel !== 'none'" 
                  class="absolute -top-2 -right-2 w-4 h-4 rounded-full animate-pulse"
                  :class="{
                    'bg-yellow-500': getChartStats(device)?.alertLevel === 'warning',
                    'bg-red-500': getChartStats(device)?.alertLevel === 'critical'
                  }">
              </div>
              
              <!-- Collapsible Header -->
              <button 
                @click="toggleStatsExpansion(device)"
                class="w-full flex items-center justify-between px-3 py-2 text-xs text-orange-300 font-medium hover:text-orange-200 transition-colors"
              >
                <div class="flex items-center gap-2">
                  <span>Stats</span>
                  <!-- Status indicator -->
                  <div class="flex items-center gap-1">
                    <div class="w-2 h-2 rounded-full"
                        :class="{
                          'bg-green-400': getChartStats(device)?.alertLevel === 'none',
                          'bg-yellow-400': getChartStats(device)?.alertLevel === 'warning', 
                          'bg-red-400': getChartStats(device)?.alertLevel === 'critical'
                        }">
                    </div>
                    <span class="text-xs"
                          :class="{
                            'text-green-400': getChartStats(device)?.alertLevel === 'none',
                            'text-yellow-400': getChartStats(device)?.alertLevel === 'warning',
                            'text-red-400': getChartStats(device)?.alertLevel === 'critical'
                          }">
                      {{ getChartStats(device)?.trendStatus }}
                    </span>
                  </div>
                </div>
                <svg 
                  :class="{'rotate-180': isStatsExpanded(device)}" 
                  class="w-3 h-3 transition-transform" 
                  fill="none" 
                  stroke="currentColor" 
                  stroke-width="2" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              
              <!-- Collapsible Content -->
              <transition name="slide-down">
                <div v-if="isStatsExpanded(device)" class="px-3 pb-3">
                  <div v-if="getChartStats(device)" class="space-y-2">
                    
                    <!-- Trend Indicator (replaces sparkline) -->
                    <div class="bg-zinc-800/50 rounded p-2 mb-2">
                      <div class="text-xs text-orange-300 mb-1">12-Hour Trend</div>
                      <div class="h-8 flex items-center justify-center">
                        <div v-if="getChartStats(device)?.trendStatus === 'Stable'" 
                             class="flex items-center gap-2 text-gray-400">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14"/>
                          </svg>
                          <span class="text-sm font-medium">Stable</span>
                        </div>
                        
                        <div v-else-if="getChartStats(device)?.trendStatus?.includes('Warming')" 
                             class="flex items-center gap-2 text-red-400">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17l9.2-9.2M17 17V7H7"/>
                          </svg>
                          <span class="text-sm font-medium">Rising</span>
                        </div>
                        
                        <div v-else-if="getChartStats(device)?.trendStatus?.includes('Cooling')" 
                             class="flex items-center gap-2 text-blue-400">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 7l-9.2 9.2M7 7v10h10"/>
                          </svg>
                          <span class="text-sm font-medium">Falling</span>
                        </div>
                        
                        <div v-else class="flex items-center gap-2 text-gray-400">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                          </svg>
                          <span class="text-sm font-medium">Unknown</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Current Stats -->
                    <div class="text-xs text-orange-200 space-y-1">
                      <div class="flex justify-between">
                        <span>Current:</span>
                        <span class="font-medium">{{ getChartStats(device)?.current }}°C</span>
                      </div>
                      <div class="flex justify-between">
                        <span>Average:</span>
                        <span class="font-medium">{{ getChartStats(device)?.average }}°C</span>
                      </div>
                      <div class="flex justify-between">
                        <span>Range:</span>
                        <span class="font-medium">{{ getChartStats(device)?.min }}-{{ getChartStats(device)?.max }}°C</span>
                      </div>
                    </div>
                    
                    <!-- Trend Analysis -->
                    <div class="border-t border-orange-700/50 pt-2">
                      <div class="text-xs text-orange-300 mb-1">Trend Analysis</div>
                      <div class="flex justify-between text-xs text-orange-200">
                        <span>Rate:</span>
                        <span class="font-medium"
                              :class="{
                                'text-blue-400': getChartStats(device)?.trendStatus === 'Cooling',
                                'text-red-400': getChartStats(device)?.trendStatus === 'Warming',
                                'text-gray-400': getChartStats(device)?.trendStatus === 'Stable'
                              }">
                          {{ getChartStats(device)?.trend }}°C/hr
                        </span>
                      </div>
                      <div class="flex justify-between text-xs text-orange-200">
                        <span>Status:</span>
                        <span class="font-medium"
                              :class="{
                                'text-blue-400': getChartStats(device)?.trendStatus === 'Cooling',
                                'text-red-400': getChartStats(device)?.trendStatus === 'Warming',
                                'text-gray-400': getChartStats(device)?.trendStatus === 'Stable'
                              }">
                          {{ getChartStats(device)?.trendStatus }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- Status Badge -->
                    <div class="text-center mt-2 px-2 py-1 rounded text-xs border-t border-orange-700/50 pt-2">
                      <div class="font-medium"
                          :class="{
                            'text-green-400': getChartStats(device)?.alertLevel === 'none',
                            'text-yellow-400': getChartStats(device)?.alertLevel === 'warning',
                            'text-red-400': getChartStats(device)?.alertLevel === 'critical'
                          }">
                        {{ getChartStats(device)?.status }}
                      </div>
                      <div class="text-orange-400 text-xs mt-1">
                        Optimal: 25-32°C
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-xs text-orange-400">
                    No data available
                  </div>
                </div>
              </transition>
            </div>
          </div>
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
        class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6 mb-12 transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl flex flex-col orange-glow"
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
        <!-- Chart Container with Info Overlay -->
        <div class="relative" style="height: 350px;">
          <LineChart
            :chart-data="co2Data"
            :chart-options="co2Options"
            ref="co2Chart"
            id="co2-chart"
            class="w-full h-full"
          />
          
          <!-- CO₂ Info Container Overlay (Simplified - No Critical High) -->
          <div class="absolute top-12 right-2 bg-zinc-900/95 border border-orange-500/50 rounded-lg backdrop-blur-sm z-10 min-w-[200px]"
              @mouseenter="handleCo2InfoHover(true)"
              @mouseleave="handleCo2InfoHover(false)">
            
            <!-- Collapsible Header (removed alert indicator) -->
            <button 
              @click="toggleCo2StatsExpansion()"
              class="w-full flex items-center justify-between px-3 py-2 text-xs text-orange-300 font-medium hover:text-orange-200 transition-colors"
            >
              <div class="flex items-center gap-2">
                <span>CO₂ Stats</span>
                <!-- Status indicator (simplified - no critical alerts) -->
                <div class="flex items-center gap-1">
                  <div class="w-2 h-2 rounded-full bg-green-400">
                  </div>
                </div>
              </div>
              <svg 
                :class="{'rotate-180': isCo2StatsExpanded}" 
                class="w-3 h-3 transition-transform" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="2" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>
            
            <!-- Collapsible Content -->
            <transition name="slide-down">
              <div v-if="isCo2StatsExpanded" class="px-3 pb-3">
                <div v-if="getCo2EnhancedStats()" class="space-y-2">
                  
                  <!-- Current Stats Only -->
                  <div class="text-xs text-orange-200 space-y-1">
                    <div class="flex justify-between">
                      <span>Devices:</span>
                      <span class="font-medium">{{ getCo2EnhancedStats()?.deviceCount }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span>Current:</span>
                      <span class="font-medium">{{ getCo2EnhancedStats()?.current }} ppm</span>
                    </div>
                    <div class="flex justify-between">
                      <span>Average:</span>
                      <span class="font-medium">{{ getCo2EnhancedStats()?.average }} ppm</span>
                    </div>
                    <div class="flex justify-between">
                      <span>Range:</span>
                      <span class="font-medium">{{ getCo2EnhancedStats()?.min }}-{{ getCo2EnhancedStats()?.max }} ppm</span>
                    </div>
                  </div>
                  
                  <!-- Status Badge (simplified) -->
                  <div class="text-center mt-2 px-2 py-1 rounded text-xs border-t border-orange-700/50 pt-2">
                    <div class="font-medium text-green-400">
                      Normal Operation
                    </div>
                    <div class="text-orange-400 text-xs mt-1">
                      System Running
                    </div>
                  </div>
                </div>
                <div v-else class="text-xs text-orange-400">
                  No CO₂ data available
                </div>
              </div>
            </transition>
          </div>
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-32 text-orange-300 text-lg font-bold">
        Please select a device to get started.
      </div>
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
import { ref, computed, watchEffect, onMounted, nextTick, reactive, onUnmounted } from 'vue'
import type { ChartData, ChartOptions } from 'chart.js'
import 'chartjs-adapter-date-fns'
import { Transition } from 'vue'
import { Button } from '@/components/ui/button'
import { onClickOutside } from '@vueuse/core'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import annotationPlugin from 'chartjs-plugin-annotation'

// Register the annotation plugin
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  annotationPlugin
)

// On mount, record the page load time in “HH:mm DD/MM/YYYY” format
const lastRefresh = computed(() => {
  // Access refreshTrigger to make this reactive to manual updates
  refreshTrigger.value
  
  const stored = sessionStorage.getItem('last-data-refresh')
  if (stored) {
    const date = new Date(stored)
    const hours   = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const day     = String(date.getDate()).padStart(2, '0')
    const month   = String(date.getMonth() + 1).padStart(2, '0')
    const year    = date.getFullYear()
    return `${hours}:${minutes} ${day}/${month}/${year}`
  }
  
  // Fallback to current time if no stored value
  const now = new Date()
  const hours   = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const day     = String(now.getDate()).padStart(2, '0')
  const month   = String(now.getMonth() + 1).padStart(2, '0')
  const year    = now.getFullYear()
  return `${hours}:${minutes} ${day}/${month}/${year}`
})

const refreshTrigger = ref(0)

let handleStorageChange: (e: StorageEvent) => void
let handleRefreshEvent: () => void

// Define the handler functions
handleStorageChange = (e: StorageEvent) => {
  if (e.key === 'last-data-refresh') {
    refreshTrigger.value++ // Force reactivity
  }
}

handleRefreshEvent = () => {
  refreshTrigger.value++ // Force reactivity
}

const backendAvailable = ref(true);

onMounted(async () => {
  try {
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices');
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices');
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices');
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices');
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices');
    backendAvailable.value = true;
  } catch (e) {
    backendAvailable.value = false;
  }
  window.addEventListener('storage', (e) => {
    if (e.key === 'last-data-refresh') {
      refreshTrigger.value++ // Force reactivity
    }
  })
  
  // Also listen for custom events from the sidebar
  window.addEventListener('refresh-dashboard-data', () => {
    refreshTrigger.value++ // Force reactivity
  })
});

/* ── Types ───────────────────────── */
interface NPKReading { timestamp: string; nitrogen: number | null; phosphorus: number | null; potassium: number | null; devicename: string }
interface SoilReading { timestamp: string; soil_temp: number | null; devicename: string }
interface CO2Reading   { timestamp: string; co2: number | null; devicename: string;  }

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
  { devicename: "NP002", locationname: "Ngee Ann Polytechnic DS Composting Room" },
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

/* ── State ───────────────────────── */
const SELECTED_DEVICES_KEY = 'dashboard_overview_selected_devices' // Changed from 'dashboard_selected_devices'
// Replace simple selected array with selectedDevices
const selectedDevices = ref<string[]>([])
// Update selected to use selectedDevices for backward compatibility
const selected = computed({
  get: () => selectedDevices.value,
  set: (val) => { selectedDevices.value = val }
})

onMounted(async () => {
  // Load saved devices from sessionStorage FIRST
  const savedDevices = sessionStorage.getItem(SELECTED_DEVICES_KEY)
  if (savedDevices) {
    try {
      const parsed = JSON.parse(savedDevices)
      if (Array.isArray(parsed)) {
        selectedDevices.value = parsed
      }
    } catch (e) {
      console.warn('Failed to parse saved devices:', e)
    }
  }

  // Then fetch device names from backend
  try {
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices')
    backendAvailable.value = true
  } catch (e) {
    backendAvailable.value = false
  }

  // Initialize sessionStorage for last refresh if not set
  if (!sessionStorage.getItem('last-data-refresh')) {
    sessionStorage.setItem('last-data-refresh', new Date().toISOString())
  }

  // Setup outside click detection for dropdown
  if (dropdownRef.value) {
    onClickOutside(dropdownRef, () => (isFilterDropdownOpen.value = false))
  }
})

// Watch for device selection changes and save to sessionStorage
watch(selectedDevices, (newDevices) => {
  sessionStorage.setItem(SELECTED_DEVICES_KEY, JSON.stringify(newDevices)) // ✅ Writing to sessionStorage
}, { deep: true })

// Add after your existing reactive state (around line 180)
const expandedStats = reactive<Record<string, boolean>>({})

// Add hover handler for intelligent tooltip positioning
const hoverTimeouts = ref<Record<string, NodeJS.Timeout>>({})

function handleInfoHover(device: string, isEntering: boolean) {
  if (isEntering) {
    // Clear any existing timeout
    if (hoverTimeouts.value[device]) {
      clearTimeout(hoverTimeouts.value[device])
    }
    // Update sparkline when hovering
    // (No sparkline function for soil temp; nothing to do here)
  } else {
    // Set a small delay before hiding detailed info
    hoverTimeouts.value[device] = setTimeout(() => {
      // Could add logic here to temporarily hide non-essential info
    }, 500)
  }
}

// Initialize stats expansion state for each device
function initializeStatsExpansion() {
  selectedDevices.value.forEach(device => {
    if (!(device in expandedStats)) {
      expandedStats[device] = false // Start collapsed
    }
  })
}

// Toggle stats expansion for a device
function toggleStatsExpansion(device: string) {
  expandedStats[device] = !expandedStats[device]
}

// Check if stats are expanded for a device
function isStatsExpanded(device: string): boolean {
  return expandedStats[device] || false
}

// Watch for device changes and initialize stats
watch(selectedDevices, () => {
  initializeStatsExpansion()
}, { immediate: true })

// CO₂ sparkline functionality
const co2SparklineRef = ref<HTMLCanvasElement | null>(null)
const co2SparklineChart = ref<any>(null)

function setCo2SparklineRef(el: HTMLCanvasElement | null) {
  if (el) {
    co2SparklineRef.value = el
    nextTick(() => createCo2Sparkline())
  }
}

function createCo2Sparkline() {
  const canvas = co2SparklineRef.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // Destroy existing chart if it exists
  if (co2SparklineChart.value) {
    co2SparklineChart.value.destroy()
  }
  
  const stats = getCo2EnhancedStats.value()
  if (!stats?.sparklineData) return
  
  co2SparklineChart.value = new ChartJS(ctx, {
    type: 'line',
    data: {
      labels: stats.sparklineData.map((_, i) => i),
      datasets: [{
        data: stats.sparklineData,
        borderColor: '#fb923c',
        backgroundColor: 'rgba(251, 146, 60, 0.1)',
        borderWidth: 1,
        pointRadius: 0,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { display: false },
        y: { 
          display: false,
          min: 200,
          max: 1500
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      },
      elements: {
        point: { radius: 0 }
      }
    }
  })
}

// CO₂ hover handler
function handleCo2InfoHover(isEntering: boolean) {
  if (isEntering) {
    nextTick(() => createCo2Sparkline())
  }
}

// Combined filter state
const isFilterDropdownOpen = ref(false)
const searchQuery = ref('')
const expandedLocations = ref<string[]>([])

// Dropdown ref for outside click detection
const dropdownRef = ref<HTMLElement | null>(null)

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
  nitrogen:   { low: 0.3, high: 0.7 },
  phosphorus: { low: 0.2, high: 0.5 },
  potassium:  { low: 0.3, high: 0.8 }
}
function npkStatus(key: NPKKey, val: number) {
  const { low, high } = NPK_THRESHOLDS[key]
  if (isNaN(val)) return '—'
  if (val < low) return 'Low'
  if (val > high) return 'Harvest Immediately'
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
    const avgField = (f: keyof NPKReading) => {
      const avg = data.reduce((sum, d) => sum + (Number(d[f]) || 0), 0) / data.length
      return Number(avg.toFixed(3))
    }
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
      nitrogen: NaN, phosphorus: NaN, potassium: NaN
    }
    const avgField = (f: keyof NPKReading) => {
      const avg = data.reduce((sum, d) => sum + (Number(d[f]) || 0), 0) / data.length
      return Number(avg.toFixed(3))
    }
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
    const nStatus = npkStatus('nitrogen',   Number(card.nitrogen) /1000)
    const pStatus = npkStatus('phosphorus', Number(card.phosphorus) /1000)
    const kStatus = npkStatus('potassium',  Number(card.potassium) /1000)

    // Nitrogen
    // Nitrogen
    if (nStatus === 'Low') {
      notes.push('🟡 Low N: Add more green compost materials (vegetable scraps, coffee grounds, fresh grass clippings).')
    } else if (nStatus === 'Harvest Immediately') {
      notes.push('🔵 High N: Avoid adding too much green material (like fresh grass or food scraps) to maintain balanced nitrogen levels, Harvest compost now.')
    } else if (nStatus === 'Optimal') {
      notes.push('🟢 Optimal N: Nitrogen levels are ideal for composting.')
    }

    // Phosphorus
    if (pStatus === 'Low') {
      notes.push('🟡 Low P: Toss in bone meal or crushed eggshells to boost phosphorus levels.')
    } else if (pStatus === 'Harvest Immediately') {
      notes.push('🔵 High P: Be cautious with bone meal, manure, and other high-phosphorus materials, use sparingly and balance with carbon-rich materials (leaves, straw) to prevent excess phosphorus, Harvest compost now.')
    } else if (pStatus === 'Optimal') {
      notes.push('🟢 Optimal P: Phosphorus levels are ideal for composting.')
    }

    // Potassium
    if (kStatus === 'Low') {
      notes.push('🟡 Low K: Add wood ash or banana peels for a potassium boost.')
    } else if (kStatus === 'Harvest Immediately') {
      notes.push('🔵 High K: Avoid adding wood ash or high-potassium fertilizers in large quantities, mix with carbon-rich materials to avoid excessive potassium levels that could disrupt plant nutrient uptake, Harvest compost now.')
    } else if (kStatus === 'Optimal') {
      notes.push('🟢 Optimal K: Potassium levels are ideal for composting.')
    }

    // If all are optimal, recommend harvest
    if ([nStatus, pStatus, kStatus].every(s => s === 'Optimal')) {
      notes.push('✅ All nutrients are optimal, Harvest compost now for best results.')
    }

    recs[name] = notes.length
      ? notes.join(' ')
      : '✅ All nutrients are optimal, Harvest compost now for best results.'
  })

  return recs
})

// Enhanced chart stats with trend analysis
const getChartStats = computed(() => {
  return (device: string) => {
    const deviceData = soilRaw.value.filter(r => r.devicename === device)
    if (!deviceData.length) return null
    
    const temps = deviceData.map(d => d.soil_temp).filter(t => t != null) as number[]
    if (!temps.length) return null
    
    const current = temps[temps.length - 1]
    const avg = temps.reduce((a, b) => a + b, 0) / temps.length
    const min = Math.min(...temps)
    const max = Math.max(...temps)
    
    // Enhanced trend detection
    const trendData = temps.slice(-5)
    let trend = 0
    let trendStatus = 'Stable'
    
    if (trendData.length >= 3) {
      const firstTemp = trendData[0]
      const lastTemp = trendData[trendData.length - 1]
      const timeSpanHours = trendData.length - 1
      
      if (timeSpanHours > 0) {
        trend = (lastTemp - firstTemp) / timeSpanHours
        const absTrend = Math.abs(trend)
        
        if (absTrend < 0.05) {
          trendStatus = 'Stable'
        } else if (trend > 0.15) {
          trendStatus = 'Warming (trending)'
        } else if (trend > 0.05) {
          trendStatus = 'Warming (drifting)'
        } else if (trend < -0.15) {
          trendStatus = 'Cooling (trending)'
        } else if (trend < -0.05) {
          trendStatus = 'Cooling (drifting)'
        }
      }
    }
    
    // Status based on optimal range
    let status = 'Optimal'
    let alertLevel = 'none'
    
    if (current < 23) {
      status = 'Critical Low'
      alertLevel = 'critical'
    } else if (current < 25) {
      status = 'Low'
      alertLevel = 'warning'
    } else if (current > 34) {
      status = 'Critical High'
      alertLevel = 'critical'
    } else if (current > 32) {
      status = 'High'
      alertLevel = 'warning'
    }
    
    return {
      current: current?.toFixed(1),
      average: avg.toFixed(1),
      min: min.toFixed(1),
      max: max.toFixed(1),
      status,
      alertLevel,
      trend: trend.toFixed(2),
      trendStatus,
      trendRate: `${trend > 0 ? '+' : ''}${trend.toFixed(1)}`, // Formatted rate
    }
  }
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
    dt.setHours(dt.getHours() + 8)
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
        pointRadius: 4, // Increased marker size
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
    const dt = new Date(ts)// Adjust for timezone
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
      pointRadius: 4,
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
  layout: {
    padding: {
      top: 10,
      right: 10,
      bottom: 40,
      left: 10
    }
  },
  scales: {
    x: {
      type: 'category',
      title: {
        display: true,
        text: 'Time',
        color: '#fb923c'
      },
      ticks: {
        maxRotation: 0,
        autoSkip: true,
        maxTicksLimit: 12,
        color: '#fb923c'
      },
      grid: {
        color: '#fb923c33'
      }
    },
    y: {
      title: {
        display: true,
        text: 'Temperature (°C)',
        color: '#fb923c'
      },
      ticks: {
        color: '#fb923c'
      },
      grid: {
        color: '#fb923c33'
      },
      min: 20,
      max: 40
    }
  },
  plugins: {
    decimation: { enabled: true, algorithm: 'lttb', samples: 60 },
    tooltip: {
      enabled: false, // Disable default tooltip for non-blocking experience
    },
    legend: {
      display: true,
      position: 'top',
      labels: {
        color: '#fb923c',
        usePointStyle: true,
        padding: 15
      }
    },
    // Add annotation plugin for optimal band
    annotation: {
      annotations: {
        optimalBand: {
          type: 'box',
          yMin: 25,
          yMax: 32,
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderColor: 'rgba(34, 197, 94, 0.3)',
          borderWidth: 1,
          label: {
            display: true,
            content: 'Optimal Range (25-32°C)',
            position: 'start',
            color: '#22c55e',
            padding: 4,
            font: {
              size: 10
            }
          }
        },
        warningLowLine: {
          type: 'line',
          yMin: 23,
          yMax: 23,
          borderColor: 'rgba(251, 191, 36, 0.8)',
          borderWidth: 2,
          borderDash: [5, 5],
          label: {
            display: true,
            content: 'Critical Low (23°C)',
            position: 'end',
            color: '#fbbf24',
            backgroundColor: 'rgba(251, 191, 36, 0.8)',
            padding: 2,
            font: {
              size: 9
            }
          }
        },
        warningHighLine: {
          type: 'line',
          yMin: 34,
          yMax: 34,
          borderColor: 'rgba(239, 68, 68, 0.8)',
          borderWidth: 2,
          borderDash: [5, 5],
          label: {
            display: true,
            content: 'Critical High (34°C)',
            position: 'end',
            color: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.8)',
            padding: 2,
            font: {
              size: 9
            }
          }
        }
      }
    }
  },
  interaction: {
    intersect: false,
    mode: 'index'
  }
}

// Computed to get current CO₂ chart stats for each device
const getCo2ChartStats = computed(() => {
  return (device: string) => {
    const deviceData = co2Raw.value.filter(r => r.devicename === device)
    if (!deviceData.length) return null
    
    const co2Values = deviceData.map(d => d.co2).filter(c => c != null) as number[]
    if (!co2Values.length) return null
    
    const current = co2Values[co2Values.length - 1]
    const avg = co2Values.reduce((a, b) => a + b, 0) / co2Values.length
    const min = Math.min(...co2Values)
    const max = Math.max(...co2Values)
    
    return {
      current: current?.toFixed(0),
      average: avg.toFixed(0),
      min: min.toFixed(0),
      max: max.toFixed(0),
      status: current < 400 ? 'Low' : current > 1000 ? 'High' : 'Normal'
    }
  }
})

// Enhanced CO₂ stats with trend analysis
const getCo2EnhancedStats = computed(() => {
  return () => {
    const allDevices = co2ChartDevices.value
    if (!allDevices.length) return null
    
    const allCo2Values: number[] = []
    const allCo2Data: { value: number; timestamp: string }[] = []
    
    allDevices.forEach(device => {
      const deviceData = co2Raw.value.filter(r => r.devicename === device)
      deviceData.forEach(d => {
        if (d.co2 != null) {
          allCo2Values.push(d.co2)
          allCo2Data.push({ value: d.co2, timestamp: d.timestamp })
        }
      })
    })
    
    if (!allCo2Values.length) return null
    
    // Sort by timestamp for trend calculation
    allCo2Data.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    
    const current = allCo2Data[allCo2Data.length - 1]?.value || 0
    const avg = allCo2Values.reduce((a, b) => a + b, 0) / allCo2Values.length
    const min = Math.min(...allCo2Values)
    const max = Math.max(...allCo2Values)
    
    // Calculate trend (last 5 points)
    const trendData = allCo2Data.slice(-5).map(d => d.value)
    let trend = 0
    let trendStatus = 'Stable'
    
    if (trendData.length >= 3) {
      const firstValue = trendData[0]
      const lastValue = trendData[trendData.length - 1]
      const timeSpanHours = trendData.length - 1
      
      if (timeSpanHours > 0) {
        trend = (lastValue - firstValue) / timeSpanHours // ppm per hour
        
        if (Math.abs(trend) < 10) trendStatus = 'Stable'  // Less than 10 ppm/hr
        else if (trend > 0) trendStatus = 'Rising'
        else trendStatus = 'Falling'
      }
    }
    
    // Status based on optimal range
    let status = 'Normal'
    let alertLevel = 'none'
    
    if (current < 300) {
      status = 'Critical Low'
      alertLevel = 'critical'
    } else if (current < 400) {
      status = 'Low'
      alertLevel = 'warning'
    } else if (current > 1200) {
      status = 'Critical High'
      alertLevel = 'critical'
    } else if (current > 1000) {
      status = 'High'
      alertLevel = 'warning'
    } else {
      status = 'Normal'
      alertLevel = 'none'
    }
    
    return {
      current: current.toFixed(0),
      average: avg.toFixed(0),
      min: min.toFixed(0),
      max: max.toFixed(0),
      status,
      alertLevel,
      trend: trend.toFixed(2),
      trendStatus,
      trendRate: trend.toFixed(1), // ppm per hour
      sparklineData: allCo2Data.slice(-12).map(d => d.value), // Last 12 points for mini chart
      deviceCount: allDevices.length
    }
  }
})

/* ── CO₂ Forecast ─────────────────── */
const CO2_UNIT = 'ppm'
const FORECAST_RATIO = 0.25
const co2Raw = ref<CO2Reading[]>([])
const bucket = 60    // minutes per bucket
const windowMin = 1440  // minutes back (24 hrs)

// Add CO₂ stats expansion state
const isCo2StatsExpanded = ref(false)

function toggleCo2StatsExpansion() {
  isCo2StatsExpanded.value = !isCo2StatsExpanded.value
}

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

function interpolateNulls(arr: (number | null)[]): (number | null)[] {
  let prevIdx = -1;
  let prevVal = null;
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] == null) {
      // Find next non-null
      let nextIdx = i + 1;
      while (nextIdx < arr.length && arr[nextIdx] == null) nextIdx++;
      if (prevVal != null && nextIdx < arr.length && arr[nextIdx] != null) {
        let nextVal = arr[nextIdx];
        let steps = nextIdx - prevIdx;
        for (let j = 1; j < steps; j++) {
          arr[prevIdx + j] = prevVal + (((nextVal as number) - prevVal) * j / steps);
        }
        i = nextIdx - 1;
      }
    } else {
      prevIdx = i;
      prevVal = arr[i];
    }
  }
  return arr;
}

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
    const dataMap = Object.fromEntries(deviceData.map(r => [r.timestamp, r.co2 ?? null]))
    const rawValues = allTimestamps.map(ts => dataMap[ts] ?? null)
    const values = interpolateNulls([...rawValues])
    return {
      label: `${device} CO₂ (Actual) (${CO2_UNIT})`,
      data: values,
      borderColor: co2DeviceColorMap.value[device],
      pointRadius: 4,
      fill: false
    }
  })
  return { labels, datasets }
})

const co2Options: ChartOptions<'line'> = {
  responsive: true,
  maintainAspectRatio: false,
  layout: {
    padding: {
      top: 10,
      right: 10,
      bottom: 40,
      left: 10
    }
  },
  scales: {
    x: {
      type: 'category',
      title: {
        display: true,
        text: 'Time',
        color: '#fb923c'
      },
      ticks: {
        autoSkip: true,
        maxTicksLimit: 8,
        maxRotation: 0,
        color: '#fb923c'
      },
      grid: {
        color: '#fb923c33'
      }
    },
    y: {
      title: {
        display: true,
        text: `CO₂ (${CO2_UNIT})`,
        color: '#fb923c'
      },
      ticks: {
        color: '#fb923c'
      },
      grid: {
        color: '#fb923c33'
      },
      min: 200,
      max: 1500
    }
  },
  plugins: {
    tooltip: {
      enabled: false, // Disable default tooltip for non-blocking experience
    },
    legend: {
      display: true,
      position: 'top',
      labels: {
        color: '#fb923c',
        usePointStyle: true,
        padding: 15
      }
    },
    // Add annotation plugin for optimal CO₂ bands
    annotation: {
      annotations: {
        optimalBand: {
          type: 'box',
          yMin: 400,
          yMax: 1000,
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderColor: 'rgba(34, 197, 94, 0.3)',
          borderWidth: 1,
          label: {
            display: true,
            content: 'Normal Range (400-1000 ppm)',
            position: 'start',
            color: '#22c55e',
            padding: 4,
            font: {
              size: 10
            }
          }
        },
        warningLowLine: {
          type: 'line',
          yMin: 300,
          yMax: 300,
          borderColor: 'rgba(251, 191, 36, 0.8)',
          borderWidth: 2,
          borderDash: [5, 5],
          label: {
            display: true,
            content: 'Critical Low (300 ppm)',
            position: 'end',
            color: '#fbbf24',
            backgroundColor: 'rgba(251, 191, 36, 0.8)',
            padding: 2,
            font: {
              size: 9
            }
          }
        },
        warningHighLine: {
          type: 'line',
          yMin: 1200,
          yMax: 1200,
          borderColor: 'rgba(239, 68, 68, 0.8)',
          borderWidth: 2,
          borderDash: [5, 5],
          label: {
            display: true,
            content: 'Critical High (1200 ppm)',
            position: 'end',
            color: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.8)',
            padding: 2,
            font: {
              size: 9
            }
          }
        }
      }
    }
  },
  interaction: {
    intersect: false,
    mode: 'index'
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
    return [...devices].sort()
  }
  const query = searchQuery.value.toLowerCase()
  return devices
    .filter(device => device.toLowerCase().includes(query))
    .sort()
}

// Get all devices in a location (unfiltered)
function getDevicesInLocation(location: string): string[] {
  return [...(locationDeviceMap.value[location] || [])].sort()
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

// Update existing functions
function selectAllDevices() {
  const allDevices = Object.values(locationDeviceMap.value).flat()
  selectedDevices.value = [...allDevices]
}

function clearAllDevices() {
  selectedDevices.value = []
  expandedLocations.value = []
}

// Get preview text for selected devices
function getSelectedDevicesPreview(): string {
  if (selectedDevices.value.length === 0) return ''
  if (selectedDevices.value.length <= 2) {
    return selectedDevices.value.join(', ')
  }
  return `${selectedDevices.value.slice(0, 2).join(', ')} and ${selectedDevices.value.length - 2} more`
}

// Update existing remove and clearAll functions to use new names
function remove(dev: string) { 
  removeDevice(dev)
  co2ChartDevices.value = [...selectedDevices.value]
}

function clearAll() {
  clearAllDevices()
  co2ChartDevices.value = []
}

onMounted(async () => {
  // Load saved devices from sessionStorage FIRST
  const savedDevices = sessionStorage.getItem(SELECTED_DEVICES_KEY)
  if (savedDevices) {
    try {
      const parsed = JSON.parse(savedDevices)
      if (Array.isArray(parsed)) {
        selectedDevices.value = parsed
      }
    } catch (e) {
      console.warn('Failed to parse saved devices:', e)
    }
  }

  // Then fetch device names from backend
  try {
    allDeviceNamesRaw.value = await $fetch<string[]>('http://localhost:3001/np-devices')
    backendAvailable.value = true
  } catch (e) {
    backendAvailable.value = false
  }

  // Initialize sessionStorage for last refresh if not set
  if (!sessionStorage.getItem('last-data-refresh')) {
    sessionStorage.setItem('last-data-refresh', new Date().toISOString())
  }

  // Setup outside click detection for dropdown
  if (dropdownRef.value) {
    onClickOutside(dropdownRef, () => (isFilterDropdownOpen.value = false))
  }

  // ✅ ADD THESE EVENT LISTENERS:
  // Listen for storage events to update when sidebar changes the value
  window.addEventListener('storage', handleStorageChange)
  
  // Also listen for custom events from the sidebar
  window.addEventListener('refresh-dashboard-data', handleRefreshEvent)
})

onUnmounted(() => {
  // Clean up event listeners that the dashboard page listens to
  window.removeEventListener('storage', handleStorageChange)
  window.removeEventListener('refresh-dashboard-data', handleRefreshEvent)
})

// Remove old device filter state
// const showDeviceModal = ref(false)
// const deviceSearch = ref('')
// const modalSelected = ref<string[]>([])

// Remove old filter functions
// const filteredDeviceOptions = computed(() => {
//   const search = deviceSearch.value.trim().toLowerCase()
//   if (!search) return allDeviceNamesRaw.value
//   return allDeviceNamesRaw.value.filter(d => d.toLowerCase().includes(search))
// })

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

const co2ChartDevices = ref<string[]>([])

watch(selectedDevices, (newVal) => {
  co2ChartDevices.value = [...newVal]
})

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
button.text-sm {
  cursor: pointer;
}
.flex.items-center.gap-2.p-3.bg-zinc-800\/50:hover {
  cursor: pointer;
}
button.text-xs {
  cursor: pointer;
}
button.flex.items-center.gap-2.flex-1.text-left {
  cursor: pointer;
}
button.w-full.border.rounded.p-3.bg-zinc-900.text-left.text-orange-200.flex.items-center.justify-between {
  cursor: pointer;
}
input[type="checkbox"] {
  cursor: pointer;
}
.ml-1.text-orange-400:hover,
.ml-1.text-orange-400 {
  cursor: pointer;
}
/* Fade transition for dropdowns */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
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

/* Alert pulse animation */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Enhanced slide-down animation */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: top;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px) scaleY(0.95);
  max-height: 0;
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px) scaleY(0.95);
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: translateY(0) scaleY(1);
  max-height: 400px;
}
</style>
