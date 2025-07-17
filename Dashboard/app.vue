<template>
  <div class="flex flex-col lg:flex-row min-h-screen">
    <!-- Sidebar -->
    <aside
      class="hidden lg:flex
            w-full        /* 100% on mobile (hidden anyway) */
            lg:w-1/5      /* 20% of viewport on lg+ */
            h-screen flex-shrink-0
            flex-col gap-6 pt-6 pl-4 …"
    >
      <Sidebar/>
    </aside>

    <!-- Main content -->
    <main class="flex-1 container mx-auto p-4 md:p-6">
      <NuxtPage />
    </main>
  </div>
</template>

