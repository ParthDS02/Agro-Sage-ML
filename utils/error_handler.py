# utils/error_handler.py
# Simple error handling utilities

import streamlit as st
import pickle
import os

def load_model_safe(filepath):
    """
    Safely load a pickle model file with error handling.
    
    Args:
        filepath: Path to the pickle file
    
    Returns:
        Loaded model or None if error
    """
    try:
        if not os.path.exists(filepath):
            st.error(f"❌ Model file not found: `{filepath}`")
            st.info("💡 Please ensure the model file exists in the correct location.")
            return None
        
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        
        return model
        
    except pickle.UnpicklingError:
        st.error(f"❌ Error loading model file: `{filepath}`")
        st.info("💡 The model file may be corrupted. Try retraining the model.")
        return None
        
    except Exception as e:
        st.error(f"❌ Unexpected error loading model: {str(e)}")
        return None

def safe_prediction(model, features, label_mapping):
    """
    Make prediction with error handling.
    
    Args:
        model: Trained model
        features: Input features
        label_mapping: Crop code to name mapping
    
    Returns:
        tuple: (success, crop_name or error_message)
    """
    try:
        # Make prediction
        prediction = model.predict(features)
        crop_code = int(prediction[0])
        crop_name = label_mapping.get(crop_code, "Unknown")
        
        return True, crop_name
        
    except ValueError as e:
        return False, "Invalid input values. Please check your inputs."
        
    except Exception as e:
        return False, f"Prediction error: {str(e)}"

def display_error_message(message, help_text=None):
    """
    Display a formatted error message.
    
    Args:
        message: Error message to display
        help_text: Optional help text
    """
    st.error(f"❌ {message}")
    
    if help_text:
        st.info(f"💡 {help_text}")

def check_dependencies():
    """
    Check if all required files exist.
   
    Returns:
        bool: True if all files present
    """
    required_files = [
        'model/crop_model.pkl',
        'model/minmax_scaler.pkl',
        'model/stand_scaler.pkl',
        'dataset/Crop_recommendation.csv'
    ]
    
    missing_files = []
    
    for filepath in required_files:
        if not os.path.exists(filepath):
            missing_files.append(filepath)
    
    if missing_files:
        st.error("Missing required files:")
        for f in missing_files:
            st.write(f"- `{f}`")
        st.info("Please ensure all model files and dataset are in the correct location.")
        return False
    
    return True
