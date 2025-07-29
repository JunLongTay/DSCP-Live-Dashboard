<template>
  <div class="relative min-h-screen">
    <!-- BG + overlay -->
    <img
      src="/home.jpg"
      alt="Background"
      class="fixed top-0 left-0 w-full h-full object-cover z-0 blur-md opacity-70 pointer-events-none select-none"
      onerror="this.style.display='none'"
    />
    <div class="fixed top-0 left-0 w-full h-full bg-black/80 z-10 pointer-events-none" />

    <!-- Sidebar -->
    <div class="fixed top-0 left-0 bottom-0 w-64 h-full z-30 border-r-2 border-orange-800 shadow-xl">
      <Sidebar />
    </div>

    <!-- Main Content -->
    <div class="min-h-screen relative z-20 flex flex-col px-6 md:px-12 py-8 ml-64">
      <!-- Header Row -->
      <div class="flex items-baseline gap-6 mb-2">
        <div class="flex items-center gap-4">
          <img src="/Logo.png" alt="Logo" class="h-16 w-16 object-contain" />
          <h1 class="text-3xl font-bold text-orange-400 font-roboto-slab">🌿 DSCP Dashboard</h1>
        </div>

        <!-- Controls -->
        <div class="flex gap-4 items-center ml-auto">
          <select v-model="chartType" class="border border-orange-500 rounded p-2 bg-zinc-900 text-orange-200">
            <option value="pie">Pie</option>
            <option value="bar">Bar</option>
            <option value="line">Line</option>
          </select>
          <ClientOnly>
            <button
              @click="exportDashboardToPDF"
              class="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-2 px-4 rounded transition-colors"
            >
              Export as PDF
            </button>
          </ClientOnly>
        </div>
      </div>

      <!-- Divider line below header -->
      <hr class="border-t border-orange-700 mb-4" />

      <!-- Status Message -->
      <section class="bg-zinc-900 p-4 rounded shadow border border-orange-300/20 mb-6">
        <p class="font-semibold text-green-400">🚀 Page loaded successfully!</p>
        <p class="text-sm mt-2 text-orange-200">This is your overview page. Data will appear here once it's loaded.</p>
      </section>

      <!-- Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <div class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-4 orange-glow">
          <p class="text-sm font-medium text-orange-300">🔌 Total Device Types</p>
          <p class="text-2xl font-bold text-orange-400 mt-1">{{ deviceTypeCount ?? '...' }}</p>
        </div>
        <div class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-4 orange-glow">
          <p class="text-sm font-medium text-orange-300">🧪 Total Sensors (+Current & Voltage)</p>
          <p class="text-2xl font-bold text-orange-400 mt-1">{{ sensorCount ?? '...' }}</p>
        </div>
        <div class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-4 orange-glow">
          <p class="text-sm font-medium text-orange-300">📍 Total Locations</p>
          <p class="text-2xl font-bold text-orange-400 mt-1">{{ locationCount ?? '...' }}</p>
        </div>
        <div class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-4 orange-glow">
          <p class="text-sm font-medium text-orange-300">👥 Total Users</p>
          <p class="text-2xl font-bold text-orange-400 mt-1">{{ userCount ?? '...' }}</p>
        </div>
        <div class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-4 orange-glow">
          <p class="text-sm font-medium text-orange-300">🖥️ Total Devices</p>
          <p class="text-2xl font-bold text-orange-400 mt-1">{{ deviceCount ?? '...' }}</p>
        </div>
        <div
          v-for="(count, loc) in filteredDevicesPerLocation"
          :key="loc"
          class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-4 orange-glow"
        >
          <p class="text-sm font-medium text-orange-300">🏢 {{ loc }}</p>
          <p class="text-2xl font-bold text-orange-400 mt-1">{{ count }} device{{ count > 1 ? 's' : '' }}</p>
        </div>
      </div>

      <!-- Charts -->
      <div class="flex flex-col lg:flex-row gap-6 mb-8">
        <!-- Pie/Bar Chart -->
        <section class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6 w-full lg:w-1/2 orange-glow">
          <h2 class="text-xl font-semibold mb-4 text-orange-400 text-center">Sensor Data Distribution</h2>
          <ClientOnly>
            <div v-if="loading" class="flex items-center justify-center h-64">
              <div class="text-orange-300">🔄 Loading sensor chart...</div>
            </div>
            <div v-else class="w-full h-64 flex flex-col items-center space-y-4">
              <component :is="chartTypeComponent" :data="sensorChartData" :options="sensorChartOptions" />
            </div>
          </ClientOnly>
        </section>

        <!-- Time-Series -->
        <section class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6 w-full lg:w-1/2 orange-glow">
          <h2 class="text-xl font-semibold mb-4 text-orange-400 text-center">Sensor Data Over Time</h2>
          <ClientOnly>
            <div v-if="loading" class="flex items-center justify-center h-64">
              <div class="text-orange-300">🔄 Loading time series chart...</div>
            </div>
            <div v-else class="w-full h-64">
              <Line :data="timeSeriesChartData" :options="timeSeriesChartOptions" />
            </div>
          </ClientOnly>
        </section>
      </div>

      <!-- Treemap -->
      <section class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6 mb-8 orange-glow">
        <h2 class="text-xl font-semibold mb-4 text-orange-400 text-center">Treemap of Devices by Location and Device Type</h2>
        <ClientOnly>
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="text-orange-300">Loading treemap...</div>
          </div>
          <div v-else class="w-full h-64">
            <VueApexCharts type="treemap" height="300" :options="treemapOptions" :series="treemapSeries" />
          </div>
        </ClientOnly>
      </section>

      <!-- User Contribution -->
      <section class="bg-zinc-900 border border-orange-300/20 rounded-xl shadow-xl p-6 orange-glow">
        <h2 class="text-xl font-semibold mb-4 text-orange-400 text-center">📊 Devices Contributed by Users</h2>
        <ClientOnly>
          <div v-if="loading" class="flex items-center justify-center h-64">
            <div class="text-orange-300">Loading user-device chart...</div>
          </div>
          <div v-else class="w-full h-64">
            <Bar :data="userDeviceChartData" :options="userDeviceChartOptions" />
          </div>
        </ClientOnly>
      </section>
    </div>
  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useNuxtApp } from '#app';
