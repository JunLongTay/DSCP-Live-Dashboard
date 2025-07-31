// ml-config.js - Updated configuration file for ML integration

export const ML_CONFIG = {
  // Flask ML API URL
  API_BASE_URL: 'http://localhost:5000',
  
  // API endpoints - FIXED to match Flask API
  ENDPOINTS: {
    HEALTH: '/health',
    PREDICT_SINGLE: '/predict/moisture/single',  // FIXED: was '/predict/moisture'
    PREDICT_BATCH: '/predict/moisture/batch',
    MODEL_INFO: '/model/info',
    MODEL_STATS: '/model/stats',  // NEW: additional endpoint
    RETRAIN: '/retrain'  // NEW: retrain endpoint
  },
  
  // Forecast settings
  FORECAST_DAYS: 30,
  RECENT_DATA_POINTS: 100, // Increased - ML models need more data points
  
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
    
    // FIXED: Use consistent moisture field name
    if (item.moisture !== undefined) {
      transformed['Soil Moisture'] = item.moisture
    } else if (item['Soil Moisture'] !== undefined) {
      transformed['Soil Moisture'] = item['Soil Moisture']
    }
    
    // Optional sensor data - only include if present
    if (item.temperature !== undefined) transformed.temperature = item.temperature
    if (item.npk_n !== undefined) transformed.npk_n = item.npk_n
    if (item.npk_p !== undefined) transformed.npk_p = item.npk_p
    if (item.npk_k !== undefined) transformed.npk_k = item.npk_k
    if (item.co2 !== undefined) transformed.co2 = item.co2
    
    // Handle different NPK field names your Vue app might use
    if (item['Soil Nitrogen'] !== undefined) transformed.npk_n = item['Soil Nitrogen']
    if (item['Soil Phosphorus'] !== undefined) transformed.npk_p = item['Soil Phosphorus']
    if (item['Soil Potassium'] !== undefined) transformed.npk_k = item['Soil Potassium']

    // Time-based features (Flask API will generate these, but including for completeness)
    const date = new Date(item.timestamp)
    transformed.hour = date.getHours()
    transformed.weekday = date.getDay()
    transformed.month = date.getMonth() + 1
    transformed.day_of_year = Math.floor((date - new Date(date.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24))
    
    return transformed
  })
}

// UPDATED: ML API service class with correct endpoints
export class MLApiService {
  constructor(baseUrl = ML_CONFIG.API_BASE_URL) {
    this.baseUrl = baseUrl
  }
  
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.HEALTH}`)
      const data = await response.json()
      console.log('ML API Health:', data)
      return data
    } catch (error) {
      console.error('ML API health check failed:', error)
      return { status: 'error', model_loaded: false }
    }
  }
  
  async getModelInfo() {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.MODEL_INFO}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      console.log('Model Info:', data)
      return data
    } catch (error) {
      console.error('Failed to get model info:', error)
      return null
    }
  }
  
  async getModelStats() {
    try {
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.MODEL_STATS}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Failed to get model stats:', error)
      return null
    }
  }
  
  // FIXED: Batch prediction with correct data format
  async predictBatch(devicesData, daysAhead = ML_CONFIG.FORECAST_DAYS) {
    try {
      console.log('Sending batch prediction request:', { devices: Object.keys(devicesData), daysAhead })
      
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
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const result = await response.json()
      console.log('Batch prediction result:', result)
      return result
      
    } catch (error) {
      console.error('Batch prediction failed:', error)
      throw error
    }
  }
  
  // FIXED: Single prediction with correct endpoint and data format
  async predictSingle(deviceName, recentData, daysAhead = ML_CONFIG.FORECAST_DAYS) {
    try {
      console.log(`Sending single prediction for ${deviceName}, data points: ${recentData.length}`)
      
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.PREDICT_SINGLE}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_name: deviceName,
          recent_data: recentData,
          days_ahead: daysAhead
        })
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const result = await response.json()
      console.log(`Single prediction result for ${deviceName}:`, result)
      return result
      
    } catch (error) {
      console.error(`Single prediction failed for ${deviceName}:`, error)
      throw error
    }
  }
  
  // NEW: Trigger model retraining
  async retrain() {
    try {
      console.log('Triggering model retraining...')
      
      const response = await fetch(`${this.baseUrl}${ML_CONFIG.ENDPOINTS.RETRAIN}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const result = await response.json()
      console.log('Retrain result:', result)
      return result
      
    } catch (error) {
      console.error('Model retraining failed:', error)
      throw error
    }
  }
}

// HELPER: Prepare device data for batch prediction
export function prepareDevicesForBatchPrediction(devicesData) {
  const prepared = {}
  
  for (const [deviceName, deviceReadings] of Object.entries(devicesData)) {
    // Transform the readings for ML API
    const transformedData = transformDataForML(deviceReadings)
    
    // Take the most recent N data points
    const recentData = transformedData
      .sort((a, b) => new Date(b.devicetimestamp) - new Date(a.devicetimestamp))
      .slice(0, ML_CONFIG.RECENT_DATA_POINTS)
    
    prepared[deviceName] = {
      recent_data: recentData
    }
  }
  
  return prepared
}

// HELPER: Simple linear regression fallback (if ML API is down)
export function linearRegressionFallback(data, daysAhead = 30) {
  if (!data || data.length < 2) {
    return []
  }
  
  // Sort by timestamp
  const sortedData = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  
  // Simple linear regression on moisture values
  const n = sortedData.length
  let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0
  
  sortedData.forEach((point, index) => {
    const x = index
    const y = point.moisture || point['Soil Moisture'] || 0
    sumX += x
    sumY += y
    sumXY += x * y
    sumXX += x * x
  })
  
  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
  const intercept = (sumY - slope * sumX) / n
  
  // Generate predictions
  const lastDate = new Date(sortedData[sortedData.length - 1].timestamp)
  const predictions = []
  
  for (let day = 1; day <= daysAhead; day++) {
    const futureValue = slope * (n + day - 1) + intercept
    const futureDate = new Date(lastDate)
    futureDate.setDate(futureDate.getDate() + day)
    
    predictions.push({
      day: day,
      date: futureDate.toISOString(),
      predicted_moisture: Math.max(0, Math.min(100, futureValue.toFixed(2)))
    })
  }
  
  return predictions
}