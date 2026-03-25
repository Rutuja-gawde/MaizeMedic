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

DISEASE_INFO = {
    "Blight":         {"severity":"high",   "label":"HIGH SEVERITY",  "icon":"🔴", "desc":"Caused by Exserohilum turcicum. Long, elliptical gray-green lesions. Up to 50% yield loss if untreated.", "spread":"Airborne spores; humid, warm conditions (18–27°C)."},
    "Common_Rust":    {"severity":"medium", "label":"MEDIUM SEVERITY", "icon":"🟡", "desc":"Caused by Puccinia sorghi. Brick-red pustules on both leaf surfaces. Reduces photosynthesis significantly.", "spread":"Wind-dispersed spores; cool, moist weather."},
    "Gray_Leaf_Spot": {"severity":"high",   "label":"HIGH SEVERITY",  "icon":"🔴", "desc":"Caused by Cercospora zeae-maydis. Rectangular tan-gray lesions between veins. Major yield-limiting disease.", "spread":"Residue-borne; warm nights and high humidity."},
    "Healthy":        {"severity":"low",    "label":"NO DISEASE",     "icon":"🟢", "desc":"No disease detected. No visible signs of fungal, bacterial, or environmental stress.", "spread":"N/A — plant is healthy."},
}

# ── Minimum confidence to trust a prediction as a maize leaf ──────────────────
CONFIDENCE_THRESHOLD = 50.0


