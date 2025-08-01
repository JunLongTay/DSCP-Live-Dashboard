<template>
  <!-- Sidebar container, only visible on large screens and up -->
  <aside
    class="relative hidden lg:flex w-64 h-screen flex-col
          pt-6 pl-4 text-xs font-normal
          border-r border-orange-700
          sidebar-bg"
  >
    <!-- Logo.png at the very top -->
    <div class="flex flex-col items-center mb-2">
      <img :src="logoPng" alt="Logo" class="w-20 h-20 object-contain mb-2 drop-shadow-lg" />
      <span class="text-lg font-bold tracking-wide text-orange-400">
        DSCP&nbsp;Dashboard
      </span>
    </div>

    <!-- System Status Box -->
    <div class="w-full px-2 mb-2">
      <div
        class="system-status-box bg-transparent rounded-lg shadow-md px-4 py-3 text-xs font-inter"
        style="border: 2px solid #ff8800; opacity: 0.75; color: #ff8800;"
      >
        <div class="flex items-center gap-2 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: #ff8800;">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M12 20h.01M4 4h16v16H4V4z" />
          </svg>
          <span class="font-semibold">System Status</span>
        </div>
        <div class="flex items-center justify-between py-1">
          <span>Devices</span>
          <span class="font-bold">{{ deviceCount }}</span>
        </div>
        <div class="flex items-center justify-between py-1">
          <span>Online</span>
          <span class="font-bold flex items-center gap-1" 
                :class="isBackendOnline ? 'text-green-400' : 'text-red-400'">
            <span class="inline-block w-2 h-2 rounded-full" 
                  :class="isBackendOnline ? 'bg-green-400' : 'bg-red-400'"></span>
            {{ isBackendOnline ? 'Online' : 'Offline' }}
          </span>
        </div>
        <div class="flex items-center justify-between py-1">
          <span>Last Data Refresh</span>
          <span class="font-bold">{{ lastUpdateRelative }}</span>
        </div>
      </div>
    </div>

    <!-- Navigation links -->
    <nav class="flex flex-col gap-3 mt-4">
      <NuxtLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="group relative inline-flex items-center w-fit px-5 py-3 gap-3
               rounded-lg cursor-pointer transition-colors duration-200
               hover:bg-orange-900 hover:text-orange-300 text-orange-100 text-base font-semibold"
        active-class="text-orange-400 bg-orange-950"
        exact-active-class="text-orange-400 bg-orange-950"
      >
        <!-- Active indicator -->
        <span
          class="pointer-events-none absolute left-0 top-0 h-full w-1 bg-orange-500
                 translate-x-full group-hover:translate-x-0
                 group-[.router-link-active]:translate-x-0
                 transition-transform duration-300 ease-out"
        />
        <!-- Icon -->
        <Icon :name="item.icon" class="h-6 w-6 shrink-0 text-orange-300 group-hover:text-orange-400 transition-colors duration-200" />
        <!-- Label -->
        <span class="relative z-10">{{ item.label }}</span>
      </NuxtLink>
    </nav>

    <!-- Refresh Button -->
    <div class="px-4 py-0 mt-auto">
      <button 
        @click="refreshPage"
        class="w-full flex items-center justify-center gap-2 px-4 py-2 
               bg-orange-900/50 hover:bg-orange-800/70 
               border border-orange-700 hover:border-orange-600
               rounded-lg text-orange-300 hover:text-orange-200 
               text-sm font-medium transition-all duration-200 cursor-pointer"
      >
        <Icon name="lucide:refresh-cw" class="h-4 w-4" />
        <span>Refresh Data</span>
      </button>
    </div>

    <!-- Footer block with logo.webp at the bottom -->
    <footer class="mt-auto px-4 py-3 text-xs text-orange-700 border-t border-orange-900 flex flex-col gap-2 items-center">
      <span>v1.0.0</span>
      <img src="/logo.webp" alt="Cute Plant Bot Logo" class="w-16 h-16 mt-2" />
    </footer>
  </aside>
</template>

<script setup lang="ts">
import logoPng from '@/assets/Logo.png'
import { onMounted, onUnmounted } from 'vue'

interface Item {
  label: string
  to: string
  icon: string
}

// Backend connectivity status
const isBackendOnline = ref(true)
let connectivityInterval: NodeJS.Timeout | null = null

/* Sidebar menu items with routes and icons */
const items: Item[] = [
  { label: 'Overview',           to: '/',             icon: 'lucide:home' },
  { label: 'Live Plant Dashboard', to: '/live-plant', icon: 'lucide:leaf' },
  { label: 'Historical Dashboard',            to: '/historical-dashboard',      icon: 'lucide:user-circle' },
]

