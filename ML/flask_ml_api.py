from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime, timedelta
import traceback
from statsmodels.tsa.arima.model import ARIMA

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
arima_model_fit = None
model_loaded = False

def load_ml_model():
    """Load the ARIMA model on startup"""
    global arima_model_fit, model_loaded

    try:
        # Load ARIMA model directly from joblib
        arima_model_fit = joblib.load('models/arima_model.pkl')
        model_loaded = True
        logger.info("ARIMA model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ARIMA model: {e}")
        model_loaded = False

def prepare_features(device_data):
    """
    Prepare features from recent device data for prediction
    """
    if not device_data:
        logger.warning("No device data provided to prepare_features")
        return None

    # Convert to DataFrame
    df = pd.DataFrame(device_data)
    logger.info(f"Incoming data columns: {df.columns.tolist()}")

    # Ensure timestamp column exists and is datetime
    if 'devicetimestamp' in df.columns:
        df['devicetimestamp'] = pd.to_datetime(df['devicetimestamp'])

        # Create time features
        df['hour'] = df['devicetimestamp'].dt.hour
        df['weekday'] = df['devicetimestamp'].dt.weekday
        df['month'] = df['devicetimestamp'].dt.month
        df['day_of_year'] = df['devicetimestamp'].dt.dayofyear

    return df

def train_arima_for_device(device_name, device_data):
    """Train ARIMA model for a specific device"""
    # Prepare the device's data for ARIMA
    df = pd.DataFrame(device_data)
    df['devicetimestamp'] = pd.to_datetime(df['devicetimestamp'])

    # Ensure 'Soil Moisture' is the only column used for ARIMA
    if 'Soil Moisture' not in df.columns:
        raise ValueError(f"Missing 'Soil Moisture' in the data for device {device_name}")

    # Use the 'Soil Moisture' column for ARIMA prediction
    device_data = df[['devicetimestamp', 'Soil Moisture']].sort_values(by='devicetimestamp')

    # Set 'devicetimestamp' as the index for ARIMA
    device_data.set_index('devicetimestamp', inplace=True)

    # Check if there is enough data for ARIMA
    if len(device_data) < 2:  # ARIMA requires at least two data points
        raise ValueError(f"Not enough data for device {device_name} to train ARIMA")

    try:
        # Fit ARIMA model (using order (p, d, q) you might want to tune)
        arima_model = ARIMA(device_data['Soil Moisture'], order=(5, 1, 0))  # Example order (p=5, d=1, q=0)
        arima_model_fit = arima_model.fit()

        # Forecast future values (e.g., 30 days ahead)
        forecast_values = arima_model_fit.forecast(steps=30)
        forecast_dates = device_data.index[-1] + pd.to_timedelta(range(1, 31), unit='D')

        forecast_data = {
            'forecast': forecast_values,
            'dates': forecast_dates
        }

        return forecast_data
    except Exception as e:
        logger.error(f"Error training ARIMA for {device_name}: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict/moisture/batch', methods=['POST'])
def predict_moisture_batch():
    """
    Predict moisture levels for multiple devices
    """
    if not model_loaded:
        return jsonify({'error': 'ARIMA model not loaded'}), 500

    try:
        data = request.get_json()

        if not data or 'devices' not in data:
            return jsonify({'error': 'devices data is required'}), 400

        devices_data = data['devices']
        days_ahead = data.get('days_ahead', 30)

        logger.info(f"Batch prediction request for {len(devices_data)} devices, days_ahead={days_ahead}")

        results = {}

        for device_name, device_info in devices_data.items():
            try:
                recent_data = device_info.get('recent_data', [])
                logger.info(f"Device '{device_name}' - recent_data count: {len(recent_data)}")

                if not recent_data:
                    results[device_name] = {
                        'error': 'No recent data provided',
                        'forecast': []
                    }
                    continue

                # Prepare features
                features_df = prepare_features(recent_data)
                logger.info(f"Device '{device_name}' - features shape: {features_df.shape if features_df is not None else None}")

                if features_df is None or len(features_df) == 0:
                    results[device_name] = {
                        'error': 'Unable to prepare features',
                        'forecast': []
                    }
                    continue

                # Make predictions using ARIMA (this should always use ARIMA)
                forecast_data = train_arima_for_device(device_name, recent_data)
                
                if forecast_data is None:
                    results[device_name] = {
                        'error': 'ARIMA model prediction failed',
                        'forecast': []
                    }
                else:
                    # Format forecast data
                    forecast_data_formatted = []
                    for i, forecast in enumerate(forecast_data['forecast']):
                        forecast_date = forecast_data['dates'][i]
                        forecast_data_formatted.append({
                            'day': i + 1,
                            'date': forecast_date.isoformat(),
                            'predicted_moisture': round(float(forecast), 2)
                        })

                    results[device_name] = {
                        'forecast': forecast_data_formatted,
                        'model_used': 'ARIMA'
                    }

            except Exception as device_error:
                logger.error(f"Error predicting for device {device_name}: {device_error}")
                results[device_name] = {
                    'error': str(device_error),
                    'forecast': []
                }

        logger.info(f"Batch prediction results: { {k: v.get('model_used', v.get('error')) for k, v in results.items()} }")

        return jsonify({
            'predictions': results,
            'metadata': {
                'prediction_timestamp': datetime.now().isoformat(),
                'days_predicted': days_ahead,
                'devices_processed': len(devices_data)
            }
        })

    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if not model_loaded:
        return jsonify({'error': 'No model loaded'}), 404
    
    return jsonify({
        'model_name': 'ARIMA',
        'model_loaded': model_loaded
    })

if __name__ == '__main__':
    # Load ARIMA model on startup
    load_ml_model()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
