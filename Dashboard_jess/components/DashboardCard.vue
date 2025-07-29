<template>
  <div class="rounded-lg bg-white p-4 shadow-md w-fit border border-gray-200">
    <p class="text-sm font-medium text-gray-700">{{ title }}</p>
    <p class="text-2xl font-bold text-gray-900 mt-1">{{ value ?? '...' }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number]
});
</script>