import Sidebar from '~/components/Sidebar/index.vue';
import * as d3 from 'd3';
import { Pie, Bar, Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title
} from 'chart.js';
import type { ChartData, ChartOptions } from 'chart.js';

import VueApexCharts from 'vue3-apexcharts';

// Type definitions
interface Location {
  locationid: string;
  locationname: string;
}

interface Device {
  deviceid: string;
  locationid: string;
  devicetypeid: string;
  userid: string;
}

interface DeviceType {
  devicetypeid: string;
  devicetypename: string;
}

interface SensorDataRow {
  sensorid: string;
  dbtimestamp: string;
  [key: string]: string;
}

interface User {
  userid: string;
  username: string;
}

interface DeviceDataRow {
  deviceid: string;
  dbtimestamp: string;
  [key: string]: string;
}

const { $html2pdf } = useNuxtApp();

const exportDashboardToPDF = async () => {
  await nextTick();
  const el = document.getElementById('dashboard-content');
  if (!el) return alert('Dashboard content not found');

  try {
    await $html2pdf(el);
  } catch (e) {
    console.error('PDF Export failed:', e);
    alert('Failed to export dashboard. Check console.');
  }
};

ChartJS.register(
  ArcElement,
  BarElement,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Title
);

const chartType = ref('pie');
const topOnly = ref(false);
const loading = ref(true);

const deviceTypeCount = ref(0);
const sensorCount = ref(0);
const locationCount = ref(0);
const userCount = ref(0);
const deviceCount = ref(0);

const devicesPerLocation = ref<Record<string, number>>({});
const rawGroupedData = ref<Record<string, number>>({});
const timeSeriesData = ref<Record<string, number>>({});

