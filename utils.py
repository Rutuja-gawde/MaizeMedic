import streamlit as st
import os
import sys
import json
from datetime import datetime

def verify_modules():
    """Ensures all necessary backend files are present before starting."""
    required = ['model_utils', 'gradcam_utils', 'styles']
    missing = [m for m in required if not os.path.exists(f"{m}.py")]
    if missing:
        st.error(f"❌ Critical Error: Missing files: {', '.join(missing)}")
        st.stop()

def validate_image(image):
    """Checks image resolution."""
    if image.size[0] < 224 or image.size[1] < 224:
        st.warning("⚠️ Low resolution detected. Results may be less accurate.")
        return True # Still allow it, but warn
    return True

def generate_report(image, prediction_index, confidence):
    """Creates a downloadable JSON summary."""
    from model_utils import class_names
    report = {
        "timestamp": datetime.now().isoformat(),
        "diagnosis": class_names[prediction_index],
        "confidence": f"{confidence:.2f}%",
        "dimensions": f"{image.size[0]}x{image.size[1]}"
    }
    return json.dumps(report, indent=4)

def update_history(prediction_text, confidence):
    """Manages the session state history (limit to last 5)."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    new_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'prediction': prediction_text,
        'confidence': confidence
    }
    st.session_state.history.append(new_entry)
    if len(st.session_state.history) > 5:
        st.session_state.history.pop(0)