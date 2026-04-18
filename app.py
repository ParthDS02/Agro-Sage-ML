import streamlit as st
import pandas as pd
import pickle

# Import all utilities
from utils import eda
from utils import validation
from utils import metrics
from utils import error_handler
from utils import plotly_charts
from utils import database
from utils import feedback

# Page configuration
st.set_page_config(page_title="Agro Sage", page_icon="🌱", layout="wide")

# Check dependencies first
if not error_handler.check_dependencies():
    st.stop()

# Initialize database
database.init_database()
feedback.init_feedback_db()

# Load model and scalers safely
model = error_handler.load_model_safe('model/crop_model.pkl')
mx = error_handler.load_model_safe('model/minmax_scaler.pkl')
sc = error_handler.load_model_safe('model/stand_scaler.pkl')

if not all([model, mx, sc]):
    st.error("Failed to load models. Please check the model files.")
    st.stop()

# Manual label mapping
label_mapping = {
    1: 'rice', 2: 'maize', 3: 'jute', 4: 'cotton', 5: 'coconut',
    6: 'papaya', 7: 'orange', 8: 'apple', 9: 'muskmelon', 10: 'watermelon',
    11: 'grapes', 12: 'mango', 13: 'banana', 14: 'pomegranate', 15: 'lentil',
    16: 'blackgram', 17: 'mungbean', 18: 'mothbeans', 19: 'pigeonpeas',
    20: 'kidneybeans', 21: 'chickpea', 22: 'coffee'
}

# Load dataset for EDA
df = pd.read_csv('dataset/Crop_recommendation.csv')

# Sidebar Menu
menu = ["Home", "Predict", "EDA", "History", "Feedback"]
choice = st.sidebar.selectbox("Menu", menu)

# App Statistics in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Statistics of Agro Sage")
stats = database.get_statistics()
st.sidebar.metric("Total Predictions", stats['total'])
st.sidebar.metric("Top Crop", stats['top_crop'])
st.sidebar.metric("Avg Confidence", f"{stats['avg_confidence']}%")

# --- HOME PAGE ---
if choice == "Home":
    st.image("aseets/Gemini.png", width=700)
    
    st.title("Agro Sage")
    st.markdown("""
    ## Welcome to **Agro Sage** 🌱
    Agro Sage is your smart crop recommendation assistant, built to support farmers, agri-startups, and researchers in identifying the **most suitable crop** based on:
    
    - 🌿 Soil Nutrients (N, P, K), 🌡️ Temperature, 💧 Humidity, 🧪 pH level, 🌧️ Rainfall

    Creted By :- Parth B Mistry
    
    Let data guide your farming decisions for **maximum yield and sustainability**.
    """)

