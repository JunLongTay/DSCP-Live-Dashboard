from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime, timedelta
import traceback
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model_data = None
model_loaded = False
best_model = None
best_model_name = None
feature_names = None

def load_trained_models():
    """Load the pre-trained optimal models"""
    global model_data, model_loaded, best_model, best_model_name, feature_names

    try:
        model_data = joblib.load('models/optimal_moisture_models.pkl')
        
        best_model_name = model_data.get('best_model_name')
        best_model = model_data.get('best_model')
        feature_names = model_data.get('feature_names')
        
        if best_model_name and best_model:
            model_loaded = True
            logger.info(f"✅ Best model loaded: {best_model_name}")
            logger.info(f"📊 Training date: {model_data.get('training_timestamp', 'Unknown')}")
            
            # Log available models
            available_models = list(model_data.get('models', {}).keys())
            logger.info(f"📦 Available models: {available_models}")
            
        else:
            logger.error("❌ No best model found in saved data")
            model_loaded = False
            
    except FileNotFoundError:
        logger.error("❌ Model file not found. Please run training script first.")
        model_loaded = False
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}")
        model_loaded = False

def prepare_features_for_device(device_data):
    """Prepare features from device data (same as training script)"""
    if not device_data:
        logger.warning("No device data provided")
        return None
    
    try:
        df = pd.DataFrame(device_data)
        
        # Convert timestamp
        if 'devicetimestamp' in df.columns:
            df['devicetimestamp'] = pd.to_datetime(df['devicetimestamp'])
            
            # For prediction, we'll use the timestamp as index
            df = df.set_index('devicetimestamp').sort_index()
            
            # Cyclical time features
            df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
            df['day_sin'] = np.sin(2 * np.pi * df.index.dayofyear / 365)
            df['day_cos'] = np.cos(2 * np.pi * df.index.dayofyear / 365)
            df['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
            df['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)
        
        # Rename moisture column if needed
        if 'moisture' in df.columns:
            df.rename(columns={'moisture': 'Soil Moisture'}, inplace=True)
        
        # Lag features for soil moisture
        if 'Soil Moisture' in df.columns:
            for lag in [1, 2, 3, 6, 12, 24]:
                df[f'moisture_lag_{lag}'] = df['Soil Moisture'].shift(lag)
            
            # Rolling statistics
            for window in [3, 7, 14]:
                df[f'moisture_rolling_mean_{window}'] = df['Soil Moisture'].rolling(window).mean()
                df[f'moisture_rolling_std_{window}'] = df['Soil Moisture'].rolling(window).std()
        
        # Weather-based features
        if 'temperature' in df.columns and 'Soil Moisture' in df.columns:
            df['temp_moisture_ratio'] = df['temperature'] / (df['Soil Moisture'] + 1e-6)
        
        # NPK ratios
        npk_cols = ['npk_n', 'npk_p', 'npk_k']
        if all(col in df.columns for col in npk_cols):
            df['npk_total'] = df[npk_cols].sum(axis=1)
            for col in npk_cols:
                df[f'{col}_ratio'] = df[col] / (df['npk_total'] + 1e-6)
        
        return df
        
    except Exception as e:
        logger.error(f"Error preparing features: {e}")
        return None

def predict_with_arima_sarima(device_name, device_data, days_ahead=30):
    """Predict using ARIMA/SARIMA models"""
    try:
        df = pd.DataFrame(device_data)
        
        # Convert timestamp and sort
        if 'devicetimestamp' in df.columns:
            df['devicetimestamp'] = pd.to_datetime(df['devicetimestamp'])
            df = df.sort_values('devicetimestamp')
        
        # Get moisture column
        if 'moisture' in df.columns:
            moisture_series = df['moisture']
        elif 'Soil Moisture' in df.columns:
            moisture_series = df['Soil Moisture']
        else:
            raise ValueError("No moisture data found")
        
        # Clean the series
        moisture_series = moisture_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        if len(moisture_series) < 10:
            raise ValueError(f"Insufficient data for {device_name}: {len(moisture_series)} points")
        
        # Get the model
        model_info = best_model
        
        if best_model_name == 'ARIMA':
            # For ARIMA, we need to refit with recent data or use stored model
            from statsmodels.tsa.arima.model import ARIMA
            
            # Use the same order as the trained model
            order = model_info.get('order', (1, 1, 1))
            
            # Fit ARIMA on recent data
            arima_model = ARIMA(moisture_series, order=order)
            arima_fitted = arima_model.fit()
            
            # Forecast
            forecast = arima_fitted.forecast(steps=days_ahead)
            
        elif best_model_name == 'SARIMA':
            # For SARIMA
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            
            order = model_info.get('order', (1, 1, 1))
            seasonal_order = model_info.get('seasonal_order', (1, 1, 1, 24))
            
            # Fit SARIMA on recent data
            sarima_model = SARIMAX(moisture_series, order=order, seasonal_order=seasonal_order)
            sarima_fitted = sarima_model.fit(disp=False)
            
            # Forecast
            forecast = sarima_fitted.forecast(steps=days_ahead)
        
        # Generate forecast dates
        last_date = df['devicetimestamp'].max()
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=days_ahead,
            freq='D'
        )
        
        # Format results
        forecast_data = []
        for i, (date, value) in enumerate(zip(forecast_dates, forecast)):
            forecast_data.append({
                'day': i + 1,
                'date': date.isoformat(),
                'predicted_moisture': round(float(value), 2)
            })
        
        return {
            'forecast': forecast_data,
            'model_used': best_model_name,
            'data_points_used': len(moisture_series)
        }
        
    except Exception as e:
        logger.error(f"ARIMA/SARIMA prediction error for {device_name}: {e}")
        return None

def predict_with_ml(device_name, device_data, days_ahead=30):
    """Predict using Random Forest (requires feature engineering)"""
    try:
        # Prepare features
        features_df = prepare_features_for_device(device_data)
        
        if features_df is None or len(features_df) == 0:
            raise ValueError("Could not prepare features")
        
        # Get the latest complete record (no NaN values)
        latest_features = features_df[feature_names].dropna()
        
        if len(latest_features) == 0:
            raise ValueError("No complete feature records available")
        
        # Use the most recent complete record
        X_pred = latest_features.tail(1)
        
        # Get the model
        rf_model = best_model['model']
        
        # Make prediction for current conditions
        current_prediction = rf_model.predict(X_pred)[0]
        
        # For ML models, we can't easily predict far into the future
        # without future feature values, so we'll use a simple approach:
        # assume gradual change based on current trends
        
        moisture_series = features_df['Soil Moisture'].dropna()
        if len(moisture_series) > 5:
            # Calculate recent trend
            recent_trend = moisture_series.tail(5).diff().mean()
        else:
            recent_trend = 0
        
        # Generate forecast with trend
        forecast_data = []
        last_date = features_df.index[-1]
        
        for day in range(1, days_ahead + 1):
            # Simple trend-based prediction
            predicted_value = current_prediction + (recent_trend * day * 0.1)  # Damped trend
            
            # Ensure reasonable bounds
            predicted_value = max(0, min(100, predicted_value))
            
            forecast_date = last_date + pd.Timedelta(days=day)
            
            forecast_data.append({
                'day': day,
                'date': forecast_date.isoformat(),
                'predicted_moisture': round(float(predicted_value), 2)
            })
        
        return {
            'forecast': forecast_data,
            'model_used': best_model_name,
            'note': 'ML prediction with trend extrapolation (limited accuracy for long-term)',
            'data_points_used': len(moisture_series)
        }
        
    except Exception as e:
        logger.error(f"ML prediction error for {device_name}: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'best_model': best_model_name,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get information about the loaded models"""
    if not model_loaded:
        return jsonify({'error': 'No models loaded'}), 404
    
    models_info = {}
    for model_name, model_data_item in model_data.get('models', {}).items():
        if model_name == 'ARIMA':
            models_info[model_name] = {
                'order': model_data_item.get('order'),
                'is_stationary': model_data_item.get('is_stationary')
            }
        elif model_name == 'SARIMA':
            models_info[model_name] = {
                'order': model_data_item.get('order'),
                'seasonal_order': model_data_item.get('seasonal_order'),
                'seasonal_period': model_data_item.get('seasonal_period'),
                'aic': model_data_item.get('aic')
            }
        elif model_name == 'RandomForest':
            models_info[model_name] = {
                'cv_score': model_data_item.get('cv_score'),
                'n_features': len(model_data_item.get('feature_names', [])),
                'top_features': model_data_item.get('feature_importance', pd.DataFrame()).head(5).to_dict('records') if 'feature_importance' in model_data_item else []
            }
    
    return jsonify({
        'models_available': list(model_data.get('models', {}).keys()),
        'best_model': best_model_name,
        'training_timestamp': model_data.get('training_timestamp'),
        'models_info': models_info
    })

@app.route('/predict/moisture/batch', methods=['POST'])
def predict_moisture_batch():
    """
    Predict moisture levels for multiple devices using the best trained model
    """
    if not model_loaded:
        return jsonify({'error': 'No models loaded. Please run training script first.'}), 500

    try:
        data = request.get_json()

        if not data or 'devices' not in data:
            return jsonify({'error': 'devices data is required'}), 400

        devices_data = data['devices']
        days_ahead = data.get('days_ahead', 30)

        logger.info(f"Batch prediction request for {len(devices_data)} devices, days_ahead={days_ahead}")
        logger.info(f"Using best model: {best_model_name}")

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

                # Make predictions based on best model type
                if best_model_name in ['ARIMA', 'SARIMA']:
                    prediction_result = predict_with_arima_sarima(device_name, recent_data, days_ahead)
                elif best_model_name == 'RandomForest':
                    prediction_result = predict_with_ml(device_name, recent_data, days_ahead)
                else:
                    prediction_result = None

                if prediction_result is None:
                    results[device_name] = {
                        'error': f'{best_model_name} prediction failed',
                        'forecast': []
                    }
                else:
                    results[device_name] = prediction_result

            except Exception as device_error:
                logger.error(f"Error predicting for device {device_name}: {device_error}")
                results[device_name] = {
                    'error': str(device_error),
                    'forecast': []
                }

        # Calculate success rate
        successful_predictions = sum(1 for result in results.values() if 'error' not in result)
        success_rate = successful_predictions / len(devices_data) if devices_data else 0

        logger.info(f"Batch prediction completed. Success rate: {success_rate:.1%}")

        return jsonify({
            'predictions': results,
            'metadata': {
                'prediction_timestamp': datetime.now().isoformat(),
                'days_predicted': days_ahead,
                'devices_processed': len(devices_data),
                'successful_predictions': successful_predictions,
                'success_rate': f"{success_rate:.1%}",
                'model_used': best_model_name
            }
        })

    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Batch prediction failed: {str(e)}'}), 500

@app.route('/predict/moisture/single', methods=['POST'])
def predict_moisture_single():
    """
    Predict moisture for a single device
    """
    if not model_loaded:
        return jsonify({'error': 'No models loaded'}), 500

    try:
        data = request.get_json()
        
        if not data or 'device_name' not in data or 'recent_data' not in data:
            return jsonify({'error': 'device_name and recent_data are required'}), 400

        device_name = data['device_name']
        recent_data = data['recent_data']
        days_ahead = data.get('days_ahead', 30)

        logger.info(f"Single prediction for device: {device_name}")

        # Make prediction
        if best_model_name in ['ARIMA', 'SARIMA']:
            prediction_result = predict_with_arima_sarima(device_name, recent_data, days_ahead)
        elif best_model_name == 'RandomForest':
            prediction_result = predict_with_ml(device_name, recent_data, days_ahead)
        else:
            return jsonify({'error': f'Unknown model type: {best_model_name}'}), 500

        if prediction_result is None:
            return jsonify({'error': 'Prediction failed'}), 500

        return jsonify({
            'device_name': device_name,
            'prediction': prediction_result,
            'metadata': {
                'prediction_timestamp': datetime.now().isoformat(),
                'model_used': best_model_name,
                'days_predicted': days_ahead
            }
        })

    except Exception as e:
        logger.error(f"Error in single prediction: {str(e)}")
        return jsonify({'error': f'Single prediction failed: {str(e)}'}), 500

@app.route('/retrain', methods=['POST'])
def trigger_retrain():
    """
    Endpoint to trigger model retraining (calls the training script)
    """
    try:
        import subprocess
        import sys
        
        logger.info("Starting model retraining...")
        
        # Run the training script
        result = subprocess.run([sys.executable, 'train_models.py'], 
                              capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            # Reload models after successful training
            load_trained_models()
            
            return jsonify({
                'status': 'success',
                'message': 'Models retrained successfully',
                'new_best_model': best_model_name,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Training failed',
                'error': result.stderr,
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'status': 'error',
            'message': 'Training timeout (>30 minutes)',
            'timestamp': datetime.now().isoformat()
        }), 500
    except Exception as e:
        logger.error(f"Retrain error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Retrain failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/model/stats', methods=['GET'])
def get_model_stats():
    """Get detailed statistics about the current models"""
    if not model_loaded:
        return jsonify({'error': 'No models loaded'}), 404
    
    try:
        stats = {
            'best_model': best_model_name,
            'training_date': model_data.get('training_timestamp'),
            'models_count': len(model_data.get('models', {})),
            'available_models': list(model_data.get('models', {}).keys())
        }
        
        # Add model-specific stats
        if best_model_name == 'RandomForest' and feature_names:
            stats['feature_count'] = len(feature_names)
            stats['top_features'] = feature_names[:10] if len(feature_names) > 10 else feature_names
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting model stats: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Optimized Moisture Prediction API")
    print("=" * 50)
    
    # Load models on startup
    print("📦 Loading pre-trained models...")
    load_trained_models()
    
    if model_loaded:
        print(f"✅ Models loaded successfully!")
        print(f"🏆 Best model: {best_model_name}")
        print(f"🔧 Available endpoints:")
        print("   - GET  /health")
        print("   - GET  /model/info")
        print("   - GET  /model/stats")
        print("   - POST /predict/moisture/batch")
        print("   - POST /predict/moisture/single")
        print("   - POST /retrain")
    else:
        print("❌ Failed to load models!")
        print("💡 Please run the training script first:")
        print("   python train_models.py")
    
    print("=" * 50)
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )