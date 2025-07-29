<template>
  <aside
    class="hidden lg:flex
           w-64
           h-screen flex-col gap-6
           pt-6 pl-3
           text-xs font-normal
           bg-zinc-900"
  >
    <!-- header -------------------------------------------------------- -->
    <header
      class="flex items-center gap-2
             px-2 py-1 w-fit
             rounded-lg cursor-pointer transition
             hover:scale-[1.02]"
    >
      <Logo class="w-[45px]" />
      <span class="text-sm font-bold tracking-wide text-orange-400">
        DSCP&nbsp;Dashboard
      </span>
    </header>

    <!-- nav ----------------------------------------------------------- -->
    <nav class="flex flex-col gap-1">
      <NuxtLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="group relative inline-flex items-center w-fit px-2 py-1 gap-1
               rounded-md cursor-pointer transition-colors hover:bg-orange-800/20
               text-orange-200 hover:text-orange-300"
        active-class="text-orange-400"
        exact-active-class="text-orange-400"
      >
        <span
          class="pointer-events-none absolute left-0 top-0 h-full w-1 bg-orange-500
                 translate-x-full group-hover:translate-x-0
                 group-[.router-link-active]:translate-x-0
                 transition-transform duration-300 ease-out"
        />
        <Icon :name="item.icon" class="h-4 w-4 shrink-0" />
        <span class="relative z-10">{{ item.label }}</span>
      </NuxtLink>
    </nav>
  </aside>
</template>


<script setup lang="ts">
interface Item {
  label: string
  to: string
  icon: string
}

/* Icon names can come from any Iconify set that nuxt-icon supports */
const items: Item[] = [
  { label: 'Overview',     to: '/',             icon: 'lucide:home' },
  { label: 'Historical Dashboard', to: '/historical-dashboard', icon: 'lucide:bar-chart' }
]
</script>
