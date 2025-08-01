import pickle
import pandas as pd
import numpy as np
from prophet import Prophet
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Soil Health ML API", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
def get_status():
    return {
        "connected": True,
        "message": "API is working ✅"
    }

# Global variables for models and data
prophet_model = None
hw_model = None
historical_df = None


# Pydantic models for request/response
class ForecastRequest(BaseModel):
    forecast_days: int = 90
    historical_data: Optional[List[Dict[str, Any]]] = None

class ForecastPoint(BaseModel):
    ds: str  # date string
    yhat: float  # predicted value
    yhat_lower: float  # confidence interval lower bound
    yhat_upper: float  # confidence interval upper bound

class ForecastResponse(BaseModel):
    forecast: List[ForecastPoint]
    model_type: str
    forecast_days: int
    generated_at: str
    data_points_used: int

def load_historical_data():
    """Load the df_wide.csv file that contains your historical data"""
    global historical_df
    
    try:
        # Look for the CSV file in common locations
        possible_paths = [
            'ml/jess/df_wide.csv',
            'ML/jess/df_wide.csv',
            'df_wide.csv',
            '../ml/jess/df_wide.csv',
            'jess/df_wide.csv'
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if csv_path is None:
            raise FileNotFoundError("df_wide.csv not found in expected locations")
        
        historical_df = pd.read_csv(csv_path)
        
        # Clean and standardize the data
        if 'dbtimestamp' in historical_df.columns:
            historical_df['dbtimestamp'] = pd.to_datetime(historical_df['dbtimestamp'])
        
        # Ensure numeric columns are properly typed
        numeric_columns = ['soil_moisture', 'soil_ph', 'soil_ec', 'soil_nitrogen', 'soil_phosphorus']
        for col in numeric_columns:
            if col in historical_df.columns:
                historical_df[col] = pd.to_numeric(historical_df[col], errors='coerce')
        
        # Remove rows with all NaN values
        historical_df = historical_df.dropna(how='all')
        
        logger.info(f"Loaded historical data from {csv_path}: {len(historical_df)} rows")
        logger.info(f"Date range: {historical_df['dbtimestamp'].min()} to {historical_df['dbtimestamp'].max()}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load historical data: {e}")
        historical_df = None
        return False

def load_models():
    """Load your trained ML models"""
    global prophet_model, hw_model
    
    # Load Prophet soil moisture model
    try:
        prophet_path = 'ml/prophet_soil_moisture_model.pkl'
        if not os.path.exists(prophet_path):
            prophet_path = 'prophet_soil_moisture_model.pkl'
        
        with open(prophet_path, 'rb') as f:
            prophet_model = pickle.load(f)
        logger.info("Prophet soil moisture model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Prophet model: {e}")
        prophet_model = None

    # Load Holt-Winters EC model
    try:
        hw_path = 'ml/hw11_sensor11_model.pkl'
        if not os.path.exists(hw_path):
            hw_path = 'hw11_sensor11_model.pkl'
            
        with open(hw_path, 'rb') as f:
            hw_model = pickle.load(f)
        logger.info("Holt-Winters EC model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Holt-Winters model: {e}")
        hw_model = None

@app.on_event("startup")
async def startup_event():
    """Load models and data on startup"""
    logger.info("Starting Soil Health ML API...")
    
    # Load historical data
    data_loaded = load_historical_data()
    
    # Load ML models
    load_models()
    
    if not data_loaded:
        logger.warning("Historical data not loaded - API will use sample data")
    
    if prophet_model is None and hw_model is None:
        logger.warning("No ML models loaded - API will use fallback forecasting")

def prepare_data_for_prophet(data_source: str = "historical") -> pd.DataFrame:
    """Prepare data for Prophet forecasting from your df_wide.csv"""
    try:
        if data_source == "historical" and historical_df is not None:
            df = historical_df.copy()
        else:
            # Use provided data or generate sample data
            logger.warning("Using sample data for Prophet")
            dates = pd.date_range(start='2025-01-01', periods=200, freq='6H')
            df = pd.DataFrame({
                'dbtimestamp': dates,
                'soil_moisture': 45 + np.random.normal(0, 10, 200) + 15 * np.sin(np.arange(200) * 0.1)
            })
        
        # Prepare for Prophet (needs 'ds' and 'y' columns)
        prophet_df = pd.DataFrame()
        prophet_df['ds'] = df['dbtimestamp']
        prophet_df['y'] = df['soil_moisture']
        
        # Remove any rows with NaN values
        prophet_df = prophet_df.dropna()
        
        # Ensure moisture values are within reasonable bounds (0-100%)
        prophet_df['y'] = prophet_df['y'].clip(0, 100)
        
        logger.info(f"Prepared {len(prophet_df)} data points for Prophet")
        return prophet_df
        
    except Exception as e:
        logger.error(f"Error preparing data for Prophet: {e}")
        raise

def prepare_data_for_hw(data_source: str = "historical") -> np.ndarray:
    """Prepare data for Holt-Winters forecasting from your df_wide.csv"""
    try:
        if data_source == "historical" and historical_df is not None:
            values = historical_df['soil_ec'].dropna().values
        else:
            # Use sample data
            logger.warning("Using sample data for Holt-Winters")
            values = 1000 + np.random.normal(0, 200, 200) + 300 * np.sin(np.arange(200) * 0.05)
            values = np.maximum(values, 0)  # Ensure non-negative
        
        logger.info(f"Prepared {len(values)} data points for Holt-Winters")
        return values
        
    except Exception as e:
        logger.error(f"Error preparing data for Holt-Winters: {e}")
        raise

@app.get("/")
async def root():
    return {
        "message": "Soil Health ML API for Urban Farming",
        "version": "1.0.0",
        "status": "running",
        "models_loaded": {
            "prophet_moisture": prophet_model is not None,
            "holt_winters_ec": hw_model is not None
        },
        "historical_data_loaded": historical_df is not None,
        "data_points": len(historical_df) if historical_df is not None else 0
    }

@app.post("/forecast/moisture", response_model=ForecastResponse)
async def forecast_moisture(request: ForecastRequest):
    """Generate soil moisture forecast using Prophet model"""
    try:
        forecast_days = min(request.forecast_days, 365)  # Limit to 1 year
        
        if request.historical_data:
            # Convert provided data to DataFrame
            df = pd.DataFrame(request.historical_data)
            df['ds'] = pd.to_datetime(df['dbtimestamp'])
            df['y'] = pd.to_numeric(df['soil_moisture'], errors='coerce')
            df = df[['ds', 'y']].dropna()
        else:
            # Use your historical data or prepare sample data
            df = prepare_data_for_prophet()
        
        if len(df) < 10:
            raise HTTPException(status_code=400, detail="Insufficient historical data for forecasting")
        
        # Use the loaded Prophet model or create a new one
        if prophet_model is not None:
            model = prophet_model
            logger.info("Using pre-trained Prophet model")
        else:
            # Train a new Prophet model
            logger.info("Training new Prophet model")
            model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            model.fit(df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_days, freq='D')
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Extract only the forecast period (not historical)
        forecast_period = forecast.tail(forecast_days)
        
        # Format response
        forecast_points = []
        for _, row in forecast_period.iterrows():
            # Ensure moisture values are within realistic bounds
            yhat = max(0, min(100, row['yhat']))
            yhat_lower = max(0, min(100, row['yhat_lower']))
            yhat_upper = max(0, min(100, row['yhat_upper']))
            
            forecast_points.append(ForecastPoint(
                ds=row['ds'].strftime('%Y-%m-%d'),
                yhat=round(yhat, 2),
                yhat_lower=round(yhat_lower, 2),
                yhat_upper=round(yhat_upper, 2)
            ))
        
        return ForecastResponse(
            forecast=forecast_points,
            model_type="Prophet (Facebook)",
            forecast_days=forecast_days,
            generated_at=datetime.now().isoformat(),
            data_points_used=len(df)
        )
        
    except Exception as e:
        logger.error(f"Error in moisture forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Moisture forecast failed: {str(e)}")

@app.post("/forecast/ec", response_model=ForecastResponse)
async def forecast_ec(request: ForecastRequest):
    """Generate EC forecast using Holt-Winters model"""
    try:
        forecast_days = min(request.forecast_days, 365)  # Limit to 1 year
        
        if request.historical_data:
            # Convert provided data to array
            df = pd.DataFrame(request.historical_data)
            values = pd.to_numeric(df['soil_ec'], errors='coerce').dropna().values
        else:
            # Use your historical data
            values = prepare_data_for_hw()
        
        if len(values) < 20:
            raise HTTPException(status_code=400, detail="Insufficient historical data for EC forecasting")
        
        # Generate forecast using your trained Holt-Winters model
        if hw_model is not None:
            try:
                logger.info("Using pre-trained Holt-Winters model")
                
                # Try different methods to generate forecast depending on model type
                if hasattr(hw_model, 'forecast'):
                    # Standard statsmodels ExponentialSmoothing
                    forecast_values = hw_model.forecast(steps=forecast_days)
                    
                    # Generate confidence intervals
                    if hasattr(hw_model, 'prediction_intervals'):
                        conf_int = hw_model.prediction_intervals(steps=forecast_days, alpha=0.05)
                        lower_bounds = conf_int.iloc[:, 0].values
                        upper_bounds = conf_int.iloc[:, 1].values
                    else:
                        # Approximate confidence intervals
                        residuals_std = np.std(values[-50:]) if len(values) >= 50 else np.std(values)
                        lower_bounds = forecast_values - 1.96 * residuals_std
                        upper_bounds = forecast_values + 1.96 * residuals_std
                        
                elif hasattr(hw_model, 'predict'):
                    # Alternative predict method
                    forecast_values = hw_model.predict(start=len(values), end=len(values) + forecast_days - 1)
                    residuals_std = np.std(values[-50:]) if len(values) >= 50 else np.std(values)
                    lower_bounds = forecast_values - 1.96 * residuals_std
                    upper_bounds = forecast_values + 1.96 * residuals_std
                    
                else:
                    raise ValueError("Model doesn't have forecast or predict method")
                    
            except Exception as model_error:
                logger.warning(f"Pre-trained model failed: {model_error}, using trend-based forecast")
                raise model_error
                
        else:
            logger.info("No pre-trained model, using trend-based forecasting")
            raise ValueError("No model available")
            
        # Ensure forecast values are reasonable (non-negative)
        forecast_values = np.maximum(forecast_values, 0)
        lower_bounds = np.maximum(lower_bounds, 0)
        upper_bounds = np.maximum(upper_bounds, 0)
        
        # Create date range for forecast
        if historical_df is not None and 'dbtimestamp' in historical_df.columns:
            last_date = historical_df['dbtimestamp'].max()
        else:
            last_date = datetime.now()
            
        start_date = last_date + timedelta(days=1)
        dates = [start_date + timedelta(days=i) for i in range(forecast_days)]
        
        # Format response
        forecast_points = []
        for i, date in enumerate(dates):
            forecast_points.append(ForecastPoint(
                ds=date.strftime('%Y-%m-%d'),
                yhat=round(float(forecast_values[i]), 2),
                yhat_lower=round(float(lower_bounds[i]), 2),
                yhat_upper=round(float(upper_bounds[i]), 2)
            ))
        
        return ForecastResponse(
            forecast=forecast_points,
            model_type="Holt-Winters Exponential Smoothing",
            forecast_days=forecast_days,
            generated_at=datetime.now().isoformat(),
            data_points_used=len(values)
        )
        
    except Exception as e:
        logger.error(f"Error in EC forecast: {e}")
        
        # Fallback: Generate trend-based forecast
        try:
            logger.info("Using fallback trend-based EC forecast")
            values = prepare_data_for_hw()
            
            # Simple trend analysis
            recent_values = values[-30:] if len(values) >= 30 else values
            trend = np.mean(np.diff(recent_values)) if len(recent_values) > 1 else 0
            last_value = recent_values[-1]
            volatility = np.std(recent_values) * 0.3
            
            # Generate forecast
            forecast_points = []
            start_date = datetime.now() + timedelta(days=1)
            
            for i in range(forecast_days):
                date = start_date + timedelta(days=i)
                
                # Add some seasonality and noise
                seasonal = 50 * np.sin(i * 2 * np.pi / 30)  # Monthly seasonality
                forecast_value = max(0, last_value + (trend * i) + seasonal)
                
                forecast_points.append(ForecastPoint(
                    ds=date.strftime('%Y-%m-%d'),
                    yhat=round(forecast_value, 2),
                    yhat_lower=round(max(0, forecast_value - volatility), 2),
                    yhat_upper=round(forecast_value + volatility, 2)
                ))
            
            return ForecastResponse(
                forecast=forecast_points,
                model_type="Trend-based Fallback",
                forecast_days=forecast_days,
                generated_at=datetime.now().isoformat(),
                data_points_used=len(values)
            )
            
        except Exception as fallback_error:
            logger.error(f"Fallback forecast also failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=f"EC forecast failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "prophet_moisture": "loaded" if prophet_model else "not loaded",
            "holt_winters_ec": "loaded" if hw_model else "not loaded"
        },
        "data": {
            "historical_loaded": historical_df is not None,
            "data_points": len(historical_df) if historical_df is not None else 0,
            "date_range": {
                "start": historical_df['dbtimestamp'].min().isoformat() if historical_df is not None else None,
                "end": historical_df['dbtimestamp'].max().isoformat() if historical_df is not None else None
            } if historical_df is not None else None
        }
    }

