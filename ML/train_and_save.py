import os
import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings('ignore')

class OptimalMoisturePrediction:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        
    def prepare_features(self, df):
        """Enhanced feature engineering for soil moisture prediction"""
        df = df.copy()
        
        # Time-based features
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp').sort_index()
            
            # Cyclical time features (better than categorical)
            df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
            df['day_sin'] = np.sin(2 * np.pi * df.index.dayofyear / 365)
            df['day_cos'] = np.cos(2 * np.pi * df.index.dayofyear / 365)
            df['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
            df['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)
        
        # Lag features for soil moisture
        if 'Soil Moisture' in df.columns:
            for lag in [1, 2, 3, 6, 12, 24]:  # hours/days depending on frequency
                df[f'moisture_lag_{lag}'] = df['Soil Moisture'].shift(lag)
            
            # Rolling statistics
            for window in [3, 7, 14]:
                df[f'moisture_rolling_mean_{window}'] = df['Soil Moisture'].rolling(window).mean()
                df[f'moisture_rolling_std_{window}'] = df['Soil Moisture'].rolling(window).std()
        
        # Weather-based features if available
        if 'temperature' in df.columns:
            df['temp_moisture_ratio'] = df['temperature'] / (df['Soil Moisture'] + 1e-6)
        
        # NPK ratios and interactions
        npk_cols = ['npk_n', 'npk_p', 'npk_k']
        if all(col in df.columns for col in npk_cols):
            df['npk_total'] = df[npk_cols].sum(axis=1)
            for col in npk_cols:
                df[f'{col}_ratio'] = df[col] / (df['npk_total'] + 1e-6)
        
        return df
    
    def evaluate_stationarity(self, series, verbose=True):
        """Check if series is stationary"""
        series = series.replace([np.inf, -np.inf], np.nan).dropna()
        adf_result = adfuller(series)
        
        if verbose:
            print(f"ADF Statistic: {adf_result[0]:.4f}")
            print(f"p-value: {adf_result[1]:.4f}")
        
        is_stationary = adf_result[1] < 0.05
        return is_stationary, adf_result
    
    def find_optimal_arima_order(self, series, max_p=3, max_d=2, max_q=3):
        """Auto-select optimal ARIMA parameters using AIC"""
        best_aic = np.inf
        best_order = None
        best_model = None
        
        print("Searching for optimal ARIMA parameters...")
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted_model = model.fit()
                        
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_order = (p, d, q)
                            best_model = fitted_model
                            
                    except:
                        continue
        
        print(f"Best ARIMA order: {best_order} with AIC: {best_aic:.2f}")
        return best_order, best_model
    
    def train_arima_model(self, df):
        """Train optimized ARIMA model"""
        series = df['Soil Moisture'].dropna()
        
        if len(series) < 50:
            print("Not enough data for ARIMA model")
            return None
        
        # Check stationarity
        is_stationary, _ = self.evaluate_stationarity(series)
        
        # Find optimal parameters
        best_order, arima_model = self.find_optimal_arima_order(series)
        
        if arima_model:
            self.models['ARIMA'] = {
                'model': arima_model,
                'order': best_order,
                'is_stationary': is_stationary,
                'last_values': series.tail(max(best_order)).tolist()  # Store for forecasting
            }
            print("✅ ARIMA model trained successfully")
        
        return arima_model
    
    def train_sarima_model(self, df, seasonal_period=24):
        """Train SARIMA model for seasonal patterns"""
        series = df['Soil Moisture'].dropna()
        
        if len(series) < seasonal_period * 2:
            print(f"Not enough data for SARIMA (need at least {seasonal_period * 2} points)")
            return None
        
        try:
            # Try different SARIMA configurations
            configs = [
                ((1, 1, 1), (1, 1, 1, seasonal_period)),
                ((2, 1, 0), (1, 1, 1, seasonal_period)),
                ((1, 1, 2), (1, 1, 1, seasonal_period))
            ]
            
            best_aic = np.inf
            best_model = None
            best_config = None
            
            for order, seasonal_order in configs:
                try:
                    model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
                    fitted_model = model.fit(disp=False)
                    
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                        best_config = (order, seasonal_order)
                        
                except:
                    continue
            
            if best_model:
                self.models['SARIMA'] = {
                    'model': best_model,
                    'order': best_config[0],
                    'seasonal_order': best_config[1],
                    'seasonal_period': seasonal_period,
                    'aic': best_aic
                }
                print(f"✅ SARIMA model trained with AIC: {best_aic:.2f}")
                return best_model
            
        except Exception as e:
            print(f"❌ SARIMA training failed: {e}")
            return None
    
    def train_ml_model(self, df):
        """Train Random Forest with engineered features"""
        # Prepare features
        df_features = self.prepare_features(df)
        df_features = df_features.dropna()
        
        if len(df_features) < 100:
            print("Not enough data for ML model")
            return None
        
        # Features and target
        feature_cols = [col for col in df_features.columns 
                       if col != 'Soil Moisture' and 'devicename' not in col.lower()]
        
        X = df_features[feature_cols]
        y = df_features['Soil Moisture']
        
        # Store feature names for later use
        self.feature_names = feature_cols
        
        # Time series split for validation
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        print("Training Random Forest with cross-validation...")
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            rf_model.fit(X_train, y_train)
            y_pred = rf_model.predict(X_val)
            score = r2_score(y_val, y_pred)
            scores.append(score)
            print(f"  Fold {fold + 1} R² Score: {score:.3f}")
        
        avg_score = np.mean(scores)
        print(f"✅ Random Forest CV R² Score: {avg_score:.3f}")
        
        # Train final model on all data
        final_rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        final_rf.fit(X, y)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': final_rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10).to_string(index=False))
        
        self.models['RandomForest'] = {
            'model': final_rf,
            'feature_names': feature_cols,
            'cv_score': avg_score,
            'feature_importance': feature_importance
        }
        
        return final_rf
    
    def compare_models(self, df, test_days=30):
        """Compare all models on holdout data"""
        print(f"\n{'='*50}")
        print("MODEL COMPARISON ON LAST {test_days} DAYS")
        print(f"{'='*50}")
        
        if len(df) < test_days + 50:
            print(f"❌ Not enough data for {test_days}-day holdout testing")
            return {}
        
        # Split data for testing
        split_point = len(df) - test_days
        train_data = df.iloc[:split_point]
        test_data = df.iloc[split_point:]
        
        results = {}
        
        for model_name, model_info in self.models.items():
            try:
                print(f"\nTesting {model_name}...")
                
                if model_name == 'ARIMA':
                    forecast = model_info['model'].forecast(steps=len(test_data))
                    y_pred = forecast
                    
                elif model_name == 'SARIMA':
                    forecast = model_info['model'].forecast(steps=len(test_data))
                    y_pred = forecast
                    
                elif model_name == 'RandomForest':
                    # Prepare test features
                    test_df = df.iloc[split_point:]
                    test_features = self.prepare_features(test_df)
                    X_test = test_features[model_info['feature_names']].dropna()
                    
                    if len(X_test) == 0:
                        print(f"  ❌ No valid features for {model_name}")
                        continue
                        
                    y_pred = model_info['model'].predict(X_test)
                
                # Calculate metrics
                y_true = test_data['Soil Moisture'].values[:len(y_pred)]
                
                mae = mean_absolute_error(y_true, y_pred)
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                r2 = r2_score(y_true, y_pred)
                
                results[model_name] = {
                    'MAE': mae,
                    'RMSE': rmse,
                    'R²': r2,
                    'predictions': len(y_pred)
                }
                
                print(f"  MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.3f}")
                
            except Exception as e:
                print(f"  ❌ {model_name} evaluation failed: {e}")
                results[model_name] = {'error': str(e)}
        
        # Select best model based on lowest RMSE
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        if valid_results:
            self.best_model_name = min(valid_results.keys(), key=lambda x: valid_results[x]['RMSE'])
            self.best_model = self.models[self.best_model_name]
            
            print(f"\n🏆 BEST MODEL: {self.best_model_name}")
            print(f"   RMSE: {valid_results[self.best_model_name]['RMSE']:.3f}")
            print(f"   R²: {valid_results[self.best_model_name]['R²']:.3f}")
        else:
            print("❌ No valid models found")
        
        return results
    
    def save_models(self, filepath='models/optimal_moisture_models.pkl'):
        """Save all trained models"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'models': self.models,
            'best_model_name': self.best_model_name,
            'best_model': self.best_model,
            'feature_names': self.feature_names,
            'training_timestamp': pd.Timestamp.now().isoformat()
        }
        
        joblib.dump(model_data, filepath)
        print(f"✅ All models saved to {filepath}")
        
        # Save summary
        summary_path = filepath.replace('.pkl', '_summary.txt')
        with open(summary_path, 'w') as f:
            f.write(f"Model Training Summary\n")
            f.write(f"=====================\n")
            f.write(f"Training Date: {model_data['training_timestamp']}\n")
            f.write(f"Best Model: {self.best_model_name}\n\n")
            
            for model_name in self.models:
                f.write(f"{model_name}: ✅ Trained\n")
        
        print(f"✅ Summary saved to {summary_path}")

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

def preprocess_data(df):
    """Preprocess the fetched data"""
    if df is None or df.empty:
        return None
    
    print(f"📊 Raw data shape: {df.shape}")
    print(f"📋 Columns: {df.columns.tolist()}")
    
    # Rename moisture column
    if "moisture" in df.columns:
        df.rename(columns={"moisture": "Soil Moisture"}, inplace=True)
        print("🔁 Renamed 'moisture' to 'Soil Moisture'")
    
    # Convert timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        print("📆 Converted timestamp to datetime")
    
    # Fill missing values
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if col != 'Soil Moisture':
            df[col].fillna(df[col].median(), inplace=True)
    
    # Remove devicename if present
    df = df.drop(columns=["devicename"], errors="ignore")
    
    print(f"✅ Preprocessed data shape: {df.shape}")
    return df

def main():
    print("🚀 STARTING OPTIMAL MOISTURE PREDICTION TRAINING")
    print("=" * 60)
    
    # Fetch data
    print("\n📡 Fetching live sensor data...")
    df = fetch_live_detailed_data()
    
    if df is None:
        print("❌ Failed to fetch data. Exiting.")
        return
    
    # Preprocess data
    print("\n🔧 Preprocessing data...")
    df = preprocess_data(df)
    
    if df is None or len(df) < 100:
        print("❌ Insufficient data for training. Need at least 100 records.")
        return
    
    # Initialize predictor
    predictor = OptimalMoisturePrediction()
    
    # Train models
    print(f"\n🤖 Training models on {len(df)} records...")
    
    # Train ARIMA
    print("\n1️⃣ Training ARIMA...")
    predictor.train_arima_model(df)
    
    # Train SARIMA (adjust seasonal_period based on your data frequency)
    print("\n2️⃣ Training SARIMA...")
    seasonal_period = 24 if len(df) > 48 else 12  # Adjust based on data frequency
    predictor.train_sarima_model(df, seasonal_period=seasonal_period)
    
    # Train Random Forest
    print("\n3️⃣ Training Random Forest...")
    predictor.train_ml_model(df)
    
    # Compare models
    if len(predictor.models) > 0:
        print("\n📈 Comparing model performance...")
        results = predictor.compare_models(df, test_days=min(30, len(df) // 4))
        
        # Save models
        print("\n💾 Saving trained models...")
        predictor.save_models()
        
        print(f"\n🎉 TRAINING COMPLETED!")
        print(f"📊 Models trained: {list(predictor.models.keys())}")
        if predictor.best_model_name:
            print(f"🏆 Best model: {predictor.best_model_name}")
            print(f"📁 Models saved to: models/optimal_moisture_models.pkl")
        
    else:
        print("❌ No models were successfully trained.")

if __name__ == "__main__":
    main()