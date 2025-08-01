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
          <!-- RIGHT: Export -->
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
      <section class="pl-0 mb-12">
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
      <section class="mb-16">
        <h2 class="text-2xl font-semibold mb-6 text-orange-400">Moisture Summary</h2>
        <div v-if="selectedDevices.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          <MoistureCard
            v-for="device in selectedDevices"
            :key="device + '-latest'"
            :device="device"
            :title="`${device} Latest`"
            :value="latestMoisture[device] ?? 0"
            :change="round((forecastValues[device]?.[29] ?? 0) - latestMoisture[device])"
            :changeLabel="'vs forecast'"
            :status="statusTag(latestMoisture[device])"
            :is-forecast="false"
            class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl orange-glow transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl p-6 min-h-[200px]"
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
        <div v-else class="w-full flex items-center justify-center h-40 text-orange-300 text-xl font-bold">
          Please select a device to get started.
        </div>
      </section>

      <!-- 📈 Historical Charts -->
      <section class="mb-16">
        <h2 class="text-2xl font-semibold mt-8 mb-6 text-orange-400">Recent Soil Moisture Readings</h2>
        <template v-if="selectedDevices.length">
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-10 justify-start items-start w-full">
            <div
              v-for="(device, idx) in selectedDevices"
              :key="device + '-chart'"
              class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl orange-glow flex flex-col gap-4 transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl p-8 min-h-[500px]"
              style="will-change: transform;"
            >
              <!-- Chart Title and Download button -->
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-orange-300">{{ device }} - Historical Data</h3>
                <button
                  @click="downloadChartImage(`historical-${device}`, `${device}-historical.png`)"
                  class="flex items-center gap-2 px-4 py-2 rounded bg-transparent border border-orange-500 text-orange-500 font-semibold hover:bg-orange-500 hover:text-white group cursor-pointer transition-all duration-200"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-400 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" />
                  </svg>
                  Download
                </button>
              </div>
              
              <!-- Chart Container with Stats Overlay -->
              <div class="relative flex-1 min-h-[400px] overflow-hidden">
                <Line :id="`historical-${device}`" :data="historicalChart(deviceData[device] ?? [], device, idx)" :options="getChartOptions()" class="h-full w-full" />
                
                <!-- Enhanced Stats Container with Pin/Drag functionality -->
                <div 
                  class="stats-container"
                  :class="{
                    'absolute z-50': pinnedStats[device]?.isPinned,
                    'absolute top-4 right-4 z-10': !pinnedStats[device]?.isPinned
                  }"
                  :style="pinnedStats[device]?.isPinned ? {
                    left: pinnedStats[device].position.x + 'px',
                    top: pinnedStats[device].position.y + 'px',
                    position: 'fixed'
                  } : {}"
                  v-show="pinnedStats[device]?.isVisible !== false"
                  @mouseenter="handleInfoHover(device, true)"
                  @mouseleave="handleInfoHover(device, false)"
                >
                  <div class="bg-zinc-900/95 border border-orange-500/50 rounded-lg backdrop-blur-sm min-w-[200px]">
                    
                    <!-- Alert indicator -->
                    <div v-if="getMoistureChartStats(device)?.alertLevel !== 'none'" 
                        class="absolute -top-2 -right-2 w-4 h-4 rounded-full animate-pulse"
                        :class="{
                          'bg-yellow-500': getMoistureChartStats(device)?.alertLevel === 'warning',
                          'bg-red-500': getMoistureChartStats(device)?.alertLevel === 'critical'
                        }">
                    </div>
                    
                    <!-- Enhanced Header with Pin/Drag controls -->
                    <div class="flex items-center justify-between px-3 py-2 border-b border-orange-700/50">
                      <!-- Left: Collapsible button -->
                      <button 
                        @click="toggleStatsExpansion(device)"
                        class="flex items-center gap-2 text-xs text-orange-300 font-medium hover:text-orange-200 transition-colors"
                      >
                        <span>Moisture Stats</span>
                        <div class="flex items-center gap-1">
                          <div class="w-2 h-2 rounded-full"
                              :class="{
                                'bg-green-400': getMoistureChartStats(device)?.alertLevel === 'none',
                                'bg-yellow-400': getMoistureChartStats(device)?.alertLevel === 'warning', 
                                'bg-red-400': getMoistureChartStats(device)?.alertLevel === 'critical'
                              }">
                          </div>
                          <span class="text-xs"
                                :class="{
                                  'text-green-400': getMoistureChartStats(device)?.alertLevel === 'none',
                                  'text-yellow-400': getMoistureChartStats(device)?.alertLevel === 'warning',
                                  'text-red-400': getMoistureChartStats(device)?.alertLevel === 'critical'
                                }"
                                v-if="getMoistureChartStats(device)?.alertLevel !== 'none'">
                            {{ getMoistureChartStats(device)?.status }}
                          </span>
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
                      
                      <!-- Right: Pin and visibility controls -->
                      <div class="flex items-center gap-1">
                        <!-- Drag handle (only show when pinned) -->
                        <button 
                          v-if="pinnedStats[device]?.isPinned"
                          @mousedown="startDrag($event, device)"
                          class="p-1 text-orange-400 hover:text-orange-200 cursor-move transition-colors"
                          title="Drag to move"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M4 8h16M4 16h16"/>
                          </svg>
                        </button>
                        
                        <!-- Pin/Unpin button -->
                        <button 
                          @click="togglePin(device)"
                          class="p-1 text-orange-400 hover:text-orange-200 transition-colors"
                          :title="pinnedStats[device]?.isPinned ? 'Unpin stats' : 'Pin stats'"
                        >
                          <svg v-if="pinnedStats[device]?.isPinned" class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z"/>
                          </svg>
                          <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
                          </svg>
                        </button>
                        
                        <!-- Hide/Show toggle (only show when pinned) -->
                        <button 
                          v-if="pinnedStats[device]?.isPinned"
                          @click="toggleStatsVisibility(device)"
                          class="p-1 text-orange-400 hover:text-orange-200 transition-colors"
                          title="Hide stats"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Collapsible Content -->
                    <transition name="slide-down">
                      <div v-if="isStatsExpanded(device)" class="px-3 pb-3">
                        <div v-if="getMoistureChartStats(device)" class="space-y-2">
                          
                          <!-- Trend Indicator -->
                          <div class="bg-zinc-800/50 rounded p-2 mb-2">
                            <div class="text-xs text-orange-300 mb-1">Recent Trend</div>
                            <div class="h-8 flex items-center justify-center">
                              <div v-if="getMoistureChartStats(device)?.trendStatus === 'Stable'" 
                                  class="flex items-center gap-2 text-gray-400">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14"/>
                                </svg>
                                <span class="text-sm font-medium">Stable</span>
                              </div>
                              
                              <div v-else-if="getMoistureChartStats(device)?.trendStatus?.includes('Increasing') || getMoistureChartStats(device)?.trendStatus?.includes('Rising')" 
                                  class="flex items-center gap-2 text-blue-400">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17l9.2-9.2M17 17V7H7"/>
                                </svg>
                                <span class="text-sm font-medium">Rising</span>
                              </div>
                              
                              <div v-else-if="getMoistureChartStats(device)?.trendStatus?.includes('Decreasing') || getMoistureChartStats(device)?.trendStatus?.includes('Falling')" 
                                  class="flex items-center gap-2 text-red-400">
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
                              <span class="font-medium">{{ getMoistureChartStats(device)?.current }}%</span>
                            </div>
                            <div class="flex justify-between">
                              <span>Average:</span>
                              <span class="font-medium">{{ getMoistureChartStats(device)?.average }}%</span>
                            </div>
                            <div class="flex justify-between">
                              <span>Range:</span>
                              <span class="font-medium">{{ getMoistureChartStats(device)?.min }}-{{ getMoistureChartStats(device)?.max }}%</span>
                            </div>
                          </div>
                          
                          <!-- Trend Analysis -->
                          <div class="border-t border-orange-700/50 pt-2">
                            <div class="text-xs text-orange-300 mb-1">Trend Analysis</div>
                            <div class="flex justify-between text-xs text-orange-200">
                              <span>Rate:</span>
                              <span class="font-medium"
                                    :class="{
                                      'text-blue-400': getMoistureChartStats(device)?.trendStatus?.includes('Increasing') || getMoistureChartStats(device)?.trendStatus?.includes('Rising'),
                                      'text-red-400': getMoistureChartStats(device)?.trendStatus?.includes('Decreasing') || getMoistureChartStats(device)?.trendStatus?.includes('Falling'),
                                      'text-gray-400': getMoistureChartStats(device)?.trendStatus === 'Stable'
                                    }">
                                {{ getMoistureChartStats(device)?.trend }}%/reading
                              </span>
                            </div>
                            <div class="flex justify-between text-xs text-orange-200">
                              <span>Status:</span>
                              <span class="font-medium"
                                    :class="{
                                      'text-blue-400': getMoistureChartStats(device)?.trendStatus?.includes('Increasing') || getMoistureChartStats(device)?.trendStatus?.includes('Rising'),
                                      'text-red-400': getMoistureChartStats(device)?.trendStatus?.includes('Decreasing') || getMoistureChartStats(device)?.trendStatus?.includes('Falling'),
                                      'text-gray-400': getMoistureChartStats(device)?.trendStatus === 'Stable'
                                    }">
                                {{ getMoistureChartStats(device)?.trendStatus }}
                              </span>
                            </div>
                          </div>
                          
                          <!-- Status Badge -->
                          <div class="text-center mt-2 px-2 py-1 rounded text-xs border-t border-orange-700/50 pt-2">
                            <div class="font-medium"
                                :class="{
                                  'text-green-400': getMoistureChartStats(device)?.alertLevel === 'none',
                                  'text-yellow-400': getMoistureChartStats(device)?.alertLevel === 'warning',
                                  'text-red-400': getMoistureChartStats(device)?.alertLevel === 'critical'
                                }">
                              {{ getMoistureChartStats(device)?.status }}
                            </div>
                            <div class="text-orange-400 text-xs mt-1">
                              Optimal: 40-70%
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
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="flex items-center justify-center h-40 text-orange-300 text-xl font-bold">
            Please select a device to get started.
          </div>
        </template>
      </section>

      <!-- 📉 Forecast Chart -->
      <section class="w-full mb-12 flex flex-col items-start">
        <h2 class="text-2xl font-semibold mt-8 mb-6 text-orange-400">Moisture Forecast (Next 30 Days)</h2>
        <template v-if="selectedDevices.length && forecastChart">
          <div
            class="bg-[#121212] from-zinc-900 via-zinc-800 to-zinc-900 border border-orange-300/20 rounded-xl shadow-xl orange-glow w-full flex flex-col gap-4 max-w-full transition-transform duration-200 hover:-translate-y-1 hover:shadow-2xl p-8 min-h-[600px]"
            style="will-change: transform;"
          >
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-orange-300">30-Day Moisture Forecast</h3>
              <button @click="downloadChartImage('forecast-chart', 'forecast-30day.png')" class="flex items-center gap-2 px-4 py-2 rounded bg-transparent border border-orange-500 text-orange-500 font-semibold hover:bg-orange-500 hover:text-white group cursor-pointer transition-all duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-orange-400 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 16v-8m0 8l-4-4m4 4l4-4M4 20h16" />
                </svg>
                Download
              </button>
            </div>
            
            <!-- Chart Container with Stats Overlay -->
            <div class="flex-1 min-h-[500px] overflow-hidden w-full relative">
              <Line id="forecast-chart" :data="forecastChart" :options="forecastOptions" class="h-full w-full" />
              
              <!-- Enhanced Stats Container with Pin/Drag functionality -->
              <div 
                class="stats-container"
                :class="{
                  'absolute z-50': pinnedStats['forecast-chart']?.isPinned,
                  'absolute top-4 right-4 z-10': !pinnedStats['forecast-chart']?.isPinned
                }"
                :style="pinnedStats['forecast-chart']?.isPinned ? {
                  left: pinnedStats['forecast-chart'].position.x + 'px',
                  top: pinnedStats['forecast-chart'].position.y + 'px',
                  position: 'fixed'
                } : {}"
                v-show="pinnedStats['forecast-chart']?.isVisible !== false"
                @mouseenter="handleInfoHover('forecast-chart', true)"
                @mouseleave="handleInfoHover('forecast-chart', false)"
              >
                <div class="bg-zinc-900/95 border border-orange-500/50 rounded-lg backdrop-blur-sm min-w-[220px]">
                  
                  <!-- Alert indicator -->
                  <div v-if="getForecastChartStats()?.alertLevel !== 'none'" 
                      class="absolute -top-2 -right-2 w-4 h-4 rounded-full animate-pulse"
                      :class="{
                        'bg-yellow-500': getForecastChartStats()?.alertLevel === 'warning',
                        'bg-red-500': getForecastChartStats()?.alertLevel === 'critical'
                      }">
                  </div>
                  
                  <!-- Enhanced Header with Pin/Drag controls -->
                  <div class="flex items-center justify-between px-3 py-2 border-b border-orange-700/50">
                    <!-- Left: Collapsible button -->
                    <button 
                      @click="toggleForecastStatsExpansion()"
                      class="flex items-center gap-2 text-xs text-orange-300 font-medium hover:text-orange-200 transition-colors"
                    >
                      <span>Forecast Stats</span>
                      <div class="flex items-center gap-1">
                        <div class="w-2 h-2 rounded-full"
                            :class="{
                              'bg-green-400': getForecastChartStats()?.alertLevel === 'none',
                              'bg-yellow-400': getForecastChartStats()?.alertLevel === 'warning', 
                              'bg-red-400': getForecastChartStats()?.alertLevel === 'critical'
                            }">
                        </div>
                        <span class="text-xs"
                              :class="{
                                'text-green-400': getForecastChartStats()?.alertLevel === 'none',
                                'text-yellow-400': getForecastChartStats()?.alertLevel === 'warning',
                                'text-red-400': getForecastChartStats()?.alertLevel === 'critical'
                              }"
                              v-if="getForecastChartStats()?.alertLevel !== 'none'">
                          {{ getForecastChartStats()?.status }}
                        </span>
                      </div>
                      <svg 
                        :class="{'rotate-180': isForecastStatsExpanded}" 
                        class="w-3 h-3 transition-transform" 
                        fill="none" 
                        stroke="currentColor" 
                        stroke-width="2" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                      </svg>
                    </button>
                    
                    <!-- Right: Pin and visibility controls -->
                    <div class="flex items-center gap-1">
                      <!-- Drag handle (only show when pinned) -->
                      <button 
                        v-if="pinnedStats['forecast-chart']?.isPinned"
                        @mousedown="startDrag($event, 'forecast-chart')"
                        class="p-1 text-orange-400 hover:text-orange-200 cursor-move transition-colors"
                        title="Drag to move"
                      >
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M4 8h16M4 16h16"/>
                        </svg>
                      </button>
                      
                      <!-- Pin/Unpin button -->
                      <button 
                        @click="togglePin('forecast-chart')"
                        class="p-1 text-orange-400 hover:text-orange-200 transition-colors"
                        :title="pinnedStats['forecast-chart']?.isPinned ? 'Unpin stats' : 'Pin stats'"
                      >
                        <svg v-if="pinnedStats['forecast-chart']?.isPinned" class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z"/>
                        </svg>
                        <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
                        </svg>
                      </button>
                      
                      <!-- Hide/Show toggle (only show when pinned) -->
                      <button 
                        v-if="pinnedStats['forecast-chart']?.isPinned"
                        @click="toggleStatsVisibility('forecast-chart')"
                        class="p-1 text-orange-400 hover:text-orange-200 transition-colors"
                        title="Hide stats"
                      >
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Collapsible Content -->
                  <transition name="slide-down">
                    <div v-if="isForecastStatsExpanded" class="px-3 pb-3">
                      <div v-if="getForecastChartStats()" class="space-y-2">
                        
                        <!-- Forecast Trend Indicator -->
                        <div class="bg-zinc-800/50 rounded p-2 mb-2">
                          <div class="text-xs text-orange-300 mb-1">30-Day Trend</div>
                          <div class="h-8 flex items-center justify-center">
                            <div v-if="getForecastChartStats()?.trendStatus === 'Stable'" 
                                class="flex items-center gap-2 text-gray-400">
                              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14"/>
                              </svg>
                              <span class="text-sm font-medium">Stable</span>
                            </div>
                            
                            <div v-else-if="getForecastChartStats()?.trendStatus?.includes('Increasing') || getForecastChartStats()?.trendStatus?.includes('Rising')" 
                                class="flex items-center gap-2 text-blue-400">
                              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17l9.2-9.2M17 17V7H7"/>
                              </svg>
                              <span class="text-sm font-medium">Rising</span>
                            </div>
                            
                            <div v-else-if="getForecastChartStats()?.trendStatus?.includes('Decreasing') || getForecastChartStats()?.trendStatus?.includes('Falling')" 
                                class="flex items-center gap-2 text-red-400">
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
                        
                        <!-- Forecast Stats -->
                        <div class="text-xs text-orange-200 space-y-1">
                          <div class="flex justify-between">
                            <span>Devices:</span>
                            <span class="font-medium">{{ getForecastChartStats()?.deviceCount }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span>Day 1 Avg:</span>
                            <span class="font-medium">{{ getForecastChartStats()?.day1 }}%</span>
                          </div>
                          <div class="flex justify-between">
                            <span>Day 30 Avg:</span>
                            <span class="font-medium">{{ getForecastChartStats()?.day30 }}%</span>
                          </div>
                          <div class="flex justify-between">
                            <span>Overall Avg:</span>
                            <span class="font-medium">{{ getForecastChartStats()?.average }}%</span>
                          </div>
                          <div class="flex justify-between">
                            <span>Range:</span>
                            <span class="font-medium">{{ getForecastChartStats()?.min }}-{{ getForecastChartStats()?.max }}%</span>
                          </div>
                        </div>
                        
                        <!-- Forecast Trend Analysis -->
                        <div class="border-t border-orange-700/50 pt-2">
                          <div class="text-xs text-orange-300 mb-1">Trend Analysis</div>
                          <div class="flex justify-between text-xs text-orange-200">
                            <span>Change:</span>
                            <span class="font-medium"
                                  :class="{
                                    'text-blue-400': getForecastChartStats()?.trendStatus?.includes('Increasing') || getForecastChartStats()?.trendStatus?.includes('Rising'),
                                    'text-red-400': getForecastChartStats()?.trendStatus?.includes('Decreasing') || getForecastChartStats()?.trendStatus?.includes('Falling'),
                                    'text-gray-400': getForecastChartStats()?.trendStatus === 'Stable'
                                  }">
                              {{ getForecastChartStats()?.trend }}% over 30 days
                            </span>
                          </div>
                          <div class="flex justify-between text-xs text-orange-200">
                            <span>Status:</span>
                            <span class="font-medium"
                                  :class="{
                                    'text-blue-400': getForecastChartStats()?.trendStatus?.includes('Increasing') || getForecastChartStats()?.trendStatus?.includes('Rising'),
                                    'text-red-400': getForecastChartStats()?.trendStatus?.includes('Decreasing') || getForecastChartStats()?.trendStatus?.includes('Falling'),
                                    'text-gray-400': getForecastChartStats()?.trendStatus === 'Stable'
                                  }">
                              {{ getForecastChartStats()?.trendStatus }}
                            </span>
                          </div>
                        </div>
                        
                        <!-- Status Badge -->
                        <div class="text-center mt-2 px-2 py-1 rounded text-xs border-t border-orange-700/50 pt-2">
                          <div class="font-medium"
                              :class="{
                                'text-green-400': getForecastChartStats()?.alertLevel === 'none',
                                'text-yellow-400': getForecastChartStats()?.alertLevel === 'warning',
                                'text-red-400': getForecastChartStats()?.alertLevel === 'critical'
                              }">
                            {{ getForecastChartStats()?.status }}
                          </div>
                          <div class="text-orange-400 text-xs mt-1">
                            {{ getForecastChartStats()?.forecastPeriod }} prediction
                          </div>
                        </div>
                      </div>
                      <div v-else class="text-xs text-orange-400">
                        No forecast data available
                      </div>
                    </div>
                  </transition>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="w-full flex items-center justify-center h-40 text-orange-300 text-xl font-bold">
            Please select a device to get started.
          </div>
        </template>
      </section>
    </div>
  </div>
  <!-- Floating Control Panel for Hidden Pinned Stats -->
  <div v-if="Object.values(pinnedStats).some(stats => stats.isPinned)" 
      class="fixed bottom-4 right-4 z-50 bg-zinc-900/95 border border-orange-500/50 rounded-lg backdrop-blur-sm p-2">
    <div class="text-xs text-orange-300 mb-2 font-medium">Pinned Stats</div>
    <div class="flex flex-col gap-1">
      <!-- Device stats -->
      <template v-for="device in selectedDevices" :key="device">
        <button 
          v-if="pinnedStats[device]?.isPinned"
          @click="toggleStatsVisibility(device)"
          class="flex items-center gap-2 px-2 py-1 text-xs rounded hover:bg-orange-600/20 transition-colors"
          :class="{
            'text-orange-200': pinnedStats[device]?.isVisible,
            'text-orange-500': !pinnedStats[device]?.isVisible
          }"
        >
          <div class="w-2 h-2 rounded-full"
              :class="{
                'bg-green-400': pinnedStats[device]?.isVisible,
                'bg-gray-500': !pinnedStats[device]?.isVisible
              }">
          </div>
          <span class="truncate max-w-[120px]">{{ device }}</span>
          <svg v-if="!pinnedStats[device]?.isVisible" class="w-3 h-3 ml-auto" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
          <svg v-else class="w-3 h-3 ml-auto" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122L12 12m0 0l3.122 3.122M12 12l6.879 6.878"/>
          </svg>
        </button>
      </template>
      
      <!-- Forecast chart stats -->
      <button 
        v-if="pinnedStats['forecast-chart']?.isPinned"
        @click="toggleStatsVisibility('forecast-chart')"
        class="flex items-center gap-2 px-2 py-1 text-xs rounded hover:bg-orange-600/20 transition-colors"
        :class="{
          'text-orange-200': pinnedStats['forecast-chart']?.isVisible,
          'text-orange-500': !pinnedStats['forecast-chart']?.isVisible
        }"
      >
        <div class="w-2 h-2 rounded-full"
            :class="{
              'bg-green-400': pinnedStats['forecast-chart']?.isVisible,
              'bg-gray-500': !pinnedStats['forecast-chart']?.isVisible
            }">
        </div>
        <span class="truncate max-w-[120px]">Forecast Chart</span>
        <svg v-if="!pinnedStats['forecast-chart']?.isVisible" class="w-3 h-3 ml-auto" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
        </svg>
        <svg v-else class="w-3 h-3 ml-auto" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L12 12m-3.122-3.122L12 12m0 0l3.122 3.122M12 12l6.879 6.878"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">

