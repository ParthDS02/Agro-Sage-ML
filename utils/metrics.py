# utils/metrics.py
# Display model performance metrics

import streamlit as st
import numpy as np

def display_model_info():
    """
    Display overall model performance information.
    Should be called on the prediction page.
    """
    st.info("**Model Information**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Model Accuracy", "96.5%")
    
    with col2:
        st.metric("Total Crops", "22")
    
    with col3:
        st.metric("Dataset Size", "2,200")

def show_prediction_confidence(model, features):
    """
    Calculate and display prediction confidence.
    
    Args:
        model: Trained ML model
        features: Preprocessed input features
    
    Returns:
        float: Confidence score (0-100)
    """
    try:
        # Get prediction probabilities
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)
            confidence = np.max(proba) * 100
            
            # Display confidence meter
            if confidence >= 90:
                st.success(f"🎯 Confidence: **{confidence:.1f}%** (Very High)")
            elif confidence >= 75:
                st.info(f"✅ Confidence: **{confidence:.1f}%** (High)")
            elif confidence >= 60:
                st.warning(f"⚠️ Confidence: **{confidence:.1f}%** (Moderate)")
            else:
                st.warning(f"⚠️ Confidence: **{confidence:.1f}%** (Low - Consider expert advice)")
            
            return confidence
        else:
            # Model doesn't support probability predictions
            st.info("Model confidence calculation not available")
            return None
            
    except Exception as e:
        st.warning("Unable to calculate confidence score")
        return None

def show_top_predictions(model, features, label_mapping, top_n=3):
    """
    Show top N crop predictions with probabilities.
    
    Args:
        model: Trained ML model
        features: Preprocessed input features
        label_mapping: Dictionary mapping codes to crop names
        top_n: Number of top predictions to show
    """
    try:
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            
            # Get top N predictions
            top_indices = np.argsort(proba)[-top_n:][::-1]
            
            st.write("**Top Recommendations:**")
            for i, idx in enumerate(top_indices, 1):
                crop_code = idx + 1  # Adjust for 1-indexed mapping
                crop_name = label_mapping.get(crop_code, "Unknown")
                probability = proba[idx] * 100
                
                # Display with progress bar
                st.write(f"{i}. **{crop_name.capitalize()}** - {probability:.1f}%")
                st.progress(probability / 100)
                
    except Exception as e:
        pass  # Silently skip if not available
