import joblib
import pandas as pd

def debug_model_file():
    """Debug script to check what's in the model file"""
    try:
        print("🔍 Loading model file...")
        model_data = joblib.load('models/optimal_moisture_models.pkl')
        
        print(f"📦 Model file type: {type(model_data)}")
        print(f"📋 Keys in model data: {list(model_data.keys()) if isinstance(model_data, dict) else 'Not a dict'}")
        
        if isinstance(model_data, dict):
            for key, value in model_data.items():
                print(f"  - {key}: {type(value)}")
                
                # If it's a nested dict, show its keys too
                if isinstance(value, dict):
                    print(f"    └─ Keys: {list(value.keys())}")
        
        # Check specific keys we're looking for
        expected_keys = ['models', 'best_model_name', 'best_model', 'feature_names', 'training_timestamp']
        print(f"\n🔍 Checking for expected keys:")
        for key in expected_keys:
            exists = key in model_data if isinstance(model_data, dict) else False
            print(f"  - {key}: {'✅' if exists else '❌'}")
            
            if exists and key == 'models':
                print(f"    └─ Available models: {list(model_data[key].keys())}")
        
        return model_data
        
    except Exception as e:
        print(f"❌ Error loading model file: {e}")
        return None

if __name__ == "__main__":
    debug_model_file()