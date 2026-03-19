import streamlit as st
import base64
import os

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def apply_custom_styles():
    img_path = 'image.png'
    if os.path.exists(img_path):
        bin_str = get_base64_of_bin_file(img_path)
        bg_img_css = f"url('data:image/png;base64,{bin_str}')"
    else:
        bg_img_css = "linear-gradient(160deg, #0d1a0e 0%, #1a3a1c 100%)"

    st.html(f"""
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
        <style>

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TOKENS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        :root {{
            --bg-base:   #0d1117;
            --bg-1:      #161b22;
            --bg-2:      #1c2128;
            --bg-3:      #252c36;
            --teal:      #00e5cc;
            --teal-dim:  rgba(0,229,204,0.12);
            --teal-glow: rgba(0,229,204,0.25);
            --amber:     #ffc53d;
            --amber-dim: rgba(255,197,61,0.12);
            --red:       #ff6b6b;
            --red-dim:   rgba(255,107,107,0.12);
            --blue:      #79c0ff;
            --blue-dim:  rgba(121,192,255,0.10);
            --white:     #f0f6fc;
            --muted:     #8b949e;
            --border:    rgba(255,255,255,0.08);
            --border-hi: rgba(0,229,204,0.28);
            --radius:    12px;
            --radius-lg: 18px;
        }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           BASE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        html, body,
        [data-testid="stAppViewContainer"], .main {{
            background-color: var(--bg-base) !important;
            color: var(--white) !important;
            font-family: 'Outfit', sans-serif !important;
        }}

        [data-testid="stAppViewContainer"] {{
            background:
                radial-gradient(ellipse 80% 40% at 10% 0%,  rgba(0,229,204,0.06) 0%, transparent 60%),
                radial-gradient(ellipse 60% 40% at 90% 100%,rgba(255,197,61,0.04) 0%, transparent 60%),
                var(--bg-base) !important;
        }}

        .main .block-container {{
            padding-top: 0 !important;
            padding-bottom: 3rem !important;
            max-width: 100% !important;
        }}

        [data-testid="stVerticalBlock"] > div {{
            gap: 0 !important;
            padding-top: 0 !important;
        }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           HERO  — light overlay so image shows
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .hero-section {{
            position: relative;
            overflow: hidden;
            padding: 5.5rem 2rem 4.5rem;
            margin-top: -95px !important;
            margin-bottom: 2.8rem !important;
            text-align: center;
            background:
                linear-gradient(180deg,
                    rgba(0,0,0,0.08) 0%,
                    rgba(0,0,0,0.22) 40%,
                    rgba(10,20,12,0.82) 80%,
                    rgba(13,17,23,1.00) 100%),
                {bg_img_css};
            background-size: cover;
            background-position: center 38%;
            border-bottom: 1px solid rgba(0,229,204,0.18);
        }}

        /* Side vignette */
        .hero-section::before {{
            content: '';
            position: absolute; inset: 0;
            background: linear-gradient(90deg,
                rgba(0,0,0,0.28) 0%, transparent 25%,
                transparent 75%, rgba(0,0,0,0.28) 100%);
            pointer-events: none; z-index: 0;
        }}

        /* Bottom teal bleed */
        .hero-section::after {{
            content: '';
            position: absolute;
            bottom: -20px; left: 50%;
            transform: translateX(-50%);
            width: 600px; height: 80px;
            background: radial-gradient(ellipse, rgba(0,229,204,0.13) 0%, transparent 70%);
            pointer-events: none; z-index: 0;
        }}

        .hero-section > * {{ position: relative; z-index: 1; }}

        .hero-eyebrow {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.60rem;
            letter-spacing: 4px;
            text-transform: uppercase;
            color: #fff8e0;
            background: rgba(0,0,0,0.38);
            border: 1px solid rgba(255,197,61,0.40);
            border-radius: 50px;
            padding: 6px 18px;
            margin-bottom: 1.4rem;
            backdrop-filter: blur(6px);
        }}

        /* ── TITLE: white "Maize" + vivid lime "Medic" ── */
        .main-title {{
            font-family: 'Outfit', sans-serif !important;
            font-size: clamp(2.2rem, 8vw, 7.2rem) !important;
            font-weight: 900 !important;
            margin: 0 !important;
            letter-spacing: clamp(-1px, -0.3vw, -3px);
            line-height: 1.0;
            white-space: nowrap;
            color: #ffffff !important;
            text-shadow:
                0 2px 12px rgba(0,0,0,0.75),
                0 4px 32px rgba(0,0,0,0.55);
        }}

        .main-title span {{
            color: #4cde6e !important;
            -webkit-text-fill-color: #4cde6e !important;
            background: none !important;
            background-clip: unset !important;
            text-shadow:
                0 2px 12px rgba(0,0,0,0.75),
                0 0  40px rgba(76,222,110,0.55),
                0 0  80px rgba(76,222,110,0.25);
        }}

        @media (max-width: 480px) {{
            .main-title {{
                font-size: clamp(2rem, 11vw, 3.2rem) !important;
                letter-spacing: -1px;
                white-space: nowrap;
            }}
            .hero-eyebrow {{
                font-size: .50rem;
                letter-spacing: 2px;
                padding: 5px 12px;
            }}
            .sub-title {{
                font-size: .52rem !important;
                letter-spacing: 2px !important;
                padding: 4px 12px !important;
            }}
            .hero-badges {{
                gap: 5px;
            }}
            .hero-badge {{
                font-size: .50rem;
                padding: 4px 10px;
            }}
        }}

        .sub-title {{
            font-family: 'JetBrains Mono', monospace !important;
            color: rgba(240,246,252,0.82) !important;
            background: rgba(0,0,0,0.32) !important;
            backdrop-filter: blur(4px) !important;
            display: inline-block !important;
            padding: 5px 18px !important;
            border-radius: 50px !important;
            margin-top: 1.3rem !important;
            font-size: 0.66rem !important;
            letter-spacing: 4px;
            text-transform: uppercase;
        }}

        .hero-badges {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 1.6rem;
            flex-wrap: wrap;
        }}

        .hero-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            padding: 6px 14px;
            border-radius: 50px;
            border: 1px solid rgba(255,255,255,0.20);
            color: rgba(255,255,255,0.88);
            background: rgba(0,0,0,0.35);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            backdrop-filter: blur(6px);
        }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TABS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--bg-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            padding: 4px !important;
            gap: 3px !important;
        }}

        .stTabs [data-baseweb="tab"] {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.65rem !important;
            letter-spacing: 1.5px !important;
            color: var(--muted) !important;
            border-radius: 7px !important;
            padding: 11px 24px !important;
            border: none !important;
            background: transparent !important;
            transition: all 0.2s !important;
            text-transform: uppercase !important;
        }}

        .stTabs [aria-selected="true"] {{
            background: var(--teal-dim) !important;
            color: var(--teal) !important;
            border: 1px solid var(--border-hi) !important;
        }}

        .stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           FILE UPLOADER — fully dark
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        [data-testid="stFileUploader"] {{
            background: transparent !important;
        }}

        /* The actual drop zone white box */
        [data-testid="stFileUploaderDropzone"] {{
            background: var(--bg-2) !important;
            border: 2px dashed rgba(0,229,204,0.32) !important;
            border-radius: var(--radius) !important;
            padding: 1.8rem 1.5rem !important;
            transition: all 0.3s ease !important;
        }}

        [data-testid="stFileUploaderDropzone"]:hover {{
            border-color: var(--teal) !important;
            background: rgba(0,229,204,0.05) !important;
            box-shadow: 0 0 28px rgba(0,229,204,0.10) !important;
        }}

        /* All text inside uploader */
        [data-testid="stFileUploader"] *,
        [data-testid="stFileUploaderDropzoneInstructions"] * {{
            color: rgba(240,246,252,0.70) !important;
            font-family: 'Outfit', sans-serif !important;
        }}

        /* Browse files button */
        [data-testid="stFileUploader"] button {{
            background: var(--teal-dim) !important;
            border: 1px solid var(--border-hi) !important;
            color: var(--teal) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.68rem !important;
            letter-spacing: 1px !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            transition: all 0.2s !important;
        }}

        [data-testid="stFileUploader"] button:hover {{
            background: rgba(0,229,204,0.22) !important;
            border-color: var(--teal) !important;
            color: #fff !important;
            box-shadow: 0 0 16px rgba(0,229,204,0.25) !important;
        }}

        /* Uploaded file name pill */
        [data-testid="stFileUploaderFile"] {{
            background: var(--bg-3) !important;
            border-radius: 8px !important;
            border: 1px solid var(--border) !important;
        }}

        /* Upload cloud icon */
        [data-testid="stFileUploaderDropzoneInstructions"] svg {{
            fill: var(--teal) !important;
            opacity: 0.65;
        }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           BUTTONS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .stButton > button {{
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.88rem !important;
            font-weight: 600 !important;
            background: linear-gradient(135deg, rgba(0,229,204,0.16) 0%, rgba(0,180,216,0.10) 100%) !important;
            border: 1px solid var(--border-hi) !important;
            color: var(--teal) !important;
            border-radius: 10px !important;
            padding: 14px 28px !important;
            transition: all 0.25s ease !important;
        }}

        .stButton > button:hover {{
            background: linear-gradient(135deg, rgba(0,229,204,0.28) 0%, rgba(0,180,216,0.20) 100%) !important;
            border-color: var(--teal) !important;
            color: #fff !important;
            box-shadow: 0 0 28px rgba(0,229,204,0.28), 0 4px 16px rgba(0,0,0,0.4) !important;
            transform: translateY(-1px) !important;
        }}

        .stButton > button:active {{ transform: translateY(0) !important; }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           RESULT PANELS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .panel {{
            background: var(--bg-1);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0,0,0,0.40);
        }}

        .panel-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 18px;
            background: var(--bg-2);
            border-bottom: 1px solid var(--border);
        }}

        .panel-dot {{
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--teal);
            box-shadow: 0 0 8px var(--teal);
            animation: blink 2.4s ease-in-out infinite;
            flex-shrink: 0;
        }}

        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50%        {{ opacity: 0.2; }}
        }}

        .panel-title {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: var(--teal);
        }}

        .img-container {{
            background: var(--bg-2);
            border-radius: var(--radius);
            overflow: hidden;
            border: 1px solid var(--border-hi);
        }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           DIAGNOSIS CARD
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .diagnosis-card {{
            background: var(--bg-1);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 22px 26px;
            margin-top: 14px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0,0,0,0.40);
        }}

        .diagnosis-card::before {{
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, var(--teal), rgba(0,180,216,0.4), transparent 70%);
        }}

        .diag-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }}

        .diagnosis-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.52rem;
            letter-spacing: 3px;
            color: var(--teal);
            text-transform: uppercase;
            margin-bottom: 8px;
        }}

        .diagnosis-name {{
            font-family: 'Outfit', sans-serif;
            font-size: 1.9rem;
            font-weight: 800;
            color: var(--white);
            line-height: 1;
        }}

        .conf-badge {{ display: flex; flex-direction: column; align-items: flex-end; }}

        .conf-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1;
        }}

        .conf-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.50rem;
            letter-spacing: 2px;
            color: var(--muted);
            text-transform: uppercase;
            margin-top: 4px;
        }}

        .conf-bar-track {{
            width: 100%; height: 6px;
            background: var(--bg-3);
            border-radius: 99px; overflow: hidden;
        }}

        .conf-bar-fill {{
            height: 100%; border-radius: 99px;
            transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
        }}

        .disease-info {{
            margin-top: 14px; padding: 14px 18px;
            background: var(--bg-2); border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: 0.85rem; color: rgba(240,246,252,0.80); line-height: 1.6;
        }}

        .disease-info-title {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem; letter-spacing: 2px;
            color: var(--amber); text-transform: uppercase; margin-bottom: 8px;
        }}

        .severity-badge {{
            display: inline-flex; align-items: center; gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem; letter-spacing: 1.5px; text-transform: uppercase;
            padding: 4px 12px; border-radius: 50px; margin-top: 10px;
        }}

        .severity-high   {{ background:var(--red-dim);   border:1px solid rgba(255,107,107,0.35); color:var(--red);   }}
        .severity-medium {{ background:var(--amber-dim); border:1px solid rgba(255,197,61,0.35);  color:var(--amber); }}
        .severity-low    {{ background:var(--teal-dim);  border:1px solid var(--border-hi);       color:var(--teal);  }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TREATMENT CARDS
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .treatment-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:14px; }}

        .treatment-card {{ padding:16px 18px; border-radius:var(--radius); font-size:0.83rem; line-height:1.58; }}

        .treatment-card.urgent       {{ background:var(--red-dim);  border:1px solid rgba(255,107,107,0.30); color:#ffc0c0; }}
        .treatment-card.preventative {{ background:var(--blue-dim); border:1px solid rgba(121,192,255,0.25); color:#b0d0ff; }}

        .treatment-card strong {{ display:block; font-family:'JetBrains Mono',monospace; font-size:0.56rem; letter-spacing:2px; text-transform:uppercase; margin-bottom:7px; }}
        .treatment-card.urgent strong       {{ color:var(--red);  }}
        .treatment-card.preventative strong {{ color:var(--blue); }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           EXPANDER / ALERTS / EMPTY STATE
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        [data-testid="stExpander"] {{
            background: var(--bg-1) !important; border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important; margin-top: 14px !important;
        }}

        [data-testid="stExpander"] summary {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.65rem !important; letter-spacing: 2px !important;
            text-transform: uppercase !important; color: var(--white) !important;
        }}

        [data-testid="stExpander"] summary:hover {{ color: var(--teal) !important; }}

        [data-testid="stAlert"] {{
            background: var(--amber-dim) !important;
            border: 1px solid rgba(255,197,61,0.30) !important;
            border-radius: 8px !important; color: #ffe0a0 !important;
        }}

        .empty-state {{
            text-align:center; padding:4rem 2rem;
            border:2px dashed rgba(255,255,255,0.08); border-radius:var(--radius-lg);
            margin:1.5rem 0; background:rgba(255,255,255,0.02);
        }}

        .empty-state-icon  {{ font-size:3.5rem; margin-bottom:1.2rem; opacity:0.5; }}
        .empty-state-text  {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--muted); }}

        /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           FOOTER / DOWNLOAD / MISC
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
        .footer-bar {{ display:flex; justify-content:center; align-items:center; gap:16px; padding:16px 0; border-top:1px solid var(--border); margin-top:2rem; }}
        .footer-item {{ font-family:'JetBrains Mono',monospace; font-size:0.58rem; letter-spacing:1.5px; text-transform:uppercase; color:rgba(139,148,158,0.45); }}
        .footer-dot  {{ width:3px; height:3px; border-radius:50%; background:var(--amber); opacity:0.5; }}

        [data-testid="stSpinner"] {{ color: var(--teal) !important; }}

        .stDownloadButton > button {{
            font-family:'JetBrains Mono',monospace !important; font-size:0.65rem !important;
            letter-spacing:1.5px !important; text-transform:uppercase !important;
            background:var(--amber-dim) !important; border:1px solid rgba(255,197,61,0.35) !important;
            color:var(--amber) !important; border-radius:8px !important; padding:10px 20px !important; width:100% !important;
        }}

        .stDownloadButton > button:hover {{
            background:rgba(255,197,61,0.22) !important; border-color:var(--amber) !important;
            color:#fff !important; box-shadow:0 0 20px rgba(255,197,61,0.22) !important;
        }}

        header,[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer {{ visibility:hidden !important; }}

        ::-webkit-scrollbar {{ width:4px; }}
        ::-webkit-scrollbar-track {{ background:var(--bg-base); }}
        ::-webkit-scrollbar-thumb {{ background:rgba(0,229,204,0.22); border-radius:2px; }}

        .stMarkdown p,[data-testid="stMarkdownContainer"] p {{ color:rgba(240,246,252,0.85) !important; font-family:'Outfit',sans-serif !important; }}
        .stCaption,[data-testid="stCaptionContainer"] {{ font-family:'JetBrains Mono',monospace !important; color:var(--muted) !important; font-size:0.6rem !important; }}

        </style>
    """)


def display_header():
    st.markdown("""
        <div class="hero-section">
            <div class="hero-eyebrow">⚡ Plant Pathology Intelligence · v2.0</div>
            <h1 class="main-title">Maize<span>Medic</span></h1>
            <p class="sub-title">EfficientNet-B0 &nbsp;·&nbsp; Grad-CAM &nbsp;·&nbsp; 4 Disease Classes</p>
            <div class="hero-badges">
                <span class="hero-badge">🌽 Blight</span>
                <span class="hero-badge">🦠 Common Rust</span>
                <span class="hero-badge">🍂 Gray Leaf Spot</span>
                <span class="hero-badge">✅ Healthy</span>
            </div>
        </div>
    """, unsafe_allow_html=True)