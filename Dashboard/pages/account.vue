<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Database Sample Rows</h1>

    <div v-if="samples.length">
      <div v-for="(sample, index) in samples" :key="index" class="mb-8">
        <h2 class="text-lg font-semibold mb-2">{{ sample.table }}</h2>
        <div class="overflow-x-auto rounded-lg shadow border border-gray-200">
          <table class="min-w-full text-sm text-left">
            <thead class="bg-gray-100 text-gray-700">
              <tr>
                <th v-for="(col, i) in Object.keys(sample.rows[0] || {})" :key="i" class="px-4 py-2 border-b">
                  {{ col }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rIndex) in sample.rows" :key="rIndex" class="border-t">
                <td v-for="(val, cIndex) in Object.values(row)" :key="cIndex" class="px-4 py-2">
                  {{ val }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <p v-else class="text-gray-500">Loading table samples...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const samples = ref([]);

onMounted(async () => {
  const res = await fetch('http://localhost:3001/table-samples');
  samples.value = await res.json();
});
</script>