// System Status logic (dummy data, replace with real API if needed)
import { ref, computed } from 'vue'

// Example: device count from parent/dashboard (replace with prop or inject if needed)
const deviceCount = ref(0) // Replace with actual device count

// Example: database online status (always online for now)
const dbOnline = ref(true)

// Example: last update timestamp (replace with actual value)
const lastUpdate = ref(new Date())

// Add a reactive timer to force updates
const currentTime = ref(new Date())
let timeInterval: NodeJS.Timeout | null = null

function getRelativeTime(date: Date) {
  if (!date) return '—'
  const now = currentTime.value // Use reactive current time instead of new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '0m ago'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  return date.toLocaleString()
}

// Function to check backend connectivity
async function checkBackendStatus() {
  try {
    // Use the health endpoint that exists in your backend
    const response = await fetch('http://localhost:3001/health', {
      method: 'GET',
    })
    
    if (response.ok) {
      isBackendOnline.value = true
    } else {
      isBackendOnline.value = false
    }
  } catch (error) {
    // If fetch fails (network error, timeout, etc.)
    isBackendOnline.value = false
    console.warn('Backend connectivity check failed:', error)
  }
}

// Function to fetch device count from backend
async function fetchDeviceCount() {
  try {
    // Fetch the list of devices from your backend
    const response = await fetch('http://localhost:3001/np-devices', {
      method: 'GET',
    })
    
    if (response.ok) {
      const devices = await response.json()
      // Update device count with the actual number from backend
      deviceCount.value = Array.isArray(devices) ? devices.length : 0
    } else {
      console.warn('Failed to fetch devices, status:', response.status)
      deviceCount.value = 0
    }
  } catch (error) {
    console.warn('Failed to fetch device count:', error)
    deviceCount.value = 0
  }
}

function refreshPage() {
  // Update the last refresh time
  lastUpdate.value = new Date()
  sessionStorage.setItem('last-data-refresh', new Date().toISOString())
  
  // Dispatch event to notify other components
  window.dispatchEvent(new CustomEvent('refresh-dashboard-data'))
  
  // Reload the page
  window.location.reload()
}

// Check if sidebar animation has already been shown
const hasAnimated = ref(false)

onMounted(() => {
  // Check if animation has been shown in this session
  const animationShown = sessionStorage.getItem('sidebar-animated')
  if (animationShown) {
    hasAnimated.value = true
  } else {
    // Mark as animated and store in session
    sessionStorage.setItem('sidebar-animated', 'true')
    hasAnimated.value = false
  }
  
  // Load last refresh time from storage or set to current time
  const lastRefresh = sessionStorage.getItem('last-data-refresh')
  if (lastRefresh) {
    lastUpdate.value = new Date(lastRefresh)
  } else {
    // First time loading, set current time as last refresh
    lastUpdate.value = new Date()
    sessionStorage.setItem('last-data-refresh', new Date().toISOString())
  }
  // Start connectivity checking
  checkBackendStatus() // Initial check
  fetchDeviceCount()   // Fetch initial device count
  // Start periodic checks
  connectivityInterval = setInterval(() => {
    checkBackendStatus() // Check backend every 30 seconds
    fetchDeviceCount()   // Update device count every 30 seconds
  }, 30000)

  // Start time interval for relative time updates
  timeInterval = setInterval(() => {
    currentTime.value = new Date()
  }, 60000) // Update every 60 seconds
})

onUnmounted(() => {
  // Clean up the intervals when component is destroyed
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  if (connectivityInterval) {
    clearInterval(connectivityInterval)
  }
})

const lastUpdateRelative = computed(() => getRelativeTime(lastUpdate.value))
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: none; }
}

/* Subtle sidebar background gradient and pattern */
.sidebar-bg {
  background: linear-gradient(135deg, #181818 80%, #ff88001a 100%);
  /* Only animate on first load */
  animation: v-bind('hasAnimated ? "none" : "fade-in 0.6s ease-out"');
}
.sidebar-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.08;
  background-image: repeating-linear-gradient(135deg, #ff8800 0 2px, transparent 2px 24px);
  pointer-events: none;
  z-index: 0;
}
.system-status-box {
  /* Transparent background, orange outline set inline */
  margin-bottom: 0.5rem;
}
.font-inter {
  font-family: 'Inter', Arial, sans-serif;
}
</style>