const sensorChartData = ref<ChartData<'pie' | 'bar' | 'line'>>({
  labels: [],
  datasets: []
});
const sensorChartOptions = ref<ChartOptions<'pie' | 'bar' | 'line'>>({});
const timeSeriesChartData = ref<ChartData<'line'>>({
  labels: [],
  datasets: []
});
const timeSeriesChartOptions = ref<ChartOptions<'line'>>({});
const userDeviceChartData = ref<ChartData<'bar'>>({
  labels: [],
  datasets: []
});
const userDeviceChartOptions = ref<ChartOptions<'bar'>>({});

const chartTypeComponent = computed(() => {
  switch (chartType.value) {
    case 'bar': return Bar;
    case 'line': return Line;
    default: return Pie;
  }
});

const treemapSeries = ref<Array<{ data: Array<{ x: string; y: number }> }>>([]);
const treemapOptions = ref({
  chart: {
    type: 'treemap',
    toolbar: { show: true },
    background: 'transparent'
  },
  legend: { show: false },
  plotOptions: {
    treemap: {
      enableShades: true,
      shadeIntensity: 0.6,
      useFillColorAsStroke: false,
      distributed: false,
      dataLabels: {
        enabled: true,
        style: {
          fontSize: '24px',
          fontWeight: 'bold',
          colors: ['#ffffff']
        },
        formatter: function (text: string, opts: any) {
          const label = text.split(':')[1] || text;
          const truncated = label.length > 25 ? label.slice(0, 25) + '…' : label;
          const value = opts?.w?.config?.series?.[opts.seriesIndex]?.data?.[opts.dataPointIndex]?.y;
          return value >= 2 ? truncated : '';
        }
      },
      colorScale: {
        ranges: [],
        inverseUniques: true,
        color: '#ea580c',
        min: undefined,
        max: undefined
      }
    }
  },
  colors: ['#ea580c'],
  fill: {
    type: 'gradient',
    gradient: {
      shade: 'light',
      type: 'vertical',
      gradientToColors: ['#f97316'],
      inverseColors: false,
      opacityFrom: 1,
      opacityTo: 1,
      stops: [0, 100]
    }
  },
  title: {
    text: undefined
  }
});

async function loadTreemapData() {
  const [devices, locations, devicetypes] = await Promise.all([
    d3.csv('/data/devices.csv') as Promise<Device[]>,
    d3.csv('/data/locations.csv') as Promise<Location[]>,
    d3.csv('/data/devicetypes.csv') as Promise<DeviceType[]>
  ]);

  const locationMap = Object.fromEntries(
    locations.map((loc: Location) => [loc.locationid, loc.locationname])
  );
  const typeMap = Object.fromEntries(
    devicetypes.map((dt: DeviceType) => [dt.devicetypeid, dt.devicetypename])
  );

  const groupCount: Record<string, number> = {};
  devices.forEach((device: Device) => {
    const loc = locationMap[device.locationid];
    const type = typeMap[device.devicetypeid];
    if (!loc || !type) return;
    const key = `${loc} > ${type}`;
    groupCount[key] = (groupCount[key] || 0) + 1;
  });

  treemapSeries.value = [
    {
      data: Object.entries(groupCount)
        .map(([name, value]) => ({ x: name, y: value }))
        .sort((a, b) => (b.y as number) - (a.y as number)) // 🔽 Sort from biggest to smallest
    }
  ];
}

const filteredDevicesPerLocation = computed(() => {
  return Object.fromEntries(
    Object.entries(devicesPerLocation.value).filter(([name]) =>
      name === 'Ngee Ann Polytechnic DS Composting Room'
    )
  );
});

function generateColors(count: number) {
  const base = [
    '#ea580c', '#f97316', '#fb923c', '#fdba74', '#fbbf24','#f59e0b',
    '#d97706', '#92400e', '#78350f', '#451a03', '#fed7aa', '#fde68a',
    '#fef3c7', '#fefce8', '#fef9c3', '#fef3c7', '#fbbf24', '#f59e0b',
    '#d97706', '#92400e'
  ];
  return Array.from({ length: count }, (_, i) => base[i % base.length]);
}