@app.get("/models/info")
async def model_info():
    """Get information about loaded models and data"""
    info = {
        "prophet_moisture": None,
        "holt_winters_ec": None,
        "historical_data": None
    }
    
    if prophet_model:
        info["prophet_moisture"] = {
            "type": "Prophet (Facebook)",
            "loaded": True,
            "description": "Time series forecasting for soil moisture prediction"
        }
    
    if hw_model:
        info["holt_winters_ec"] = {
            "type": "Holt-Winters Exponential Smoothing",
            "loaded": True,
            "description": "Exponential smoothing for electrical conductivity prediction",
            "model_summary": str(type(hw_model))
        }
    
    if historical_df is not None:
        info["historical_data"] = {
            "loaded": True,
            "rows": len(historical_df),
            "columns": list(historical_df.columns),
            "date_range": {
                "start": historical_df['dbtimestamp'].min().isoformat(),
                "end": historical_df['dbtimestamp'].max().isoformat()
            },
            "sensors": {
                "soil_moisture_range": [
                    float(historical_df['soil_moisture'].min()), 
                    float(historical_df['soil_moisture'].max())
                ] if 'soil_moisture' in historical_df.columns else None,
                "soil_ec_range": [
                    float(historical_df['soil_ec'].min()), 
                    float(historical_df['soil_ec'].max())
                ] if 'soil_ec' in historical_df.columns else None
            }
        }
    
    return info

@app.get("/data/sample")
async def get_sample_data():
    """Get a sample of historical data for testing"""
    if historical_df is not None:
        sample = historical_df.tail(50).to_dict('records')
        return {
            "sample_data": sample,
            "total_records": len(historical_df),
            "message": "Last 50 records from your df_wide.csv"
        }
    else:
        return {
            "sample_data": [],
            "total_records": 0,
            "message": "No historical data loaded"
        }

if __name__ == "__main__":
    import uvicorn
    
    # Run the API server
    uvicorn.run(
        "API:app",  # Adjust this if your file is named differently
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )