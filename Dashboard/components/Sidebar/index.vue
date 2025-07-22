<template>
  <!-- Sidebar container, only visible on large screens and up -->
  <aside
    class="hidden lg:flex w-64 h-screen flex-col
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
      <img src="/logo.webp" alt="Cute Plant Bot Logo" class="w-16 h-16 object-contain mt-2" />
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
  position: relative;
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
</style>