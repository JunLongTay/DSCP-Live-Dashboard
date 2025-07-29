// ml-config.js - Configuration file for ML integration

export const ML_CONFIG = {
  // Flask ML API URL
  API_BASE_URL: 'http://localhost:5000',
  
  // API endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    PREDICT_SINGLE: '/predict/moisture',
    PREDICT_BATCH: '/predict/moisture/batch',
    MODEL_INFO: '/model/info'
  },
  
  // Forecast settings
  FORECAST_DAYS: 30,
  RECENT_DATA_POINTS: 50, // Number of recent readings to send to ML model
  
  // Fallback settings
  ENABLE_FALLBACK: true,
  FALLBACK_METHOD: 'linear_regression',
  
  // Feature mapping - map your Vue data structure to ML model features
  FEATURE_MAPPING: {
    'devicetimestamp': 'timestamp',
    'Soil Moisture': 'moisture',
    'temperature': 'temperature',
    'Soil Nitrogen': 'npk_n',
    'Soil Phosphorus': 'npk_p',
    'Soil Potassium': 'npk_k',
    'CO2': 'co2'
  }
}

// Helper function to transform Vue data to ML API format
export function transformDataForML(vueData) {
  return vueData.map(item => {
    const transformed = {}
    
    // Map Vue.js data structure to ML model expected format
    transformed.devicetimestamp = item.timestamp
    transformed.devicename = item.devicename
    transformed['Soil Moisture'] = item.moisture
    if ('temperature' in item) transformed.temperature = item.temperature
    if ('npk_n' in item) transformed.npk_n = item.npk_n
    if ('npk_p' in item) transformed.npk_p = item.npk_p
    if ('npk_k' in item) transformed.npk_k = item.npk_k
    if ('co2' in item) transformed.co2 = item.co2

    // Add time-based features that your ML model might expect
    const date = new Date(item.timestamp)
    transformed.hour = date.getHours()
    transformed.weekday = date.getDay()
    transformed.month = date.getMonth() + 1
    transformed.day_of_year = Math.floor((date - new Date(date.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24))
    return transformed
  })
}

// ML API service class
export class MLApiService {
  constructor(baseUrl = ML_CONFIG.API_BASE_URL) {
    this.baseUrl = baseUrl
  }
  
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.HEALTH}`)
      return await response.json()
    } catch (error) {
      console.error('ML API health check failed:', error)
      return { status: 'error', model_loaded: false }
    }
  }
  
  async getModelInfo() {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.MODEL_INFO}`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get model info:', error)
      return null
    }
  }
  
  async predictBatch(devicesData, daysAhead = ML_CONFIG.FORECAST_DAYS) {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.PREDICT_BATCH}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          devices: devicesData,
          days_ahead: daysAhead
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Batch prediction failed:', error)
      throw error
    }
  }
  
  async predictSingle(deviceName, recentData, daysAhead = ML_CONFIG.FORECAST_DAYS) {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.PREDICT_SINGLE}/${deviceName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recent_data: recentData,
          days_ahead: daysAhead
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error(`Single prediction failed for ${deviceName}:`, error)
      throw error
    }
  }
}