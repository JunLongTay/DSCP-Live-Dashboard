import joblib
import pandas as pd
import numpy as np
import requests
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def fetch_live_detailed_data():
    """Fetch data from your API endpoint"""
    try:
        url = "http://localhost:3001/moisture-detailed?bucket_min=2&window_min=10080"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def prepare_features(df):
    """Prepare features (simplified version)"""
    df = df.copy()
    
    # Rename moisture column
    if "moisture" in df.columns:
        df.rename(columns={"moisture": "Soil Moisture"}, inplace=True)
    
    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp").sort_index()
        
        # Basic time features
        df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
        df['day_sin'] = np.sin(2 * np.pi * df.index.dayofyear / 365)
        df['day_cos'] = np.cos(2 * np.pi * df.index.dayofyear / 365)
        df['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
        df['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)
    
    # Lag features for soil moisture
    if 'Soil Moisture' in df.columns:
        for lag in [1, 2, 3, 6, 12, 24]:
            df[f'moisture_lag_{lag}'] = df['Soil Moisture'].shift(lag)
        
        # Rolling statistics
        for window in [3, 7, 14]:
            df[f'moisture_rolling_mean_{window}'] = df['Soil Moisture'].rolling(window).mean()
            df[f'moisture_rolling_std_{window}'] = df['Soil Moisture'].rolling(window).std()
    
    # NPK ratios
    npk_cols = ['npk_n', 'npk_p', 'npk_k']
    if all(col in df.columns for col in npk_cols):
        df['npk_total'] = df[npk_cols].sum(axis=1)
        for col in npk_cols:
            df[f'{col}_ratio'] = df[col] / (df['npk_total'] + 1e-6)
    
    return df

def evaluate_models_and_select_best():
    """Load existing models, evaluate them, and select the best one"""
    
    print("🔍 Loading existing model file...")
    try:
        model_data = joblib.load('models/optimal_moisture_models.pkl')
    except Exception as e:
        print(f"❌ Error loading model file: {e}")
        return False
    
    print("📊 Found models:", list(model_data['models'].keys()))
    
    # Fetch fresh data for evaluation
    print("📡 Fetching fresh data for model evaluation...")
    df = fetch_live_detailed_data()
    
    if df is None or len(df) < 50:
        print("❌ Insufficient data for evaluation")
        return False
    
    # Preprocess data
    df = prepare_features(df)
    df = df.dropna()
    
    if len(df) < 30:
        print("❌ Not enough clean data for evaluation")
        return False
    
    print(f"✅ Using {len(df)} data points for evaluation")
    
    # Test each model
    test_days = min(14, len(df) // 3)  # Use smaller test period
    split_point = len(df) - test_days
    
    print(f"📈 Testing models on last {test_days} days...")
    
    results = {}
    
    for model_name, model_info in model_data['models'].items():
        try:
            print(f"\n🧪 Testing {model_name}...")
            
            if model_name in ['ARIMA', 'SARIMA']:
                # Time series forecast
                moisture_series = df['Soil Moisture'].iloc[:split_point]
                
                if model_name == 'ARIMA':
                    forecast = model_info['model'].forecast(steps=test_days)
                elif model_name == 'SARIMA':
                    forecast = model_info['model'].forecast(steps=test_days)
                
                y_pred = forecast
                
            elif model_name == 'RandomForest':
                # ML prediction
                feature_names = model_data.get('feature_names', [])
                
                if not feature_names:
                    print(f"  ❌ No feature names found for RandomForest")
                    continue
                
                # Check if we have all required features
                missing_features = [f for f in feature_names if f not in df.columns]
                if missing_features:
                    print(f"  ❌ Missing features: {missing_features[:5]}...")
                    continue
                
                X_test = df[feature_names].iloc[split_point:].dropna()
                
                if len(X_test) == 0:
                    print(f"  ❌ No valid test features for RandomForest")
                    continue
                
                y_pred = model_info['model'].predict(X_test)
            
            # Calculate metrics
            y_true = df['Soil Moisture'].iloc[split_point:split_point + len(y_pred)].values
            
            if len(y_true) != len(y_pred):
                min_len = min(len(y_true), len(y_pred))
                y_true = y_true[:min_len]
                y_pred = y_pred[:min_len]
            
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            r2 = r2_score(y_true, y_pred)
            
            results[model_name] = {
                'MAE': mae,
                'RMSE': rmse,
                'R²': r2,
                'predictions': len(y_pred)
            }
            
            print(f"  📊 MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.3f}")
            
        except Exception as e:
            print(f"  ❌ {model_name} evaluation failed: {e}")
            results[model_name] = {'error': str(e)}
    
    # Select best model
    valid_results = {k: v for k, v in results.items() if 'error' not in v}
    
    if not valid_results:
        print("❌ No models could be evaluated successfully")
        return False
    
    # Choose best model based on lowest RMSE
    best_model_name = min(valid_results.keys(), key=lambda x: valid_results[x]['RMSE'])
    best_model_info = model_data['models'][best_model_name]
    
    print(f"\n🏆 BEST MODEL: {best_model_name}")
    best_stats = valid_results[best_model_name]
    print(f"   📊 RMSE: {best_stats['RMSE']:.3f}")
    print(f"   📊 MAE: {best_stats['MAE']:.3f}")
    print(f"   📊 R²: {best_stats['R²']:.3f}")
    
    # Update model data
    model_data['best_model_name'] = best_model_name
    model_data['best_model'] = best_model_info
    model_data['evaluation_results'] = results
    model_data['evaluation_timestamp'] = pd.Timestamp.now().isoformat()
    
    # Save updated model data
    print(f"\n💾 Saving updated model data...")
    joblib.dump(model_data, 'models/optimal_moisture_models.pkl')
    
    print(f"✅ Updated model file saved!")
    print(f"🎉 Your Flask API should now work with best model: {best_model_name}")
    
    return True

if __name__ == "__main__":
    print("🚀 FIXING MODEL SELECTION")
    print("=" * 50)
    
    success = evaluate_models_and_select_best()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("Now you can run: python flask_api.py")
    else:
        print("\n❌ FAILED!")
        print("You may need to retrain models: python train_models.py")