async function parseCSV(path: string, limit: number = 100): Promise<Record<string, string>[]> {
  const res = await fetch(path);
  const reader = res.body?.getReader();
  if (!reader) return [];

  const decoder = new TextDecoder('utf-8');
  let { value: chunk, done } = await reader.read();
  let csv = '';
  let rows: string[] = [];

  while (!done && rows.length <= limit + 1) {
    csv += decoder.decode(chunk, { stream: true });
    rows = csv.split('\n');
    ({ value: chunk, done } = await reader.read());
  }

  const headers = rows[0].split(',').map(h => h.trim());
  const bodyRows = rows.slice(1, limit + 1);

  return bodyRows.map(row => {
    const values = row.split(',').map(v => v.trim());
    const obj: Record<string, string> = {};
    headers.forEach((h, i) => {
      obj[h] = values[i];
    });
    return obj;
  });
}

function updateSensorChartData() {
  const entries = Object.entries(rawGroupedData.value);
  const sorted = entries.sort((a, b) => b[1] - a[1]);
  const limited = topOnly.value ? sorted.slice(0, 5) : sorted;

  const labels = limited.map(([id]) => `Sensor ${id}`);
  const values = limited.map(([, count]) => count);

  sensorChartData.value = {
    labels,
    datasets: [{
      label: 'Sensor Data Count',
      data: values,
      backgroundColor: generateColors(values.length),
      borderColor: '#ea580c',
      borderWidth: 2,
      tension: 0.3
    }]
  };

  sensorChartOptions.value = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Sensor Data Count',
        align: 'center',
        font: { size: 18, weight: 'bold' },
        color: '#ea580c',
        padding: { top: 10, bottom: 15 }
      },
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          boxWidth: 14,
          padding: 10,
          font: { size: 12 },
          color: '#fbbf24',
          usePointStyle: true
        }
      }
    },
    layout: {
      padding: { top: 10, bottom: 10 }
    },
    scales: chartType.value !== 'pie' ? {
      x: { 
        beginAtZero: true,
        ticks: { color: '#fbbf24' },
        grid: { color: '#374151' }
      },
      y: { 
        beginAtZero: true, 
        ticks: { precision: 0, color: '#fbbf24' },
        grid: { color: '#374151' }
      }
    } : undefined
  };
}

function buildTimeSeriesChartData() {
  const entries = Object.entries(timeSeriesData.value).sort();
  const labels = entries.map(([time]) => time);
  const values = entries.map(([, count]) => count);

  timeSeriesChartData.value = {
    labels,
    datasets: [{
      label: 'Sensor Data Entries by Time',
      data: values,
      fill: false,
      borderColor: '#ea580c',
      backgroundColor: '#f97316',
      tension: 0.3,
      pointBackgroundColor: '#ea580c',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 4
    }]
  };

  timeSeriesChartOptions.value = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'Sensor Data Count Over Time',
        font: { size: 18, weight: 'bold' },
        color: '#ea580c',
        align: 'start'
      },
      legend: {
        position: 'bottom',
        labels: { color: '#fbbf24' }
      }
    },
    scales: {
      x: {
        title: { display: true, text: 'Time (HH:MM)', color: '#fbbf24' },
        ticks: { color: '#fbbf24' },
        grid: { color: '#374151' }
      },
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Entries', color: '#fbbf24' },
        ticks: { color: '#fbbf24' },
        grid: { color: '#374151' }
      }
    }
  };
}

async function parseDeviceData(path: string) {
  const data = await d3.csv(path) as Promise<DeviceDataRow[]>;
  const countByTimestamp: Record<string, number> = {};

  (await data).forEach((row: DeviceDataRow) => {
    const time = row.dbtimestamp?.trim().slice(0, 5);
    if (time) {
      countByTimestamp[time] = (countByTimestamp[time] || 0) + 1;
    }
  });

  return countByTimestamp;
}

