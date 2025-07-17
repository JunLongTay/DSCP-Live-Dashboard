<template>
  <!-- Sidebar container, only visible on large screens and up -->
  <aside
    class="hidden lg:flex w-64 h-screen flex-col gap-6
           pt-6 pl-4 text-xs font-normal
           border-r border-neutral-200 dark:border-neutral-700
           bg-white dark:bg-zinc-900"
  >
    <!-- Header with logo and title -->
    <header
      class="flex items-center gap-3 px-2 py-1 w-fit
             rounded-lg cursor-pointer transition
             hover:scale-[1.02]"
    >
      <Logo class="w-[45px]" />
      <span class="text-sm font-bold tracking-wide">
        DSCP&nbsp;Dashboard
      </span>
    </header>

    <!-- Navigation links -->
    <nav class="flex flex-col gap-2">
      <NuxtLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="group relative inline-flex items-center w-fit px-3 py-1 gap-2
               rounded-md cursor-pointer transition-colors hover:bg-neutral-100
               dark:hover:bg-zinc-800"
        active-class="text-primary-600"
        exact-active-class="text-primary-600"
      >
        <!-- Active indicator -->
        <span
          class="pointer-events-none absolute left-0 top-0 h-full w-1 bg-primary-600
                 translate-x-full group-hover:translate-x-0
                 group-[.router-link-active]:translate-x-0
                 transition-transform duration-300 ease-out"
        />
        <!-- Icon -->
        <Icon :name="item.icon" class="h-4 w-4 shrink-0" />
        <!-- Label -->
        <span class="relative z-10">{{ item.label }}</span>
      </NuxtLink>
    </nav>

    <!-- Optional footer block -->
    <!-- <footer class="mt-auto px-4 py-2 text-xs text-gray-400">Footer content</footer> -->
  </aside>
</template>

<script setup lang="ts">
interface Item {
  label: string
  to: string
  icon: string
}

/* Sidebar menu items with routes and icons */
const items: Item[] = [
  { label: 'Overview',           to: '/',             icon: 'lucide:home' },
  { label: 'Live Plant Dashboard', to: '/live-plant', icon: 'lucide:leaf' },
  { label: 'DataBased Sample',            to: '/data-viewing',      icon: 'lucide:user-circle' },
  { label: 'Contacts',           to: '/contacts',     icon: 'lucide:book' },
  { label: 'Settings',           to: '/settings',     icon: 'lucide:settings' }
]
</script>