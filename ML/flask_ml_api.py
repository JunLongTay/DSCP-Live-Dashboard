from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime, timedelta
import traceback

# Import your ML pipeline
from ml_pipeline_fixed import MoisturePredictionPipeline

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
ml_pipeline = None
model_loaded = False

def load_ml_model():
    """Load the trained ML model on startup"""
    global ml_pipeline, model_loaded
    
    try:
        ml_pipeline = MoisturePredictionPipeline()
        ml_pipeline.load_model('models/moisture_predictor.pkl')
        model_loaded = True
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        model_loaded = False

def prepare_features(device_data):
    """
    Prepare features from recent device data for prediction
    """
    if not device_data:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(device_data)
    
    # Ensure timestamp column exists and is datetime
    if 'devicetimestamp' in df.columns:
        df['devicetimestamp'] = pd.to_datetime(df['devicetimestamp'])
        
        # Create time features
        df['hour'] = df['devicetimestamp'].dt.hour
        df['weekday'] = df['devicetimestamp'].dt.weekday
        df['month'] = df['devicetimestamp'].dt.month
        df['day_of_year'] = df['devicetimestamp'].dt.dayofyear
    
    # Select only the features that the model expects
    if ml_pipeline and ml_pipeline.feature_columns:
        available_features = [col for col in ml_pipeline.feature_columns if col in df.columns]
        df_features = df[available_features]
        
        # Fill missing features with default values
        for col in ml_pipeline.feature_columns:
            if col not in df_features.columns:
                df_features[col] = 0  # or appropriate default value
        
        return df_features[ml_pipeline.feature_columns]
    
    return df

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict/moisture/<device_name>', methods=['POST'])
def predict_moisture(device_name):
    """
    Predict moisture levels for a specific device
    Expects JSON body with recent device data
    """
    if not model_loaded:
        return jsonify({'error': 'ML model not loaded'}), 500
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'recent_data' not in data:
            return jsonify({'error': 'recent_data is required'}), 400
        
        recent_data = data['recent_data']
        days_ahead = data.get('days_ahead', 30)
        
        # Prepare features
        features_df = prepare_features(recent_data)
        
        if features_df is None or len(features_df) == 0:
            return jsonify({'error': 'Unable to prepare features from data'}), 400
        
        # Make predictions
        predictions = ml_pipeline.predict_future(features_df, days_ahead)
        
        # Format response
        forecast_data = []
        base_date = datetime.now()
        
        for i, pred in enumerate(predictions):
            forecast_date = base_date + timedelta(days=i+1)
            forecast_data.append({
                'day': i + 1,
                'date': forecast_date.isoformat(),
                'predicted_moisture': round(float(pred), 2),
                'confidence': 'medium'  # You could implement confidence intervals
            })
        
        return jsonify({
            'device_name': device_name,
            'model_used': ml_pipeline.best_model_name,
            'forecast': forecast_data,
            'metadata': {
                'prediction_timestamp': datetime.now().isoformat(),
                'days_predicted': days_ahead,
                'input_data_points': len(recent_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/predict/moisture/batch', methods=['POST'])
def predict_moisture_batch():
    """
    Predict moisture levels for multiple devices
    """
    if not model_loaded:
        return jsonify({'error': 'ML model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'devices' not in data:
            return jsonify({'error': 'devices data is required'}), 400
        
        devices_data = data['devices']
        days_ahead = data.get('days_ahead', 30)
        
        results = {}
        
        for device_name, device_info in devices_data.items():
            try:
                recent_data = device_info.get('recent_data', [])
                
                if not recent_data:
                    results[device_name] = {
                        'error': 'No recent data provided',
                        'forecast': []
                    }
                    continue
                
                # Prepare features
                features_df = prepare_features(recent_data)
                
                if features_df is None or len(features_df) == 0:
                    results[device_name] = {
                        'error': 'Unable to prepare features',
                        'forecast': []
                    }
                    continue
                
                # Make predictions
                predictions = ml_pipeline.predict_future(features_df, days_ahead)
                
                # Format forecast data
                forecast_data = []
                base_date = datetime.now()
                
                for i, pred in enumerate(predictions):
                    forecast_date = base_date + timedelta(days=i+1)
                    forecast_data.append({
                        'day': i + 1,
                        'date': forecast_date.isoformat(),
                        'predicted_moisture': round(float(pred), 2)
                    })
                
                results[device_name] = {
                    'forecast': forecast_data,
                    'model_used': ml_pipeline.best_model_name
                }
                
            except Exception as device_error:
                logger.error(f"Error predicting for device {device_name}: {device_error}")
                results[device_name] = {
                    'error': str(device_error),
                    'forecast': []
                }
        
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
        'model_name': ml_pipeline.best_model_name,
        'feature_columns': ml_pipeline.feature_columns,
        'target_column': ml_pipeline.target_column,
        'model_loaded': model_loaded
    })

@app.route('/retrain', methods=['POST'])
def retrain_model():
    """
    Retrain the model with new data
    This is a placeholder - implement based on your needs
    """
    return jsonify({
        'message': 'Model retraining not implemented yet',
        'status': 'not_implemented'
    }), 501

if __name__ == '__main__':
    # Load model on startup
    load_ml_model()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