async function loadUserDeviceChart() {
    const [users, devices] = await Promise.all([
      d3.csv('/data/users.csv') as Promise<User[]>,
      d3.csv('/data/devices.csv') as Promise<Device[]>
    ]);
}

onMounted(async () => {
  const [sensorData, locationData, userData, deviceData] = await Promise.all([
    d3.csv('/data/sensors.csv') as Promise<any[]>,
    d3.csv('/data/locations.csv') as Promise<Location[]>,
    d3.csv('/data/users.csv') as Promise<User[]>,
    d3.csv('/data/devices.csv') as Promise<Device[]>
  ]);

  deviceTypeCount.value = new Set(deviceData.map((d: Device) => d.devicetypeid)).size;
  sensorCount.value = sensorData.length;
  locationCount.value = locationData.length;
  userCount.value = userData.length;
  deviceCount.value = deviceData.length;

  // Group sensor data for rawGroupedData
  const sensorCSV = await parseCSV('/data/sensordata.csv', 100);
  const grouped: Record<string, number> = {};
  sensorCSV.forEach((d: Record<string, string>) => {
    const id = d.sensorid?.trim();
    if (!id) return;
    grouped[id] = (grouped[id] || 0) + 1;
  });
  rawGroupedData.value = grouped;
  updateSensorChartData();

  // Devices per Location
  const locationMap: Record<string, number> = {};
  deviceData.forEach((d: Device) => {
    const locationId = d.locationid;
    const locationName = locationData.find((loc: Location) => loc.locationid === locationId)?.locationname || `ID ${locationId}`;
    locationMap[locationName] = (locationMap[locationName] || 0) + 1;
  });
  devicesPerLocation.value = locationMap;

  // Time series chart
  const dbCounts = await parseDeviceData('/data/devicedata.csv');
  timeSeriesData.value = dbCounts;
  buildTimeSeriesChartData();

  // User-Device Contribution Chart
  const users = userData;
  const devices = deviceData;
  const userMap = Object.fromEntries(users.map((u: User) => [u.userid, u.username]));
  const counts: Record<string, number> = {};

  devices.forEach((device: Device, i: number) => {
    const userIndex = i % users.length;
    const username = users[userIndex]?.username || `User ${userIndex + 1}`;
    counts[username] = (counts[username] || 0) + 1;
  });

  const labels = Object.keys(counts);
  const values = Object.values(counts);

  userDeviceChartData.value = {
    labels,
    datasets: [{
      label: 'Devices per User',
      data: values,
      backgroundColor: generateColors(values.length),
      borderColor: '#ea580c',
      borderWidth: 2
    }]
  };

  userDeviceChartOptions.value = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'User-Device Contribution',
        font: { size: 18 },
        color: '#ea580c'
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        title: { display: true, text: 'Device Count', color: '#fbbf24' },
        ticks: { color: '#fbbf24' },
        grid: { color: '#374151' }
      },
      y: {
        title: { display: true, text: 'Users', color: '#fbbf24' },
        ticks: { color: '#fbbf24' },
        grid: { color: '#374151' }
      }
    }
  };

  await loadTreemapData();
  await loadUserDeviceChart();

  loading.value = false;
});

watch([topOnly, chartType], updateSensorChartData);
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

.orange-glow {
  box-shadow:
    0 2px 16px 0 #ea580c33,
    0 0 0 1.5px #fff2,
    0 1px 8px #0002;
  transition: box-shadow 0.3s cubic-bezier(0.4,0,0.2,1);
}
.orange-glow:hover {
  box-shadow:
    0 4px 32px 0 #ea580c66,
    0 0 0 2px #ea580c99,
    0 2px 16px #0004;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: none; }
}
.animate-fade-in {
  animation: fade-in 0.8s cubic-bezier(0.4,0,0.2,1);
}
</style> 