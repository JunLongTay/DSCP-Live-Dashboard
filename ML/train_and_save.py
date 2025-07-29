import os
import pandas as pd
import joblib
import requests
from ml_pipeline_fixed import MoisturePredictionPipeline

def fetch_live_detailed_data():
    url = "http://localhost:3001/moisture-detailed?bucket_min=2&window_min=10080"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data)

def train_and_save_model(df):
    pipeline = MoisturePredictionPipeline()
    pipeline.create_models()
    X, y, _ = pipeline.prepare_data(df=df)
    pipeline.train_and_evaluate(X, y)
    os.makedirs("models", exist_ok=True)
    pipeline.save_model("models/moisture_predictor.pkl")

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
