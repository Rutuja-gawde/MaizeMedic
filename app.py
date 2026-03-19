import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from datetime import datetime

from styles import apply_custom_styles, display_header
from utils import validate_image, generate_report, update_history, verify_modules
from model_utils import load_maize_model, preprocess_image, predict_disease, class_names
from gradcam_utils import make_gradcam_heatmap
from chatbot import display_chat_ui

# ─── Disease Database ─────────────────────────────────────────────────────────
DISEASE_INFO = {
    "Blight": {
        "severity": "high", "severity_label": "HIGH SEVERITY", "icon": "🔴",
        "description": "Blight is caused by the fungus Exserohilum turcicum. It produces long, elliptical gray-green lesions on leaves. Can cause up to 50% yield loss if untreated.",
        "spread": "Airborne spores; spreads in humid, warm conditions (18–27°C).",
    },
    "Common_Rust": {
        "severity": "medium", "severity_label": "MEDIUM SEVERITY", "icon": "🟡",
        "description": "Caused by Puccinia sorghi. Small, oval, brick-red pustules appear on both leaf surfaces. Usually manageable but can reduce photosynthesis significantly.",
        "spread": "Wind-dispersed spores, thrives in cool, moist weather.",
    },
    "Gray_Leaf_Spot": {
        "severity": "high", "severity_label": "HIGH SEVERITY", "icon": "🔴",
        "description": "Caused by Cercospora zeae-maydis. Rectangular, gray-tan lesions restricted by leaf veins. One of the most yield-limiting diseases in maize.",
        "spread": "Residue-borne; favored by warm nights and high humidity.",
    },
    "Healthy": {
        "severity": "low", "severity_label": "NO DISEASE", "icon": "🟢",
        "description": "No disease detected. The leaf shows no visible signs of fungal, bacterial, or environmental stress. Continue standard agronomic practices.",
        "spread": "N/A — plant is healthy.",
    },
}

# ─── Results renderer (defined before page runs) ─────────────────────────────
def show_results(image, model):
    img_array = preprocess_image(image)

    with st.spinner("Analyzing leaf sample…"):
        predicted_class, confidence = predict_disease(model, img_array)
        heatmap = make_gradcam_heatmap(img_array, model, "top_conv")
        heatmap_resized  = cv2.resize(heatmap, (image.size[0], image.size[1]))
        heatmap_uint8    = np.uint8(255 * heatmap_resized)
        jet_heatmap      = plt.colormaps['jet'](heatmap_uint8)[:, :, :3]
        superimposed_img = np.clip(
            ((jet_heatmap * 0.4) + (np.array(image) / 255.0)) * 255, 0, 255
        ).astype("uint8")
        update_history(class_names[predicted_class], confidence)

        # ── Save scan context for chatbot ─────────────────────────────────────
        st.session_state.last_scan = {
            "disease":     class_names[predicted_class],
            "confidence":  round(float(confidence), 1),
            "severity":    DISEASE_INFO[class_names[predicted_class]]["severity"],
            "description": DISEASE_INFO[class_names[predicted_class]]["description"],
            "spread":      DISEASE_INFO[class_names[predicted_class]]["spread"],
            "time":        datetime.now().strftime("%H:%M"),
        }

    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

    disease      = class_names[predicted_class]
    disease_data = DISEASE_INFO[disease]
    conf_pct     = confidence
    conf_color   = "#00e5cc" if conf_pct >= 80 else "#ffc53d" if conf_pct >= 60 else "#ff6b6b"

    left_col, right_col = st.columns(2, gap="medium")

    with left_col:
        st.markdown("""
            <div class="panel"><div class="panel-header">
                <div class="panel-dot"></div>
                <span class="panel-title">Leaf Scan Input</span>
            </div></div>
        """, unsafe_allow_html=True)
        st.image(image, use_container_width=True)

        sev_cls   = f"severity-{disease_data['severity']}"
        sev_label = disease_data["severity_label"]
        sev_icon  = disease_data["icon"]

        st.markdown(f"""
            <div class="diagnosis-card">
                <div style="width:100%">
                    <div class="diag-top">
                        <div>
                            <div class="diagnosis-label">AI Diagnosis</div>
                            <div class="diagnosis-name">{disease.replace("_"," ")}</div>
                            <span class="severity-badge {sev_cls}">{sev_icon} {sev_label}</span>
                        </div>
                        <div class="conf-badge">
                            <div class="conf-value" style="color:{conf_color}">{conf_pct:.1f}%</div>
                            <div class="conf-label">Confidence</div>
                        </div>
                    </div>
                    <div class="conf-bar-track">
                        <div class="conf-bar-fill"
                             style="width:{conf_pct:.1f}%;background:{conf_color};
                                    box-shadow:0 0 10px {conf_color}66;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="disease-info">
                <div class="disease-info-title">🧬 About This Condition</div>
                <div>{disease_data["description"]}</div>
                <div style="margin-top:10px;font-size:.78rem;color:rgba(240,246,252,0.5);">
                    <span style="color:#ffc53d;font-family:'JetBrains Mono',monospace;
                                 font-size:.55rem;letter-spacing:1.5px;text-transform:uppercase;">
                        Spread pattern —
                    </span>
                    &nbsp;{disease_data["spread"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
            <div class="panel"><div class="panel-header">
                <div class="panel-dot"></div>
                <span class="panel-title">Grad-CAM Localization</span>
            </div></div>
        """, unsafe_allow_html=True)
        st.image(superimposed_img, use_container_width=True)
        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

        with st.expander("📋  TREATMENT PROTOCOL", expanded=True):
            if disease == "Healthy":
                st.markdown("""
                    <div style="background:rgba(0,229,204,0.07);border:1px solid rgba(0,229,204,0.22);
                                border-radius:10px;padding:16px 20px;font-family:'Outfit',sans-serif;
                                color:#a0f0e8;font-size:.88rem;line-height:1.6;">
                        ✅ &nbsp;<strong>No pathogens detected.</strong><br>
                        Crop is in optimal condition. Continue standard care — regular irrigation,
                        balanced fertilisation, and periodic scouting.
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="treatment-grid">
                        <div class="treatment-card urgent">
                            <strong>⚠ Immediate Action</strong>
                            Remove and dispose of all visibly infected leaves to limit spread.
                            Avoid overhead irrigation.
                        </div>
                        <div class="treatment-card preventative">
                            <strong>🧪 Chemical Control</strong>
                            Apply appropriate fungicide — consult your local agricultural
                            extension officer for dosage and timing.
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
        report_json = generate_report(image, predicted_class, confidence)
        st.download_button(
            label="⬇  DOWNLOAD REPORT",
            data=report_json,
            file_name=f"maizemedic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

        # ── Ask MaizeBot about this scan ──────────────────────────────────────
        st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
        if st.button("🤖  ASK MAIZEBOT ABOUT THIS SCAN", use_container_width=True, key="ask_bot_btn"):
            scan = st.session_state.get("last_scan", {})
            auto_q = f"My leaf scan just detected {scan.get('disease','').replace('_',' ')} with {scan.get('confidence',0)}% confidence. What should I do?"
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({
                "role": "user",
                "content": auto_q,
                "ts": datetime.now().strftime("%H:%M")
            })
            st.session_state.awaiting_reply = True


# ─── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MaizeMedic",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_styles()
verify_modules()
model = load_maize_model()
display_header()

st.markdown("""
    <style>
    section.main > div.block-container {
        max-width: 920px !important;
        margin: 0 auto !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
if "temp_image" not in st.session_state:
    st.session_state.temp_image = None
if "show_camera" not in st.session_state:
    st.session_state.show_camera = False

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📁   UPLOAD LEAF IMAGE",
    "📸   REAL-TIME SCAN",
    "💬   CONSULT AI",
])

