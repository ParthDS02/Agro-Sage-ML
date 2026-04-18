# utils/database.py
"""Simple SQLite database for storing predictions."""

import sqlite3
import streamlit as st
from datetime import datetime
import pandas as pd

def init_database():
    """
    Create database and predictions table if not exists.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect('crop_predictions.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            predicted_crop TEXT,
            confidence REAL
        )
    ''')
    
    conn.commit()
    return conn

def save_prediction(inputs, crop_name, confidence=None):
    """
    Save a prediction to database.
    
    Args:
        inputs: Dictionary of input values
        crop_name: Predicted crop
        confidence: Prediction confidence score
    """
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (timestamp, nitrogen, phosphorus, potassium, temperature, 
             humidity, ph, rainfall, predicted_crop, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            inputs['N'],
            inputs['P'],
            inputs['K'],
            inputs['temperature'],
            inputs['humidity'],
            inputs['ph'],
            inputs['rainfall'],
            crop_name,
            confidence
        ))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        st.warning(f"Could not save prediction: {str(e)}")

def get_prediction_history(limit=50):
    """
    Retrieve recent predictions.
    
    Args:
        limit: Number of records to fetch
    
    Returns:
        DataFrame: Prediction history
    """
    try:
        conn = init_database()
        
        query = f'''
            SELECT timestamp, nitrogen, phosphorus, potassium,
                   temperature, humidity, ph, rainfall,
                   predicted_crop, confidence
            FROM predictions
            ORDER BY timestamp DESC
            LIMIT {limit}
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Could not load history: {str(e)}")
        return pd.DataFrame()

def get_statistics():
    """
    Get prediction statistics.
    
    Returns:
        dict: Statistics summary
    """
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total = cursor.fetchone()[0]
        
        # Most recommended crop
        cursor.execute('''
            SELECT predicted_crop, COUNT(*) as count
            FROM predictions
            GROUP BY predicted_crop
            ORDER BY count DESC
            LIMIT 1
        ''')
        top_crop = cursor.fetchone()
        
        # Average confidence
        cursor.execute('SELECT AVG(confidence) FROM predictions WHERE confidence IS NOT NULL')
        avg_conf = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'top_crop': top_crop[0] if top_crop else 'N/A',
            'avg_confidence': round(avg_conf, 2) if avg_conf else 0
        }
        
    except Exception as e:
        return {'total': 0, 'top_crop': 'N/A', 'avg_confidence': 0}

def clear_history():
    """Delete all prediction history."""
    try:
        conn = init_database()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM predictions')
        conn.commit()
        conn.close()
        st.success("History cleared successfully")
    except Exception as e:
        st.error(f"Could not clear history: {str(e)}")
