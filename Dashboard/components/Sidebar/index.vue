<template>
  <!-- Sidebar container, only visible on large screens and up -->
  <aside
    class="relative hidden lg:flex w-64 h-screen flex-col
          pt-6 pl-4 text-xs font-normal
          border-r border-orange-700
          sidebar-bg animate-fade-in"
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
          <span class="font-bold flex items-center gap-1" style="color: #22c55e;">
            <span class="inline-block w-2 h-2 rounded-full bg-green-400"></span>
            Online
          </span>
        </div>
        <div class="flex items-center justify-between py-1">
          <span>Last Update</span>
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

    <!-- Footer block with logo.webp at the bottom -->
    <footer class="mt-auto px-4 py-3 text-xs text-orange-700 border-t border-orange-900 flex flex-col gap-2 items-center">
      <span>v1.0.0</span>
      <NuxtLink to="/about" class="hover:underline text-orange-500">Help / About</NuxtLink>
      <img src="/logo.webp" alt="Cute Plant Bot Logo" class="w-16 h-16 mt-2" />
    </footer>
  </aside>
</template>

<script setup lang="ts">
import logoPng from '@/assets/Logo.png'

interface Item {
  label: string
  to: string
  icon: string
}

/* Sidebar menu items with routes and icons */
const items: Item[] = [
  { label: 'Overview',           to: '/',             icon: 'lucide:home' },
  { label: 'Live Plant Dashboard', to: '/live-plant', icon: 'lucide:leaf' },
  { label: 'Data tables',            to: '/data-viewing',      icon: 'lucide:user-circle' },
]

// System Status logic (dummy data, replace with real API if needed)
import { ref, computed } from 'vue'

// Example: device count from parent/dashboard (replace with prop or inject if needed)
const deviceCount = ref(12) // Replace with actual device count

// Example: database online status (always online for now)
const dbOnline = ref(true)

// Example: last update timestamp (replace with actual value)
const lastUpdate = ref(new Date())

function getRelativeTime(date: Date) {
  if (!date) return '—'
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '0m ago'
  if (diffMin < 60) return `${diffMin}m ago`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr}h ago`
  return date.toLocaleString()
}

const lastUpdateRelative = computed(() => getRelativeTime(lastUpdate.value))
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
/* Subtle sidebar background gradient and pattern */
.sidebar-bg {
  background: linear-gradient(135deg, #181818 80%, #ff88001a 100%);
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