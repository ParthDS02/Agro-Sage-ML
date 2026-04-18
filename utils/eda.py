# utils/eda.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Display the raw dataset
def show_data(df):
    st.subheader("Raw Dataset")
    st.dataframe(df)

# Correlation heatmap (excluding non-numeric columns)
def plot_heatmap(df):
    st.subheader(" Feature Correlation Heatmap")
    
    # Calculate correlation on numeric columns
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    # Display observations
    st.markdown("### Observations from Correlation Heatmap")
    st.markdown("""
    - **Phosphorus and Potassium (P & K)** have a **strong positive correlation (0.74)** – they tend to increase together.
    - **Nitrogen (N) and Phosphorus (P)** show a **slight negative correlation (-0.23)**.
    - **Temperature, Humidity, and Rainfall** have **weak or negligible correlations** with most soil nutrients.
    - **Most variables are weakly correlated**, which is ideal for machine learning as it avoids redundancy.
    - Overall, each feature contributes fairly independently to the crop prediction model.
    """)


# Bar chart of label distribution
def class_distribution(df):
    st.subheader("🌾 Crop Distribution (Count)")
    st.bar_chart(df['label'].value_counts(), color= "#2ecc71") # 2ecc71 is green colors code

# Summary statistics table
def show_summary(df):
    st.subheader("Statistical Summary")
    st.dataframe(df.describe())

# Histogram for any selected numeric feature
def feature_distribution(df):
    st.subheader("Feature Distribution")
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    selected_feature = st.selectbox("Select a feature to visualize", numeric_cols)
    fig, ax = plt.subplots()
    sns.histplot(df[selected_feature], kde=True, color="green", ax=ax)
    st.pyplot(fig)

# Table of label-wise count and percentage
def label_distribution_table(df):
    st.subheader("Crop Category Overview")
    label_counts = df['label'].value_counts().reset_index()
    label_counts.columns = ['Crop', 'Count']
    label_counts['Percentage'] = round((label_counts['Count'] / label_counts['Count'].sum()) * 100, 2)
    st.dataframe(label_counts)
