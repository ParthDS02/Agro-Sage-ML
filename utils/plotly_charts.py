# utils/plotly_charts.py
"""Interactive Plotly visualizations."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def plot_correlation_heatmap(df):
    """
    Create interactive correlation heatmap.
    
    Args:
        df: Dataset with numeric columns
    """
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Feature Correlation Heatmap",
        width=700,
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_crop_distribution(df):
    """
    Create interactive bar chart of crop distribution.
    
    Args:
        df: Dataset with 'label' column
    """
    crop_counts = df['label'].value_counts().reset_index()
    crop_counts.columns = ['Crop', 'Count']
    
    fig = px.bar(
        crop_counts,
        x='Crop',
        y='Count',
        title='Crop Distribution',
        color='Count',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_feature_boxplot(df, feature):
    """
    Create box plot for feature distribution by crop.
    
    Args:
        df: Dataset
        feature: Column name to plot
    """
    fig = px.box(
        df,
        x='label',
        y=feature,
        title=f'{feature} Distribution by Crop',
        color='label'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_3d_scatter(df):
    """
    Create 3D scatter plot of NPK values.
    
    Args:
        df: Dataset with N, P, K columns
    """
    fig = px.scatter_3d(
        df,
        x='N',
        y='P',
        z='K',
        color='label',
        title='NPK Distribution by Crop',
        opacity=0.7
    )
    
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

def plot_feature_histogram(df, feature):
    """
    Create histogram with KDE curve.
    
    Args:
        df: Dataset
        feature: Column name to plot
    """
    fig = px.histogram(
        df,
        x=feature,
        marginal='box',
        title=f'{feature} Distribution',
        nbins=30,
        color_discrete_sequence=['green']
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
