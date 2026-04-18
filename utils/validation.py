# utils/validation.py
# Simple input validation based on dataset ranges

import streamlit as st

# Define valid ranges based on dataset statistics
RANGES = {
    'N': (0, 140),
    'P': (5, 145),
    'K': (5, 205),
    'temperature': (8.83, 43.68),
    'humidity': (14.26, 99.98),
    'ph': (3.50, 9.94),
    'rainfall': (6.11, 298.56)
}

def validate_input(name, value):
    """
    Validate if input value is within acceptable range.
    
    Args:
        name: Parameter name (e.g., 'N', 'temperature')
        value: User input value
    
    Returns:
        bool: True if valid, False otherwise
    """
    if name not in RANGES:
        return True
    
    min_val, max_val = RANGES[name]
    
    if value < min_val or value > max_val:
        st.error(f"❌ {name} must be between {min_val} and {max_val}")
        return False
    
    return True

def validate_all_inputs(inputs_dict):
    """
    Validate all inputs at once.
    
    Args:
        inputs_dict: Dictionary of parameter names to values
    
    Returns:
        bool: True if all valid, False otherwise
    """
    all_valid = True
    
    for name, value in inputs_dict.items():
        if not validate_input(name, value):
            all_valid = False
    
    return all_valid

def get_input_info(name):
    """
    Get min/max range info for display.
    
    Args:
        name: Parameter name
    
    Returns:
        tuple: (min_value, max_value)
    """
    return RANGES.get(name, (None, None))
