import numpy as np
import os

# ── Set thread config via env vars BEFORE importing TensorFlow ────────────────
# This avoids the "cannot be modified after initialization" error.
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"

import tensorflow as tf
import streamlit as st

# ─── Constants ────
IMG_SIZE    = 224
class_names = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']
MODEL_PATH  = "plant_disease_model.keras"

# ─── Google Drive file ID ────
GDRIVE_FILE_ID = "1E-PFCu-c7pcweJbbSJF2DVbXa3XRnd1s"

# ─── Download model from Google Drive if not present ─────────────────────────
def _download_model():
    if os.path.exists(MODEL_PATH):
        return  # already on disk — skip download

    try:
        import gdown
    except ImportError:
        st.error("❌ `gdown` not installed. Add `gdown>=5.1.0` to requirements.txt.")
        st.stop()

    with st.spinner("⬇️ Downloading model (first run only, ~30MB)…"):
        try:
            url = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
            gdown.download(url, MODEL_PATH, quiet=False)
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError("File not found after download.")
        except Exception as e:
            st.error(
                f"❌ Model download failed: {e}\n\n"
                "Make sure the Google Drive file is shared as **'Anyone with the link'**."
            )
            st.stop()

# ─── Load model (cached — only runs once per app session) ─────────────────────
@st.cache_resource
def load_maize_model():
    _download_model()
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"❌ Could not load model: {e}")
        st.info("Ensure `plant_disease_model.keras` is valid and not corrupted.")
        st.stop()

# ─── Preprocessing ────────────────────────────────────────────────────────────
def preprocess_image(image):
    image     = image.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(image)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    return img_array

# ─── Prediction ───────────────────────────────────────────────────────────────
def predict_disease(model, img_array):
    prediction      = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    confidence      = np.max(prediction) * 100
    return predicted_class, confidence