type MoistureData = {
  timestamp: string;   // Timestamp for each sensor reading
  devicename: string;  // The name of the device
  moisture: number;    // Soil moisture value
  temperature: number | null;  // Soil temperature value (nullable)
  npk_n: number | null; // Soil Nitrogen (nullable)
  npk_p: number | null; // Soil Phosphorus (nullable)
  npk_k: number | null; // Soil Potassium (nullable)
  co2: number | null;  // CO2 levels (nullable)
}

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
import { Transition } from 'vue'
import Sidebar from '../components/Sidebar/index.vue'
import { onClickOutside } from '@vueuse/core'
import { ML_CONFIG, MLApiService, transformDataForML } from './ml_config_file.js'
import * as XLSX from 'xlsx';
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Button } from '@/components/ui/button'

const mlApiUrl = 'http://localhost:5000' // Your Flask ML API URL
const mlPredictions = ref<Record<string, any>>({})
const mlLoading = ref(false)
const mlError = ref<string | null>(null)
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

// Add these after your existing reactive state (around line 400)
const expandedStats = reactive<Record<string, boolean>>({})
const pinnedStats = reactive<Record<string, { isPinned: boolean; position: { x: number; y: number }; isVisible: boolean }>>({})
const dragState = ref<{ isDragging: boolean; deviceKey: string; startX: number; startY: number; startLeft: number; startTop: number } | null>(null)