def show_results(image, model, tab_key="upload"):
    """Run model and display results. tab_key must be unique per tab."""

    with st.spinner("Analyzing leaf sample…"):
        img_array = preprocess_image(image)
        predicted_class, confidence = predict_disease(model, img_array)
        heatmap   = make_gradcam_heatmap(img_array, model, "top_conv")
        heatmap_r = cv2.resize(heatmap, (image.size[0], image.size[1]))
        jet       = plt.colormaps['jet'](np.uint8(255 * heatmap_r))[:, :, :3]
        overlay   = np.clip(((jet * 0.4) + (np.array(image) / 255.0)) * 255, 0, 255).astype("uint8")

    # ── Reject low-confidence predictions (likely not a maize leaf) ───────────
    if confidence < CONFIDENCE_THRESHOLD:
        st.markdown(f"""
        <div style="background:rgba(255,107,107,0.10);border:1px solid rgba(255,107,107,0.35);
                    border-radius:14px;padding:2rem;text-align:center;margin-top:1rem;">
            <div style="font-size:2.5rem;margin-bottom:.6rem;">⚠️</div>
            <div style="font-family:'Outfit',sans-serif;font-size:1.1rem;font-weight:700;
                        color:#ff6b6b;margin-bottom:.5rem;">Not a Maize Leaf</div>
            <div style="font-family:'Outfit',sans-serif;font-size:.88rem;
                        color:rgba(240,246,252,0.65);line-height:1.6;">
                Confidence too low ({confidence:.1f}%) — this doesn't appear to be a maize leaf.<br>
                Please upload a clear, close-up photo of a <strong>maize leaf</strong>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Save scan for chatbot ─────────────────────────────────────────────────
    update_history(class_names[predicted_class], confidence)
    st.session_state.last_scan = {
        "disease":     class_names[predicted_class],
        "confidence":  round(float(confidence), 1),
        "severity":    DISEASE_INFO[class_names[predicted_class]]["severity"],
        "description": DISEASE_INFO[class_names[predicted_class]]["desc"],
        "spread":      DISEASE_INFO[class_names[predicted_class]]["spread"],
        "time":        datetime.now().strftime("%H:%M"),
    }

    disease = class_names[predicted_class]
    info    = DISEASE_INFO[disease]
    color   = "#00e5cc" if confidence >= 80 else "#ffc53d" if confidence >= 60 else "#ff6b6b"

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    left, right = st.columns(2, gap="medium")

    # ── Left column ───────────────────────────────────────────────────────────
    with left:
        st.markdown('<div class="panel"><div class="panel-header"><div class="panel-dot"></div><span class="panel-title">Leaf Scan Input</span></div></div>', unsafe_allow_html=True)
        st.image(image, use_container_width=True)

        st.markdown(f"""
        <div class="diagnosis-card">
          <div style="width:100%">
            <div class="diag-top">
              <div>
                <div class="diagnosis-label">AI Diagnosis</div>
                <div class="diagnosis-name">{disease.replace("_"," ")}</div>
                <span class="severity-badge severity-{info['severity']}">{info['icon']} {info['label']}</span>
              </div>
              <div class="conf-badge">
                <div class="conf-value" style="color:{color}">{confidence:.1f}%</div>
                <div class="conf-label">Confidence</div>
              </div>
            </div>
            <div class="conf-bar-track">
              <div class="conf-bar-fill" style="width:{confidence:.1f}%;background:{color};box-shadow:0 0 10px {color}66;"></div>
            </div>
          </div>
        </div>
        <div class="disease-info">
          <div class="disease-info-title">🧬 About This Condition</div>
          <div>{info['desc']}</div>
          <div style="margin-top:8px;font-size:.78rem;color:rgba(240,246,252,0.5);">
            <span style="color:#ffc53d;font-family:'JetBrains Mono',monospace;font-size:.55rem;
                         letter-spacing:1.5px;text-transform:uppercase;">Spread — </span>
            {info['spread']}
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Right column ──────────────────────────────────────────────────────────
    with right:
        st.markdown('<div class="panel"><div class="panel-header"><div class="panel-dot"></div><span class="panel-title">Grad-CAM Localization</span></div></div>', unsafe_allow_html=True)
        st.image(overlay, use_container_width=True)
        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

        # Treatment Protocol — st.html() prevents Streamlit injecting a white wrapper
        if disease == "Healthy":
            treatment_inner = """
            <div style="background:rgba(0,229,204,0.07);border:1px solid rgba(0,229,204,0.22);
                        border-radius:10px;padding:16px 20px;color:#a0f0e8;
                        font-family:'Outfit',sans-serif;font-size:.88rem;line-height:1.6;">
                ✅ &nbsp;<strong style="color:#a0f0e8;">No pathogens detected.</strong><br>
                Crop is in optimal condition. Continue standard care — regular irrigation,
                balanced fertilisation, and periodic scouting.
            </div>"""
        else:
            treatment_inner = """
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="padding:16px 18px;border-radius:12px;font-size:0.83rem;line-height:1.58;
                            background:rgba(255,107,107,0.12);border:1px solid rgba(255,107,107,0.30);
                            color:#ffc0c0;">
                    <strong style="display:block;font-family:'JetBrains Mono',monospace;font-size:0.56rem;
                                   letter-spacing:2px;text-transform:uppercase;margin-bottom:7px;
                                   color:#ff6b6b;">⚠ Immediate Action</strong>
                    Remove and dispose of all infected leaves. Avoid overhead irrigation.
                </div>
                <div style="padding:16px 18px;border-radius:12px;font-size:0.83rem;line-height:1.58;
                            background:rgba(121,192,255,0.10);border:1px solid rgba(121,192,255,0.25);
                            color:#b0d0ff;">
                    <strong style="display:block;font-family:'JetBrains Mono',monospace;font-size:0.56rem;
                                   letter-spacing:2px;text-transform:uppercase;margin-bottom:7px;
                                   color:#79c0ff;">🧪 Chemical Control</strong>
                    Apply appropriate fungicide — consult your local extension officer for dosage and timing.
                </div>
            </div>"""

        st.html(f"""
        <div style="background:#161b22;border:1px solid rgba(0,229,204,0.22);border-radius:12px;overflow:hidden;">
          <div style="background:#1c2128;padding:11px 16px;border-bottom:1px solid rgba(0,229,204,0.15);
                      font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:2px;
                      text-transform:uppercase;color:#f0f6fc;">
            📋 &nbsp;Treatment Protocol
          </div>
          <div style="padding:14px 16px;background:#161b22;">
            {treatment_inner}
          </div>
        </div>
        """)

        st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)

        # Download report — unique key per tab
        report_json = generate_report(image, predicted_class, confidence)
        st.download_button(
            "⬇  DOWNLOAD REPORT",
            data=report_json,
            file_name=f"maizemedic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            key=f"dl_{tab_key}"
        )

        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

        # Ask MaizeBot — unique key per tab
        if st.button("🤖  ASK MAIZEBOT ABOUT THIS SCAN", use_container_width=True, key=f"ask_{tab_key}"):
            scan = st.session_state.get("last_scan", {})
            if "messages" not in st.session_state:
                st.session_state.messages = []
            st.session_state.messages.append({
                "role": "user",
                "content": f"My scan detected {scan.get('disease','').replace('_',' ')} with {scan.get('confidence',0)}% confidence. What should I do?",
                "ts": datetime.now().strftime("%H:%M")
            })
            st.session_state.awaiting_reply    = True
            st.session_state.switch_to_chatbot = True
            st.rerun()


