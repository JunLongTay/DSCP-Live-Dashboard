import { defineStore } from 'pinia'

export const useFilterStore = defineStore('filters', {
  state: () => ({
    selectedDevices: [],
    searchQuery: '',
    expandedLocations: [],
    isFilterDropdownOpen: false,
  }),
  
  actions: {
    setSelectedDevices(devices) {
      this.selectedDevices = devices
    },
    
    setSearchQuery(query) {
      this.searchQuery = query
    },
    
    setExpandedLocations(locations) {
      this.expandedLocations = locations
    },
    
    toggleDevice(device) {
      const index = this.selectedDevices.indexOf(device)
      if (index > -1) {
        this.selectedDevices.splice(index, 1)
      } else {
        this.selectedDevices.push(device)
      }
    },
    
    selectAllDevices(allDevices) {
      this.selectedDevices = [...allDevices]
    },
    
    clearAllDevices() {
      this.selectedDevices = []
    },
    
    // Persist to localStorage
    saveToLocalStorage() {
      localStorage.setItem('dashboard-filters', JSON.stringify({
        selectedDevices: this.selectedDevices,
        searchQuery: this.searchQuery,
        expandedLocations: this.expandedLocations
      }))
    },
    
    // Load from localStorage
    loadFromLocalStorage() {
      const saved = localStorage.getItem('dashboard-filters')
      if (saved) {
        const data = JSON.parse(saved)
        this.selectedDevices = data.selectedDevices || []
        this.searchQuery = data.searchQuery || ''
        this.expandedLocations = data.expandedLocations || []
      }
    }
  },
  
  // Auto-persist whenever state changes
  persist: true // if using pinia-plugin-persistedstate
})