// Add hover handler for intelligent tooltip positioning
const hoverTimeouts = ref<Record<string, NodeJS.Timeout>>({})

function handleInfoHover(device: string, isEntering: boolean) {
  if (isEntering) {
    if (hoverTimeouts.value[device]) {
      clearTimeout(hoverTimeouts.value[device])
    }
  } else {
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

// (Removed duplicate implementation of initializePinnedStats)

// Toggle stats expansion for a device
function toggleStatsExpansion(device: string) {
  expandedStats[device] = !expandedStats[device]
}

// Check if stats are expanded for a device
function isStatsExpanded(device: string): boolean {
  return expandedStats[device] || false
}

function togglePin(device: string) {
  if (!pinnedStats[device]) return
  pinnedStats[device].isPinned = !pinnedStats[device].isPinned
  
  if (!pinnedStats[device].isPinned) {
    pinnedStats[device].position = { x: 10, y: 10 }
  }
}

function toggleStatsVisibility(device: string) {
  if (!pinnedStats[device]) return
  pinnedStats[device].isVisible = !pinnedStats[device].isVisible
}

function startDrag(event: MouseEvent, device: string) {
  if (!pinnedStats[device]?.isPinned) return
  
  const rect = (event.target as HTMLElement).closest('.stats-container')?.getBoundingClientRect()
  if (!rect) return
  
  dragState.value = {
    isDragging: true,
    deviceKey: device,
    startX: event.clientX,
    startY: event.clientY,
    startLeft: pinnedStats[device].position.x,
    startTop: pinnedStats[device].position.y
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event: MouseEvent) {
  if (!dragState.value) return
  
  const deltaX = event.clientX - dragState.value.startX
  const deltaY = event.clientY - dragState.value.startY
  
  pinnedStats[dragState.value.deviceKey].position = {
    x: Math.max(0, dragState.value.startLeft + deltaX),
    y: Math.max(0, dragState.value.startTop + deltaY)
  }
}

function stopDrag() {
  dragState.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// Enhanced chart stats with trend analysis for moisture data (CORRECTED)
const getMoistureChartStats = computed(() => {
  return (device: string) => {
    const deviceDataArray = deviceData.value[device] || []
    if (!deviceDataArray.length) return null
    
    const moistureValues = deviceDataArray.map(d => d.moisture).filter(m => m != null) as number[]
    if (!moistureValues.length) return null
    
    const current = moistureValues[0] // Latest reading (first in array since it's sorted newest first)
    const avg = moistureValues.reduce((a, b) => a + b, 0) / moistureValues.length
    const min = Math.min(...moistureValues)
    const max = Math.max(...moistureValues)
    
    // Enhanced trend detection (using last 5 readings)
    const trendData = moistureValues.slice(0, 5) // Get last 5 readings
    let trend = 0
    let trendStatus = 'Stable'
    
    if (trendData.length >= 3) {
      // Calculate trend correctly (newest - oldest)
      const oldestMoisture = trendData[trendData.length - 1] // Oldest of the 5
      const newestMoisture = trendData[0] // Newest
      const timeSpanHours = trendData.length - 1
      
      if (timeSpanHours > 0) {
        trend = (newestMoisture - oldestMoisture) / timeSpanHours
        const absTrend = Math.abs(trend)
        
        if (absTrend < 0.5) {
          trendStatus = 'Stable'
        } else if (trend > 1.5) {
          trendStatus = 'Increasing'
        } else if (trend > 0.5) {
          trendStatus = 'Rising'
        } else if (trend < -1.5) {
          trendStatus = 'Decreasing'
        } else if (trend < -0.5) {
          trendStatus = 'Falling'
        }
      }
    }
    
    // Status based on current moisture reading (40-70% optimal range)
    let status = 'Optimal'
    let alertLevel = 'none'
    
    if (current < 20) {
      status = 'Critical Dry'
      alertLevel = 'critical'
    } else if (current < 40) {
      status = 'Below Optimal'
      alertLevel = 'warning'
    } else if (current > 80) {
      status = 'Critical Wet'
      alertLevel = 'critical'
    } else if (current > 70) {
      status = 'Above Optimal'
      alertLevel = 'warning'
    } else {
      status = 'Optimal' // 40-70% range
      alertLevel = 'none'
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
      deviceName: device,
      dataPoints: moistureValues.length
    }
  }
})

// Enhanced forecast stats with trend analysis
const getForecastChartStats = computed(() => {
  return () => {
    if (!selectedDevices.value.length || !forecastChart.value) return null
    
    const allForecastValues: number[] = []
    const deviceForecasts: { device: string; values: number[] }[] = []
    
    selectedDevices.value.forEach(device => {
      const deviceForecast = forecastValues.value[device] || []
      if (deviceForecast.length) {
        deviceForecasts.push({ device, values: deviceForecast })
        allForecastValues.push(...deviceForecast)
      }
    })
    
    if (!allForecastValues.length) return null
    
    // Calculate overall forecast stats
    const avgForecast = allForecastValues.reduce((a, b) => a + b, 0) / allForecastValues.length
    const minForecast = Math.min(...allForecastValues)
    const maxForecast = Math.max(...allForecastValues)
    
    // Calculate trend from day 1 to day 30
    const day1Avg = deviceForecasts.reduce((sum, df) => sum + (df.values[0] || 0), 0) / deviceForecasts.length
    const day30Avg = deviceForecasts.reduce((sum, df) => sum + (df.values[29] || 0), 0) / deviceForecasts.length
    
    const overallTrend = day30Avg - day1Avg
    let trendStatus = 'Stable'
    
    if (Math.abs(overallTrend) < 2) {
      trendStatus = 'Stable'
    } else if (overallTrend > 5) {
      trendStatus = 'Increasing'
    } else if (overallTrend > 2) {
      trendStatus = 'Rising'
    } else if (overallTrend < -5) {
      trendStatus = 'Decreasing'
    } else if (overallTrend < -2) {
      trendStatus = 'Falling'
    }
    
    // Overall status based on forecast average
    let status = 'Forecasted Healthy'
    let alertLevel = 'none'
    
    if (avgForecast < 30) {
      status = 'Forecasted Critical Dry'
      alertLevel = 'critical'
    } else if (avgForecast < 40) {
      status = 'Forecasted Below Optimal'
      alertLevel = 'warning'
    } else if (avgForecast > 80) {
      status = 'Forecasted Critical Wet'
      alertLevel = 'critical'
    } else if (avgForecast > 70) {
      status = 'Forecasted Above Optimal'
      alertLevel = 'warning'
    }
    
    return {
      average: avgForecast.toFixed(1),
      min: minForecast.toFixed(1),
      max: maxForecast.toFixed(1),
      day1: day1Avg.toFixed(1),
      day30: day30Avg.toFixed(1),
      trend: overallTrend.toFixed(1),
      trendStatus,
      status,
      alertLevel,
      deviceCount: selectedDevices.value.length,
      forecastPeriod: '30 days'
    }
  }
})

// Add forecast stats expansion state
const isForecastStatsExpanded = ref(false)

function toggleForecastStatsExpansion() {
  isForecastStatsExpanded.value = !isForecastStatsExpanded.value
}

// Update initializePinnedStats to include forecast chart
function initializePinnedStats() {
  selectedDevices.value.forEach(device => {
    if (!(device in pinnedStats)) {
      pinnedStats[device] = {
        isPinned: false,
        position: { x: 10, y: 10 },
        isVisible: true
      }
    }
  })
  
  // Add forecast chart stats
  if (!('forecast-chart' in pinnedStats)) {
    pinnedStats['forecast-chart'] = {
      isPinned: false,
      position: { x: 10, y: 10 },
      isVisible: true
    }
  }
}

// 1️⃣ state to hold the recommendation text
const recommendation = ref('')

// Combined filter state
const selectedDevices = ref<string[]>([])
const isFilterDropdownOpen = ref(false)
const searchQuery = ref('')
const expandedLocations = ref<string[]>([])

// Enhanced device recommendations based on current status AND forecast trend
const deviceRecommendations = computed<Record<string,string>>(() => {
  return selectedDevices.value.reduce((map, device) => {
    const currentMoisture = latestMoisture.value[device] ?? 0
    const forecastDay30 = forecastValues.value[device]?.[29] ?? 0
    const change = forecastDay30 - currentMoisture
    const currentStatus = statusTag(currentMoisture)
    const mlInfo = mlPredictions.value[device]
    const modelUsed = mlInfo?.model_used || 'Linear Regression (Fallback)'
    
    let recommendation = ''
    
    // Determine forecast trend
    const isImproving = change > 5
    const isStable = Math.abs(change) <= 5
    const isDeclining = change < -5
    
    // Generate recommendations based on current status AND forecast trend
    if (currentStatus === 'Dry') {
      if (isImproving) {
        recommendation = '🌱 Current soil is dry, but forecast shows improvement! Water lightly now and monitor - conditions should naturally improve over the next 30 days.'
      } else if (isDeclining) {
        recommendation = '⚠️ Soil is dry and forecast shows further drying! Increase watering frequency immediately and consider adding mulch to retain moisture.'
      } else {
        recommendation = '💧 Soil is dry with stable forecast. Water thoroughly now and maintain regular watering schedule.'
      }
    } else if (currentStatus === 'Too Wet') {
      if (isImproving) {
        recommendation = '☀️ Soil is currently too wet, but forecast shows it will dry to optimal levels. Reduce watering and allow natural drying - perfect timing!'
      } else if (isDeclining) {
        recommendation = '🚨 Soil is too wet and forecast shows continued wetness! Stop watering immediately, improve drainage, and ensure good air circulation.'
      } else {
        recommendation = '⏸️ Soil is too wet with stable forecast. Pause watering and allow soil to dry out before resuming.'
      }
    } else { // Healthy
      if (isImproving) {
        recommendation = '✨ Soil is healthy and forecast shows even better conditions ahead! Continue current care routine - you\'re doing great!'
      } else if (isDeclining) {
        recommendation = '📉 Soil is currently healthy but forecast shows decline. Consider slightly increasing watering frequency to prevent future dryness.'
      } else {
        recommendation = '👍 Soil is healthy with stable forecast. Maintain your current watering schedule - perfect balance!'
      }
    }
    
    // Add forecast insight
    const trendText = isImproving ? 'improving' : isDeclining ? 'declining' : 'stable'
    const changeText = Math.abs(change).toFixed(1)
    
    map[device] = `${recommendation}\n\n📊 30-day outlook: ${trendText} (${change > 0 ? '+' : ''}${changeText}% change)\n🤖 Model: ${modelUsed}`
    
    return map
  }, {} as Record<string,string>)
})

// 2️⃣ Computed property to get the latest moisture values for selected devices
const clickedDataPoints = ref<string[]>([]) // Array to track clicked data points

const handleChartClick = (event: any, chartElement: any) => {
  if (chartElement.length > 0) {
    const clickedPoint = chartElement[0];
    const datasetIndex = clickedPoint.datasetIndex;
    const index = clickedPoint.index;

    // Create a unique identifier for the clicked point
    const pointId = `${datasetIndex}-${index}`;

    // Toggle visibility of the clicked data point
    if (clickedDataPoints.value.includes(pointId)) {
      // Remove it from the clicked points
      clickedDataPoints.value = clickedDataPoints.value.filter(id => id !== pointId);
    } else {
      // Add it to the clicked points
      clickedDataPoints.value.push(pointId);
    }

    // Update the chart to reflect the changes
    nextTick(() => {
      chartElement.chart.update(); // Update the chart after modifying the data
    });
  }
};

/* ── State ───────────────────────────── */
const rawData = ref<MoistureData[]>([])

/* ── Loading State ───────────────────────────── */
const isLoading = ref(true)

/* ── Fetch Data ───────────────────────────── */
watchEffect(async () => {
  const { data } = await useFetch<MoistureData[]>(
    'http://localhost:3001/moisture-detailed'
  );
  rawData.value = data.value ?? [];
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
      .map(r => r.map(val => "${val}").join(','))
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

  / 🟢 Summary Sheet /
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

  / 📈 Historical Data Sheet /
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

  / 🔮 Forecast Data Sheet /
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

  / 💾 Save Workbook */
  XLSX.writeFile(wb, 'soil_moisture_dashboard_report.xlsx');
}
async function checkMLApiHealth() {
  try {
    const response = await fetch(`${mlApiUrl}/health`)
    const health = await response.json()
    console.log('ML API Health:', health)
    return health.model_loaded
  } catch (error) {
    console.error('ML API Health check failed:', error)
    return false
  }
}


// Function to fetch ML predictions
async function fetchMLPredictions() {
  if (!selectedDevices.value.length) return

  mlLoading.value = true
  mlError.value = null

  try {
    // Prepare data for batch prediction
    const devicesData: Record<string, any> = {}

    for (const device of selectedDevices.value) {
      const recentData = deviceData.value[device]?.slice(0, 500) || []
      // Use transformDataForML to match ML API expected format
      const formattedData = transformDataForML(recentData)
      devicesData[device] = {
        recent_data: formattedData
      }
    }

    const response = await fetch(`${mlApiUrl}/predict/moisture/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        devices: devicesData,
        days_ahead: 30
      })
    })

    if (!response.ok) {
      throw new Error(`ML API error: ${response.status}`)
    }

    const result = await response.json()
    mlPredictions.value = result.predictions


  } catch (error) {
    console.error('Error fetching ML predictions:', error)
    mlError.value = error instanceof Error ? error.message : 'Unknown error occurred'
  } finally {
    mlLoading.value = false
  }
}
/* ── Download Data ───────────────────────────── */
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
  // Check if ML API is available
  const mlApiAvailable = await checkMLApiHealth()
  if (!mlApiAvailable) {
    console.warn('ML API is not available, falling back to simple forecasting')
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
  const deviceName = data[0]?.devicename

  // Use ML predictions if available
  if (deviceName && mlPredictions.value[deviceName]?.forecast) {
    const mlForecast = mlPredictions.value[deviceName].forecast
    return mlForecast.map((item: any) => round(item.predicted_moisture))
  }

  // Fallback to simple linear regression if ML not available
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

  // Initialize predictions array
  let predictions: number[] = []

  // Use the last known value as the starting point for prediction
  let lastPrediction = smoothed[smoothed.length - 1]

  // Predict for the next 30 days
  for (let i = 0; i < 30; i++) {
    // Apply trend using linear regression formula
    const trend = slope * (n + i) + intercept
    
    // Add jitter to the prediction (you can adjust the range of jitter)
    const jitter = (Math.random() - 0.5) * 0.4
    
    // The predicted moisture value for the current day
    const prediction = round(trend + jitter)
    predictions.push(prediction)

    // Use the predicted value as the starting point for the next day's prediction
    lastPrediction = prediction
  }

  return predictions
}


// Add watcher to fetch ML predictions when selected devices or rawData changes
watchEffect(async () => {
  if (selectedDevices.value.length > 0 && rawData.value.length > 0) {
    await fetchMLPredictions()
  }
})

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
  // Define the type for the accumulator
  const groupedByDay: Record<string, { count: number, totalMoisture: number }> = {};

  // Group data by day and calculate the average moisture for each day
  data.forEach(curr => {
    const date = new Date(curr.timestamp);
    const day = date.toISOString().split('T')[0]; // Extract the date in "YYYY-MM-DD" format
    
    // Initialize the day in the accumulator if not already present
    if (!groupedByDay[day]) {
      groupedByDay[day] = { count: 0, totalMoisture: 0 };
    }

    // Aggregate moisture for the day
    groupedByDay[day].count++;
    groupedByDay[day].totalMoisture += curr.moisture;
  });

  // Create labels (dates) and moisture values
  const labels = Object.keys(groupedByDay);
  const moistureData = labels.map(day => {
    const { totalMoisture, count } = groupedByDay[day];
    return totalMoisture / count; // Calculate the average moisture for the day
  });

  return {
    labels: labels, // Labels are the days
    datasets: [{
      label: label,
      data: moistureData, // Daily moisture values
      borderColor: chartPalette[idx % chartPalette.length],
      backgroundColor: chartPalette[idx % chartPalette.length] + '33', // Transparent background
      pointRadius: 4,
      pointBackgroundColor: chartPalette[idx % chartPalette.length],
      pointBorderColor: chartPalette[idx % chartPalette.length],
      tension: 0.3,
      fill: false  // No fill under the curve
    }]
  };
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
  const labels = [...Array(30)].map((_, i) => `Day ${i + 1}`);

  const datasets = selectedDevices.value.map((device, idx) => ({
    label: `${device} Forecast`,
    data: forecastValues.value[device],
    borderColor: chartPalette[idx % chartPalette.length],
    backgroundColor: chartPalette[idx % chartPalette.length] + '33',
    fill: true,
    pointRadius: (context: any) => {
      const pointId = `${context.datasetIndex}-${context.dataIndex}`;
      // Highlight clicked points
      if (clickedDataPoints.value.includes(pointId)) {
        return 6; // Larger size for clicked points
      }
      return 0; // Default radius for non-clicked points
    },
    pointBackgroundColor: (context: any) => {
      const pointId = `${context.datasetIndex}-${context.dataIndex}`;
      // Change color for clicked points
      if (clickedDataPoints.value.includes(pointId)) {
        return 'orange';
      }
      return 'rgba(255, 255, 255, 0.7)'; // Default color for non-clicked points
    },
    pointBorderColor: chartPalette[idx % chartPalette.length],
  }));

  const allVals = datasets.flatMap(ds => ds.data);
  const pad = 0.3;
  const yMin = Math.floor(Math.min(...allVals) - pad);
  const yMax = Math.ceil(Math.max(...allVals) + pad);

  return { labels, datasets, yMin, yMax };
});

const forecastOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  onClick: handleChartClick, // Attach the click handler
  scales: {
    y: {
      min: forecastChart.value.yMin,
      max: forecastChart.value.yMax,
      grid: {
        color: '#666666',
      },
      ticks: {
        callback: (v: any) => `${v}%`,
        color: '#ff8800',
        font: { size: 16, weight: 'bold' },
      },
      title: {
        display: true,
        text: 'Moisture (%)',
        color: '#ff8800',
        font: { size: 16, weight: 'bold' },
      },
    },
    x: {
      grid: {
        color: '#666666',
      },
      ticks: {
        color: '#ff8800',
        font: { size: 14, weight: 'bold' },
      },
      title: {
        display: true,
        text: 'Day',
        color: '#ff8800',
        font: { size: 14, weight: 'bold' },
      },
    },
  },
}));

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

const SELECTED_DEVICES_KEY = 'dashboard_live_plant_selected_devices'
onMounted(async () => {
  // Load saved devices from sessionstorage FIRST
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

  // Format last refresh time
  const now = new Date()
  const hours   = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const day     = String(now.getDate()).padStart(2, '0')
  const month   = String(now.getMonth() + 1).padStart(2, '0')
  const year    = now.getFullYear()
  lastRefresh.value = `${hours}:${minutes} ${day}/${month}/${year}`

  // Setup outside click detection for dropdown
  if (dropdownRef.value) {
    onClickOutside(dropdownRef, () => (isFilterDropdownOpen.value = false))
  }

  // Check if ML API is available (your existing code)
  const mlApiAvailable = await checkMLApiHealth()
  if (!mlApiAvailable) {
    console.warn('ML API is not available, falling back to simple forecasting')
  }
})

// Watch for device changes and initialize stats
watch(selectedDevices, () => {
  initializeStatsExpansion()
  initializePinnedStats()
}, { immediate: true })

// Watch for changes and save to localStorage
watch(selectedDevices, (newDevices) => {
  sessionStorage.setItem(SELECTED_DEVICES_KEY, JSON.stringify(newDevices))
}, { deep: true })


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
animation: fade-in 30s cubic-bezier(0.4,0,0.2,1);
}
/* Basic box-shadow and transition */
.orange-glow {
  box-shadow:
    0 2px 16px 0 #ea580c33,
    0 0 0 1.5px #fff2,
    0 1px 8px #0002;
  transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1), 
              transform 0.3s ease-in-out; /* Only transform will transition */
}

/* Hover state for enlargement and glow */
.orange-glow:hover {
  box-shadow:
    0 4px 32px 0 #ea580c66,
    0 0 0 2px #ea580c99,
    0 2px 16px #0004;
  transform: scale(1.1);  /* Immediately enlarge the element */
  transition-delay: 0s;   /* No delay for enlargement */
}

/* Non-hover state (when mouse leaves) */
.orange-glow:not(:hover) {
  transition-delay: 0s;   /* Keep the glow effect for 2s after hover */
  transform: scale(1);    /* Immediately shrink back */
}

/* For hover glow effect on a specific class */
.hover\:glow-orange:hover {
  box-shadow: 0 0 24px 0 rgba(255, 136, 0, 0.18), 0 0 2px 0 rgba(255, 136, 0, 0.12);
  transform: scale(1.1); /* Add the enlargement effect */
  transition-delay: 0s;  /* No delay for enlargement */
}

/* Non-hover state for hover glow */
.hover\:glow-orange:not(:hover) {
  transition-delay: 0s;  /* Keep the glow effect for 2s after hover */
  transform: scale(1);   /* Immediately shrink back */
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
/* Add to your existing styles */
.stats-container {
  transition: all 0.2s ease;
}

.cursor-move {
  cursor: move;
}

.stats-container.absolute {
  user-select: none;
}

/* Prevent text selection during drag */
.stats-container:active {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
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
</style>