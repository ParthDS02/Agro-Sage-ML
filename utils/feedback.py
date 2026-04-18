# utils/feedback.py
"""User feedback collection and storage."""

import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd

def init_feedback_db():
    """
    Create feedback table if not exists.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect('crop_predictions.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            predicted_crop TEXT,
            rating INTEGER,
            usefulness TEXT,
            comments TEXT,
            actual_result TEXT
        )
    ''')
    
    conn.commit()
    return conn

def collect_feedback(predicted_crop):
    """
    Display feedback form and collect user input.
    
    Args:
        predicted_crop: The crop that was recommended
    """
    st.write("---")
    st.subheader("Feedback")
    
    with st.form("feedback_form"):
        rating = st.slider(
            "Rate this recommendation (1-5 stars)",
            min_value=1,
            max_value=5,
            value=3
        )
        
        usefulness = st.radio(
            "How useful was this recommendation?",
            ["Very Helpful", "Helpful", "Neutral", "Not Helpful"],
            index=1
        )
        
        comments = st.text_area(
            "Additional comments (optional)",
            placeholder="Share your thoughts..."
        )
        
        actual_result = st.selectbox(
            "If you planted this crop, how was the result?",
            ["Not planted yet", "Excellent yield", "Good yield", 
             "Average yield", "Poor yield"]
        )
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            save_feedback(predicted_crop, rating, usefulness, comments, actual_result)

def save_feedback(crop, rating, usefulness, comments, actual_result):
    """
    Save feedback to database.
    
    Args:
        crop: Predicted crop name
        rating: Star rating (1-5)
        usefulness: Usefulness category
        comments: User comments
        actual_result: Actual harvest result
    """
    try:
        conn = init_feedback_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback 
            (timestamp, predicted_crop, rating, usefulness, comments, actual_result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            crop,
            rating,
            usefulness,
            comments,
            actual_result
        ))
        
        conn.commit()
        conn.close()
        
        st.success("Thank you for your feedback!")
        
    except Exception as e:
        st.error(f"Could not save feedback: {str(e)}")

def get_feedback_stats():
    """
    Get feedback statistics.
    
    Returns:
        dict: Feedback summary
    """
    try:
        conn = init_feedback_db()
        cursor = conn.cursor()
        
        # Average rating
        cursor.execute('SELECT AVG(rating) FROM feedback')
        avg_rating = cursor.fetchone()[0]
        
        # Total feedback count
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total = cursor.fetchone()[0]
        
        # Most helpful count
        cursor.execute('''
            SELECT COUNT(*) FROM feedback 
            WHERE usefulness IN ('Very Helpful', 'Helpful')
        ''')
        helpful = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'avg_rating': round(avg_rating, 2) if avg_rating else 0,
            'total': total,
            'helpful_count': helpful,
            'helpful_percent': round((helpful / total * 100), 1) if total > 0 else 0
        }
        
    except Exception as e:
        return {'avg_rating': 0, 'total': 0, 'helpful_count': 0, 'helpful_percent': 0}

def view_all_feedback():
    """
    Display all feedback in a table.
    
    Returns:
        DataFrame: All feedback records
    """
    try:
        conn = init_feedback_db()
        
        query = '''
            SELECT timestamp, predicted_crop, rating, 
                   usefulness, comments, actual_result
            FROM feedback
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Could not load feedback: {str(e)}")
        return pd.DataFrame()

def display_feedback_summary():
    """Display feedback statistics in a nice format."""
    stats = get_feedback_stats()
    
    st.subheader("Feedback Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Rating", f"{stats['avg_rating']}/5")
    
    with col2:
        st.metric("Total Feedback", stats['total'])
    
    with col3:
        st.metric("Helpful %", f"{stats['helpful_percent']}%")
