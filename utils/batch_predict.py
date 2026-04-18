# utils/batch_predict.py
"""Batch prediction from CSV file upload."""

import streamlit as st
import pandas as pd

def validate_csv_columns(df):
    """
    Check if CSV has required columns.
    
    Args:
        df: Uploaded dataframe
    
    Returns:
        bool: True if valid
    """
    required_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        return False
    
    return True

def predict_batch(df, model, mx_scaler, sc_scaler, label_mapping):
    """
    Make predictions for multiple rows.
    
    Args:
        df: DataFrame with input features
        model: Trained model
        mx_scaler: MinMax scaler
        sc_scaler: Standard scaler
        label_mapping: Crop code to name mapping
    
    Returns:
        DataFrame: Original data with predictions
    """
    try:
        # Extract features
        features = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
        
        # Scale features
        mx_scaled = mx_scaler.transform(features)
        scaled_features = sc_scaler.transform(mx_scaled)
        
        # Predict
        predictions = model.predict(scaled_features)
        
        # Map to crop names
        df['Recommended_Crop'] = [label_mapping.get(int(pred), 'Unknown') 
                                   for pred in predictions]
        
        # Add confidence if available
        if hasattr(model, 'predict_proba'):
            probas = model.predict_proba(scaled_features)
            df['Confidence_%'] = [max(p) * 100 for p in probas]
        
        return df
        
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        return None

def download_csv(df, filename="predictions.csv"):
    """
    Create download button for results.
    
    Args:
        df: DataFrame to download
        filename: Output filename
    """
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Results",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

def show_sample_format():
    """Display sample CSV format for users."""
    st.info("**Required CSV Format:**")
    sample_data = {
        'N': [90, 85],
        'P': [42, 58],
        'K': [43, 41],
        'temperature': [20.8, 21.7],
        'humidity': [82.0, 80.3],
        'ph': [6.5, 7.0],
        'rainfall': [202.9, 226.6]
    }
    st.dataframe(pd.DataFrame(sample_data))