# --- PREDICTION PAGE ---
elif choice == "Predict":
    st.header("🌱 Crop Prediction")
    
    # Display model info
    metrics.display_model_info()
    
    st.subheader("Enter Soil & Climate Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_n, max_n = validation.get_input_info('N')
        N = st.number_input(f"Nitrogen (N) [{min_n}-{max_n}]", min_value=0, value=50)
        
        min_p, max_p = validation.get_input_info('P')
        P = st.number_input(f"Phosphorous (P) [{min_p}-{max_p}]", min_value=0, value=50)
        
        min_k, max_k = validation.get_input_info('K')
        K = st.number_input(f"Potassium (K) [{min_k}-{max_k}]", min_value=0, value=40)
        
        min_temp, max_temp = validation.get_input_info('temperature')
        temperature = st.number_input(f"Temperature °C [{min_temp:.1f}-{max_temp:.1f}]", value=25.0)
    
    with col2:
        min_hum, max_hum = validation.get_input_info('humidity')
        humidity = st.number_input(f"Humidity % [{min_hum:.1f}-{max_hum:.1f}]", value=70.0)
        
        min_ph, max_ph = validation.get_input_info('ph')
        ph = st.number_input(f"pH Level [{min_ph:.1f}-{max_ph:.1f}]", value=6.5)
        
        min_rain, max_rain = validation.get_input_info('rainfall')
        rainfall = st.number_input(f"Rainfall mm [{min_rain:.1f}-{max_rain:.1f}]", value=100.0)
    
    if st.button("🌿 Recommend Crop"):
        # Validate inputs
        inputs = {
            'N': N, 'P': P, 'K': K,
            'temperature': temperature,
            'humidity': humidity,
            'ph': ph,
            'rainfall': rainfall
        }
        
        if validation.validate_all_inputs(inputs):
            # Make prediction
            mx_scaled = mx.transform([[N, P, K, temperature, humidity, ph, rainfall]])
            features = sc.transform(mx_scaled)
            
            success, result = error_handler.safe_prediction(model, features, label_mapping)
            
            if success:
                st.success(f"✅ Recommended Crop: **{result.capitalize()}**")
                
                # Show confidence
                confidence = metrics.show_prediction_confidence(model, features)
                
                # Show top 3 predictions
                st.write("---")
                metrics.show_top_predictions(model, features, label_mapping, top_n=3)
                
                # Save to database
                database.save_prediction(inputs, result, confidence)
                
                # Collect feedback
                st.write("---")
                feedback.collect_feedback(result)
            else:
                error_handler.display_error_message(result)

# --- EDA PAGE ---
elif choice == "EDA":
    st.header("📊 Exploratory Data Analysis")
    
    eda_option = st.selectbox("Select Visualization", [
        "Plotly Correlation Heatmap",
        "Plotly Crop Distribution",
        "Plotly 3D NPK Scatter",
        "Plotly Feature Boxplot",
        "Plotly Feature Histogram",
        "Interactive Data Table",
        "Statistical Summary",
        "Crop Category Table"
    ])
    
    if eda_option == "Plotly Correlation Heatmap":
        plotly_charts.plot_correlation_heatmap(df)
        
    elif eda_option == "Plotly Crop Distribution":
        plotly_charts.plot_crop_distribution(df)
        
    elif eda_option == "Plotly 3D NPK Scatter":
        plotly_charts.plot_3d_scatter(df)
        
    elif eda_option == "Plotly Feature Boxplot":
        feature = st.selectbox("Select Feature", 
                              ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
        plotly_charts.plot_feature_boxplot(df, feature)
        
    elif eda_option == "Plotly Feature Histogram":
        feature = st.selectbox("Select Feature", 
                              ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
        plotly_charts.plot_feature_histogram(df, feature)
        
    elif eda_option == "Interactive Data Table":
        eda.show_data(df)
        
    elif eda_option == "Statistical Summary":
        eda.show_summary(df)
        
    elif eda_option == "Crop Category Table":
        eda.label_distribution_table(df)

# --- HISTORY PAGE ---
elif choice == "History":
    st.header("📜 Prediction History")
    
    # Show statistics
    stats = database.get_statistics()
    st.subheader("Summary")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", stats['total'])
    with col2:
        st.metric("Most Popular Crop", stats['top_crop'])
    with col3:
        st.metric("Average Confidence", f"{stats['avg_confidence']}%")
    
    # Show history table
    st.subheader("Recent Predictions")
    
    limit = st.slider("Number of records to show", min_value=10, max_value=100, value=50)
    history = database.get_prediction_history(limit=limit)
    
    if not history.empty:
        st.dataframe(history)
        
        # Download history
        st.download_button(
            label="📥 Download History",
            data=history.to_csv(index=False),
            file_name="prediction_history.csv",
            mime="text/csv"
        )
        
        # Clear history button
        st.write("---")
        if st.button("🗑️ Clear All History", type="secondary"):
            database.clear_history()
            st.rerun()
    else:
        st.info("No prediction history yet. Make some predictions first!")

# --- FEEDBACK PAGE ---
elif choice == "Feedback":
    st.header("💬 User Feedback")
    
    # Display feedback summary
    feedback.display_feedback_summary()
    
    st.write("---")
    
    # View all feedback
    st.subheader("All Feedback")
    all_feedback = feedback.view_all_feedback()
    
    if not all_feedback.empty:
        st.dataframe(all_feedback)
        
        # Download feedback
        st.download_button(
            label="📥 Download Feedback",
            data=all_feedback.to_csv(index=False),
            file_name="user_feedback.csv",
            mime="text/csv"
        )
    else:
        st.info("No feedback collected yet!")