# ── Tab 1: Upload ─────────────────────────────────────────────────────────────
with tab1:
    uploaded_file = st.file_uploader(
        "Drop your leaf image here — JPG, PNG, JPEG",
        type=["jpg", "png", "jpeg"],
        key="file_up"
    )
    upload_image = None
    if uploaded_file:
        upload_image = Image.open(uploaded_file).convert("RGB")
        st.session_state.temp_image = None   # clear camera image

    if upload_image is not None and validate_image(upload_image):
        show_results(upload_image, model)
    else:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🌽</div>
                <div class="empty-state-text">Upload a maize leaf image to begin analysis</div>
            </div>
        """, unsafe_allow_html=True)

# ── Tab 2: Camera ─────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.show_camera:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        if st.button("📸   INITIALIZE CAMERA", use_container_width=True):
            st.session_state.show_camera = True
            st.session_state.temp_image = None
            st.rerun()
    else:
        camera_image = st.camera_input("Scan", label_visibility="collapsed")
        if camera_image:
            st.session_state.temp_image = Image.open(camera_image).convert("RGB")
            st.session_state.show_camera = False
            st.rerun()
        if st.button("✕   STOP CAMERA", use_container_width=True):
            st.session_state.show_camera = False
            st.rerun()

    cam_image = st.session_state.temp_image
    if cam_image is not None and validate_image(cam_image):
        show_results(cam_image, model)
    elif not st.session_state.show_camera:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📷</div>
                <div class="empty-state-text">Initialize the camera to scan a maize leaf</div>
            </div>
        """, unsafe_allow_html=True)

# ── Tab 3: Chatbot — nothing else renders here ────────────────────────────────
with tab3:
    display_chat_ui()

# ─── Footer ───────────────────────────────────────────────────────────────────
scan_count = len(st.session_state.get("history", []))
st.markdown(f"""
    <div class="footer-bar">
        <span class="footer-item">Engine · EfficientNet-B0</span>
        <span class="footer-dot"></span>
        <span class="footer-item">Explainability · Grad-CAM</span>
        <span class="footer-dot"></span>
        <span class="footer-item">Session Scans · {scan_count:02d}</span>
        <span class="footer-dot"></span>
        <span class="footer-item">MaizeMedic · v2.0</span>
    </div>
""", unsafe_allow_html=True)