# ─── Page setup ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="MaizeMedic", page_icon="🌽",
                   layout="wide", initial_sidebar_state="collapsed")

apply_custom_styles()
verify_modules()
model = load_maize_model()
display_header()

st.markdown('<style>section.main>div.block-container{max-width:920px!important;margin:0 auto!important;padding:0 2rem!important;}</style>', unsafe_allow_html=True)

for key, val in [("show_camera", False), ("switch_to_chatbot", False)]:
    if key not in st.session_state:
        st.session_state[key] = val

# Auto-switch to chatbot tab via JS when "Ask MaizeBot" is clicked
if st.session_state.switch_to_chatbot:
    st.session_state.switch_to_chatbot = False
    st.components.v1.html(
        '<script>window.parent.setTimeout(()=>{'
        'var t=window.parent.document.querySelectorAll(\'[data-baseweb="tab"]\');'
        'if(t.length>=3)t[2].click();},150);</script>',
        height=0
    )

tab1, tab2, tab3 = st.tabs(["📁   UPLOAD LEAF IMAGE", "📸   REAL-TIME SCAN", "💬   CONSULT AI"])

# ── Tab 1: Upload ──────────────────────────────────────────────────────────────
with tab1:
    uploaded_file = st.file_uploader(
        "Drop your leaf image here — JPG, PNG, JPEG",
        type=["jpg", "png", "jpeg"], key="file_up"
    )
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        if validate_image(image):
            show_results(image, model, tab_key="upload")
    else:
        st.markdown('<div class="empty-state"><div class="empty-state-icon">🌽</div><div class="empty-state-text">Upload a maize leaf image to begin analysis</div></div>', unsafe_allow_html=True)

# ── Tab 2: Camera ──────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.show_camera:
        # Placeholder until user activates camera
        st.markdown("""
        <div style="text-align:center;padding:2.5rem 1rem 2rem;
                    border:2px dashed rgba(0,229,204,0.22);border-radius:14px;
                    background:rgba(0,229,204,0.03);margin-bottom:1rem;">
            <div style="font-size:2.8rem;margin-bottom:.6rem;">📷</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:.62rem;
                        letter-spacing:2px;text-transform:uppercase;color:#8b949e;
                        margin-bottom:1.4rem;">Click below to activate camera</div>
        </div>""", unsafe_allow_html=True)

        if st.button("📸   INITIALIZE CAMERA", use_container_width=True, key="cam_start"):
            st.session_state.show_camera = True
            st.rerun()
    else:
        if st.button("✕   STOP CAMERA", use_container_width=True, key="cam_stop"):
            st.session_state.show_camera = False
            st.rerun()

        st.markdown("""
        <div style="padding:8px 12px;background:rgba(0,229,204,0.06);
                    border:1px solid rgba(0,229,204,0.20);border-radius:8px;margin-bottom:.8rem;
                    font-family:'JetBrains Mono',monospace;font-size:.60rem;
                    letter-spacing:1px;color:rgba(0,229,204,0.80);">
            📱 Allow camera access when prompted — capture a clear, close-up maize leaf photo
        </div>""", unsafe_allow_html=True)

        # Camera input — no rerun trick, processes directly
        camera_photo = st.camera_input("", label_visibility="collapsed", key="cam_input")

        if camera_photo:
            cam_image = Image.open(camera_photo).convert("RGB")
            if validate_image(cam_image):
                show_results(cam_image, model, tab_key="camera")

# ── Tab 3: Chatbot ─────────────────────────────────────────────────────────────
with tab3:
    display_chat_ui()

# ─── Footer ───────────────────────────────────────────────────────────────────
scan_count = len(st.session_state.get("history", []))
st.markdown(f"""
    <div class="footer-bar">
        <span class="footer-item">Engine · EfficientNet-B0</span><span class="footer-dot"></span>
        <span class="footer-item">Explainability · Grad-CAM</span><span class="footer-dot"></span>
        <span class="footer-item">Session Scans · {scan_count:02d}</span><span class="footer-dot"></span>
        <span class="footer-item">MaizeMedic · v2.0</span>
    </div>
""", unsafe_allow_html=True)