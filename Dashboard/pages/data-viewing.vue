<template>
  <div class="relative min-h-screen w-full">
    <!-- Sidebar absolutely positioned, flush with all edges -->
    <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30">
      <Sidebar />
    </div>
    <!-- Main content, margin-left for sidebar -->
    <div class="ml-64 relative min-h-screen">
      <div class="container mx-auto p-6 bg-black min-h-screen animate-fade-in">
        <h1 class="text-2xl font-bold mb-4 text-orange-400">Database Sample Rows</h1>

        <div v-if="samples.length">
          <div v-for="(sample, index) in samples" :key="index" class="mb-8">
            <h2 class="text-lg font-semibold mb-2 text-orange-300">{{ sample.table }}</h2>
            <div class="overflow-x-auto rounded-lg shadow border border-orange-500 bg-zinc-900">
              <table class="min-w-full text-sm text-left">
                <thead class="bg-orange-900 text-orange-200">
                  <tr>
                    <th v-for="(col, i) in Object.keys(sample.rows[0] || {})" :key="i" class="px-4 py-2 border-b border-orange-700">
                      {{ col }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rIndex) in sample.rows" :key="rIndex" class="border-t border-orange-800 transition-colors duration-200 hover:bg-orange-950/60">
                    <td v-for="(val, cIndex) in Object.values(row)" :key="cIndex" class="px-4 py-2 text-orange-100">
                      {{ val }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <p v-else class="text-orange-400 animate-pulse">Loading table samples...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from '../components/Sidebar/index.vue'
import { ref, onMounted } from 'vue';

const samples = ref([]);

onMounted(async () => {
  const res = await fetch('http://localhost:3001/table-samples');
  samples.value = await res.json();
});
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
</style>
