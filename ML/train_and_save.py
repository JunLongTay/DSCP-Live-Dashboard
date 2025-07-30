import os
import pandas as pd
import joblib
import requests
from ml_pipeline_fixed import MoisturePredictionPipeline
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import numpy as np

def fetch_live_detailed_data():
    url = "http://localhost:3001/moisture-detailed?bucket_min=2&window_min=10080"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data)

def check_stationarity(series):
    """Check if the series is stationary and handle missing values"""
    
    # Remove any Inf or NaN values before applying ADF test
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    
    result = adfuller(series)
    print(f"ADF Statistic: {result[0]}")
    print(f"p-value: {result[1]}")
    
    if result[1] > 0.05:
        print("Data is non-stationary. Differencing is required.")
        series = series.diff().dropna()  # Apply differencing
    else:
        print("Data is stationary.")
        
    return series

def train_arima_model(df):
    """Train ARIMA model on soil moisture data"""
    
    # Ensure 'Soil Moisture' column has no NaN or Inf values
    df['Soil Moisture'] = df['Soil Moisture'].replace([np.inf, -np.inf], np.nan).dropna()

    # Check if data is stationary and difference if necessary
    df['Soil Moisture'] = check_stationarity(df['Soil Moisture'])

    try:
        # Train ARIMA model (adjust order as necessary)
        arima_model = ARIMA(df['Soil Moisture'], order=(5, 1, 0))  # Example ARIMA order
        arima_model_fit = arima_model.fit()
        print("ARIMA model training completed!")

        # Optionally, forecast future values (e.g., next 30 days)
        forecasted_values = arima_model_fit.forecast(steps=30)
        print(f"Forecasted values for the next 30 days: {forecasted_values}")
        
        # Save ARIMA model
        joblib.dump(arima_model_fit, 'models/arima_model.pkl')
        print("ARIMA model saved to models/arima_model.pkl")
        
    except Exception as e:
        print(f"Error training ARIMA model: {e}")


def train_and_save_model(df):
    """Train the machine learning model and save it"""
    pipeline = MoisturePredictionPipeline()
    pipeline.create_models()

    # Handle missing values in other columns
    df["npk_n"].fillna(0, inplace=True)
    df["npk_p"].fillna(0, inplace=True)
    df["npk_k"].fillna(0, inplace=True)
    df["co2"].fillna(df["co2"].mean(), inplace=True)  # Or 0 for `co2`

    X, y, _ = pipeline.prepare_data(df=df)

    # Split data into train and validation sets for evaluation
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train and evaluate the machine learning model
    pipeline.train_and_evaluate(X_train, y_train)

    # Evaluate on validation data
    pipeline.evaluate_model(X_val, y_val)

    os.makedirs("models", exist_ok=True)
    pipeline.save_model("models/moisture_predictor.pkl")

    # Train and save the ARIMA model
    train_arima_model(df)

if __name__ == "__main__":
    print("📡 Fetching detailed sensor data...")
    df = fetch_live_detailed_data()

    print("📊 Sample data:\n", df.head())
    print("📋 Columns detected:", df.columns.tolist())

    # Rename moisture column
    if "moisture" in df.columns:
        df.rename(columns={"moisture": "Soil Moisture"}, inplace=True)
        print("🔁 Renamed 'moisture' to 'Soil Moisture'")

    # Convert timestamp to datetime and extract time-based features
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["weekday"] = df["timestamp"].dt.weekday
        df["month"] = df["timestamp"].dt.month
        df["day_of_year"] = df["timestamp"].dt.dayofyear
        print("📆 Extracted time features from 'timestamp'")

    # Drop non-numeric or ID columns
    df = df.drop(columns=["timestamp", "devicename"], errors="ignore")

    if df.empty or "Soil Moisture" not in df.columns or df.drop(columns=["Soil Moisture"]).empty:
        print("❌ Not enough valid feature columns to train the model.")
    else:
        print(f"✅ Training model on {len(df)} rows and {len(df.columns) - 1} feature(s)...")
        train_and_save_model(df)
        print("✅ Model training and saving completed.")
