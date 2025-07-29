import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler, PowerTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import warnings
warnings.filterwarnings('ignore')

class MoisturePredictionPipeline:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.feature_columns = None
        self.target_column = "Soil Moisture"
        
    def prepare_data(self, data_path=None, df=None):
        """
        Prepare data for training. Either pass data_path or df directly.
        """
        if df is None and data_path is None:
            raise ValueError("Either data_path or df must be provided")
            
        if df is None:
            # Load your data here - adjust based on your data source
            df = pd.read_csv(data_path)
        
        # Convert timestamps
        if 'devicetimestamp' in df.columns:
            df['devicetimestamp'] = pd.to_datetime(df['devicetimestamp'])
            
            # Create time features
            df['hour'] = df['devicetimestamp'].dt.hour
            df['weekday'] = df['devicetimestamp'].dt.weekday
            df['month'] = df['devicetimestamp'].dt.month
            df['day_of_year'] = df['devicetimestamp'].dt.dayofyear
        
        # Handle missing target values
        df_clean = df.dropna(subset=[self.target_column])
        
        # Define feature columns (adjust based on your actual columns)
        sensor_cols = [col for col in df_clean.columns if col not in [
            'deviceid', 'devicetimestamp', 'dbtimestamp', 'dataid', 
            'devicedataid', 'sensorid', 'errorid', 'error', 'errormessage'
        ]]
        
        # Remove target from features
        feature_cols = [col for col in sensor_cols if col != self.target_column]
        self.feature_columns = feature_cols
        
        X = df_clean[feature_cols]
        y = df_clean[self.target_column]
        
        return X, y, df_clean
    
    def create_models(self):
        """Create different model pipelines"""
        
        # Linear Regression with preprocessing
        self.models['Linear_Regression'] = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', RobustScaler()),
            ('power', PowerTransformer(method='yeo-johnson')),
            ('model', LinearRegression())
        ])
        
        # Random Forest (handles missing values well)
        self.models['Random_Forest'] = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('model', RandomForestRegressor(
                n_estimators=100, 
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ))
        ])
        
        # Gradient Boosting
        self.models['Gradient_Boosting'] = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('model', GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ))
        ])
        

    def train_and_evaluate(self, X, y):
        """Train all models and find the best one"""
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        results = {}
        
        print("Training and evaluating models...")
        print("-" * 50)
        
        for name, model in self.models.items():
            print(f"Training {name}...")
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()
                
                results[name] = {
                    'RMSE': rmse,
                    'MAE': mae,
                    'R²': r2,
                    'CV_R²_mean': cv_mean,
                    'CV_R²_std': cv_std,
                    'model': model
                }
                
                print(f"{name} → RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}, CV_R²: {cv_mean:.4f}±{cv_std:.4f}")
                
            except Exception as e:
                print(f"Error training {name}: {e}")
                continue
        
        # Find best model based on R² score
        if results:
            best_name = max(results.keys(), key=lambda k: results[k]['R²'])
            self.best_model = results[best_name]['model']
            self.best_model_name = best_name
            
            print("-" * 50)
            print(f"Best model: {best_name} (R² = {results[best_name]['R²']:.4f})")
        
        return results
    
    def evaluate_model(self, X_val, y_val):
        """Evaluate the best model based on validation data."""
        if self.models:  # Check if there are any models
            # Use the best model (for example, Random Forest)
            model = self.models.get(self.best_model_name)  # This assumes 'best_model_name' is set to Random_Forest
            if model:
                y_pred = model.predict(X_val)
                rmse = np.sqrt(mean_squared_error(y_val, y_pred))
                mae = mean_absolute_error(y_val, y_pred)
                r2 = r2_score(y_val, y_pred)
                print(f"Evaluation for {self.best_model_name}: RMSE: {rmse}, MAE: {mae}, R²: {r2}")
            else:
                print("No model found in 'self.models'")
        else:
            print("No models available to evaluate")

    def predict_future(self, recent_data, days_ahead=30):
        """
        Predict future moisture values
        Args:
            recent_data: DataFrame with recent sensor readings
            days_ahead: Number of days to predict
        """
        if self.best_model is None:
            raise ValueError("No trained model available. Train models first.")
        
        predictions = []
        
        # Use the most recent data point as starting point
        if len(recent_data) > 0:
            last_row = recent_data.iloc[-1:][self.feature_columns]
            
            # Simple approach: predict each day using the model
            for day in range(days_ahead):
                try:
                    pred = self.best_model.predict(last_row)[0]
                    predictions.append(max(0, min(100, pred)))  # Clamp between 0-100%
                    
                    # For next prediction, you might want to update some features
                    # This is a simplified approach - you might want to be more sophisticated
                    
                except Exception as e:
                    print(f"Error predicting day {day + 1}: {e}")
                    # Fallback to previous prediction or average
                    if predictions:
                        predictions.append(predictions[-1])
                    else:
                        predictions.append(50.0)  # Default fallback
        else:
            # No recent data, return default values
            predictions = [50.0] * days_ahead
        
        return predictions
    
    def save_model(self, filepath):
        """Save the best trained model"""
        if self.best_model is None:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.best_model,
            'model_name': self.best_model_name,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a trained model"""
        model_data = joblib.load(filepath)
        
        self.best_model = model_data['model']
        self.best_model_name = model_data['model_name']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']
        
        print(f"Model loaded: {self.best_model_name}")

# Example usage:
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = MoisturePredictionPipeline()
    
    # Create models
    pipeline.create_models()
    
    # Note: You'll need to adapt this to your actual data loading
    # For now, this is a placeholder
    print("Pipeline created successfully!")
    print("Next steps:")
    print("1. Load your preprocessed data")
    print("2. Call pipeline.prepare_data(df=your_dataframe)")
    print("3. Call pipeline.train_and_evaluate(X, y)")
    print("4. Save the model with pipeline.save_model('model.pkl')")
