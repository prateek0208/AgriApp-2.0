import joblib
import pandas as pd
import streamlit as st

def get_predicted_price(crop_name, n, p, k, ph, rainfall, acres):
    try:
        # 1. Load the model you just moved from Kaggle
        model = joblib.load('models/price_model.pkl')
        
        # 2. Create the input features (Order must match Kaggle training!)
        # Features used: N, P, K, ph, rainfall, acres
        input_data = pd.DataFrame([[n, p, k, ph, rainfall, acres]], 
                                 columns=['N', 'P', 'K', 'ph', 'rainfall', 'acres'])
        
        # 3. Predict
        prediction = model.predict(input_data)[0]
        
        return round(float(prediction), 2)
        
    except Exception as e:
        # This will help us debug if it still shows 0.0
        print(f"DEBUG: Price Prediction Error -> {e}")
        return 0.0