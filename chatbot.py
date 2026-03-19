import streamlit as st
import requests
import re
from datetime import datetime

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
GROQ_MODEL   = "llama-3.3-70b-versatile"

QUICK_PROMPTS = [
    ("🔬", "Early signs of Blight?"),
    ("🦠", "Common Rust spread?"),
    ("🍂", "Gray Leaf Spot?"),
    ("💊", "Best fungicide?"),
    ("🌱", "Keep crop healthy?"),
    ("📸", "Orange-red spots?"),
]

_PREFIX_RE = re.compile(r"^\s*(MaizeBot|Maize\s*Bot|AI|Assistant|Bot)\s*:\s*", re.IGNORECASE)

def _clean(t): return _PREFIX_RE.sub("", t).strip()
def _esc(t):   return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")

def _system_prompt():
    base = """You are MaizeBot — a friendly maize crop health advisor.
- Greet warmly if farmer greets. Ask what crop issue to help with.
- For disease questions: name disease, one-line symptom, best action.
- Max 3 sentences. Never start with your name or a label.
- Only answer maize/corn health topics. Politely decline everything else."""

    scan = st.session_state.get("last_scan")
    if scan:
        base += f"\n\nRECENT SCAN: {scan['disease'].replace('_',' ')} | {scan['confidence']}% | {scan['severity'].upper()}\n{scan['description']}\nSpread: {scan['spread']}\nGive specific advice for this diagnosis."
    return base

def _backend():
    try:
        k = st.secrets.get("GROQ_API_KEY","")
        if k and len(k) > 20: return "groq"
    except: pass
    try:
        if requests.get("http://localhost:11434/", timeout=2).status_code == 200: return "ollama"
    except: pass
    return "none"

def _groq(prompt, history):
    try:
        import groq as g
        client = g.Groq(api_key=st.secrets["GROQ_API_KEY"])
        msgs = [{"role":"system","content":_system_prompt()}]
        for m in history[-8:]:
            msgs.append({"role":"user" if m["role"]=="user" else "assistant","content":m["content"]})
        msgs.append({"role":"user","content":prompt})
        r = client.chat.completions.create(model=GROQ_MODEL, messages=msgs, max_tokens=150, temperature=0.5)
        return _clean(r.choices[0].message.content.strip())
    except Exception as e:
        return f"⚠️ Groq error: {str(e)[:100]}"

def _ollama(prompt, history):
    convo = "".join(f"{'Farmer' if m['role']=='user' else 'MaizeBot'}: {m['content']}\n" for m in history[-8:])
    convo += f"Farmer: {prompt}\nMaizeBot:"
    try:
        r = requests.post(OLLAMA_URL, json={"model":OLLAMA_MODEL,"prompt":f"{_system_prompt()}\n\n{convo}","stream":False,"options":{"temperature":0.5,"num_predict":150,"stop":["Farmer:","\nFarmer:"]}}, timeout=180)
        return _clean(r.json().get("response","").strip()) or "Try again."
    except requests.exceptions.Timeout:
        return "⏱️ Took too long. Try `ollama pull phi3` for a faster model."
    except Exception as e:
        return f"⚠️ {str(e)[:80]}"

def _respond(prompt, history):
    b = _backend()
    if b == "groq":   return _groq(prompt, history)
    if b == "ollama": return _ollama(prompt, history)
    return "⚠️ No AI backend. Add GROQ_API_KEY in Streamlit Secrets, or run `ollama serve` locally."

# ─── Bubble HTML ──────────────────────────────────────────────────────────────
AV = "width:36px;height:36px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:1.1rem;"

def _bot(content, ts="", cursor=False):
    cur = '<span style="display:inline-block;width:2px;height:.85em;background:#00e5cc;margin-left:2px;vertical-align:middle;animation:cur .65s steps(1) infinite;"></span>' if cursor else ""
    return f"""
<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:16px;">
  <div style="{AV}background:rgba(0,229,204,0.10);border:1.5px solid rgba(0,229,204,0.28);margin-top:20px;">🤖</div>
  <div style="flex:1;min-width:0;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:.45rem;letter-spacing:2px;text-transform:uppercase;color:#00e5cc;margin-bottom:5px;">AI Pathologist</div>
    <div style="background:#1c2128;border:1px solid rgba(0,229,204,0.15);border-radius:3px 14px 14px 14px;padding:12px 16px;display:inline-block;max-width:84%;font-family:'Outfit',sans-serif;font-size:.88rem;line-height:1.72;color:rgba(240,246,252,0.92);word-break:break-word;">{_esc(content)}{cur}</div>
    {'<div style="font-family:monospace;font-size:.44rem;color:#8b949e;margin-top:4px;padding-left:46px;">'+ts+'</div>' if ts else ""}
  </div>
</div>"""

def _user(content, ts=""):
    return f"""
<div style="display:flex;align-items:flex-start;flex-direction:row-reverse;gap:10px;margin-bottom:16px;">
  <div style="{AV}background:rgba(76,222,110,0.10);border:1.5px solid rgba(76,222,110,0.26);margin-top:20px;">👨‍🌾</div>
  <div style="flex:1;display:flex;flex-direction:column;align-items:flex-end;min-width:0;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:.45rem;letter-spacing:2px;text-transform:uppercase;color:#4cde6e;margin-bottom:5px;">Farmer</div>
    <div style="background:linear-gradient(135deg,rgba(0,229,204,0.14),rgba(0,180,216,0.08));border:1px solid rgba(0,229,204,0.22);border-radius:14px 3px 14px 14px;padding:12px 16px;max-width:84%;font-family:'Outfit',sans-serif;font-size:.88rem;line-height:1.72;color:#f0f6fc;word-break:break-word;">{_esc(content)}</div>
    {'<div style="font-family:monospace;font-size:.44rem;color:#8b949e;margin-top:4px;text-align:right;padding-right:46px;">'+ts+'</div>' if ts else ""}
  </div>
</div>"""

def _typing():
    d = "display:inline-block;width:7px;height:7px;border-radius:50%;background:#00e5cc;opacity:.3;margin-right:4px;"
    return f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:16px;"><div style="{AV}background:rgba(0,229,204,0.10);border:1.5px solid rgba(0,229,204,0.28);margin-top:20px;">🤖</div><div style="margin-top:20px;background:#1c2128;border:1px solid rgba(0,229,204,0.15);border-radius:3px 14px 14px 14px;padding:13px 17px;"><span style="{d}animation:tdot 1.2s infinite ease-in-out;"></span><span style="{d}animation:tdot 1.2s .15s infinite ease-in-out;"></span><span style="{d}animation:tdot 1.2s .30s infinite ease-in-out;margin-right:0;"></span></div></div>'

# ─── Main UI ──────────────────────────────────────────────────────────────────
def display_chat_ui():
    st.html("""<style>
    @keyframes tdot{0%,80%,100%{transform:translateY(0);opacity:.3;}40%{transform:translateY(-6px);opacity:1;}}
    @keyframes cur{0%,100%{opacity:1;}50%{opacity:0;}}
    @keyframes cblink{0%,100%{opacity:1;}50%{opacity:.15;}}
    [data-testid="stChatInput"],[data-testid="stChatInput"]>div,[data-testid="stChatInput"]>div>div{background:#1c2128!important;border-radius:12px!important;}
    [data-testid="stChatInput"]{border:1.5px solid rgba(0,229,204,0.26)!important;}
    [data-testid="stChatInput"]:focus-within{border-color:#00e5cc!important;box-shadow:0 0 18px rgba(0,229,204,0.12)!important;}
    [data-testid="stChatInput"] textarea{background:#1c2128!important;color:#f0f6fc!important;font-family:'Outfit',sans-serif!important;caret-color:#00e5cc!important;}
    [data-testid="stChatInput"] textarea::placeholder{color:rgba(139,148,158,0.45)!important;}
    [data-testid="stChatInput"] button{background:rgba(0,229,204,0.14)!important;border:1px solid rgba(0,229,204,0.26)!important;border-radius:8px!important;color:#00e5cc!important;}
    div[data-testid="stHorizontalBlock"] .stButton>button{font-family:'JetBrains Mono',monospace!important;font-size:.52rem!important;background:#1c2128!important;border:1px solid rgba(0,229,204,0.20)!important;color:rgba(0,229,204,0.80)!important;border-radius:50px!important;padding:6px 10px!important;width:100%!important;white-space:nowrap!important;}
    div[data-testid="stHorizontalBlock"] .stButton>button:hover{background:rgba(0,229,204,0.10)!important;border-color:#00e5cc!important;color:#fff!important;}
    </style>""")

    for k,v in [("messages",[]),("pending_qp",None),("awaiting_reply",False)]:
        if k not in st.session_state: st.session_state[k] = v

    backend = _backend()
    dot_c  = "#00e5cc" if backend=="groq" else "#4cde6e" if backend=="ollama" else "#ff6b6b"
    mdl_t  = f"● Groq · {GROQ_MODEL}" if backend=="groq" else f"● Ollama · {OLLAMA_MODEL}" if backend=="ollama" else "⚫ No backend"
    mdl_c  = "#8b949e" if backend!="none" else "#ff6b6b"

    # Status bar
    st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:9px 16px;background:#1c2128;border:1px solid rgba(0,229,204,0.20);border-radius:10px;margin-bottom:12px;">
  <div style="display:flex;align-items:center;gap:8px;"><div style="width:7px;height:7px;border-radius:50%;background:{dot_c};box-shadow:0 0 7px {dot_c};animation:cblink 2.5s ease-in-out infinite;"></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.56rem;letter-spacing:3px;text-transform:uppercase;color:#00e5cc;">AI Pathologist · MaizeBot</span></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.50rem;color:{mdl_c};background:#252c36;border:1px solid rgba(255,255,255,0.07);border-radius:50px;padding:3px 10px;">{mdl_t}</span>
</div>""", unsafe_allow_html=True)

    # Scan context banner
    scan = st.session_state.get("last_scan")
    if scan:
        sev = scan["severity"]
        sc  = "#ff6b6b" if sev=="high" else "#ffc53d" if sev=="medium" else "#4cde6e"
        ico = "🔴" if sev=="high" else "🟡" if sev=="medium" else "🟢"
        st.markdown(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:9px 14px;margin-bottom:10px;background:rgba(0,229,204,0.05);border:1px solid rgba(0,229,204,0.22);border-radius:10px;">
  <div style="display:flex;align-items:center;gap:8px;"><span>🔬</span>
    <div><div style="font-family:'JetBrains Mono',monospace;font-size:.46rem;letter-spacing:2px;text-transform:uppercase;color:#00e5cc;margin-bottom:2px;">Recent Scan · {scan['time']}</div>
    <div style="font-family:'Outfit',sans-serif;font-size:.85rem;font-weight:600;color:#f0f6fc;">{ico} {scan['disease'].replace('_',' ')}</div></div></div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:.62rem;font-weight:700;color:{sc};background:rgba(0,0,0,0.25);border:1px solid {sc}44;border-radius:50px;padding:3px 10px;">{scan['confidence']}%</span>
</div>""", unsafe_allow_html=True)

    # Messages
    msgs_box = st.container(height=440, border=False)
    with msgs_box:
        if not st.session_state.messages and not st.session_state.awaiting_reply:
            st.markdown('<div style="text-align:center;padding:4rem 1rem;"><div style="font-size:3rem;margin-bottom:.8rem;">🤖</div><div style="font-family:\'Outfit\',sans-serif;font-size:1.05rem;font-weight:700;color:rgba(240,246,252,0.85);margin-bottom:.4rem;">MaizeBot</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;letter-spacing:2px;text-transform:uppercase;color:#8b949e;">Expert maize crop health advisor</div></div>', unsafe_allow_html=True)
        else:
            for m in st.session_state.messages:
                fn = _user if m["role"]=="user" else _bot
                st.markdown(fn(m["content"], m.get("ts","")), unsafe_allow_html=True)

            if st.session_state.awaiting_reply:
                last_q  = st.session_state.messages[-1]["content"]
                history = [{"role":m["role"],"content":m["content"]} for m in st.session_state.messages[:-1]]
                ph = st.empty()
                ph.markdown(_typing(), unsafe_allow_html=True)
                reply = _respond(last_q, history)
                ph.empty()
                st.session_state.messages.append({"role":"assistant","content":reply,"ts":datetime.now().strftime("%H:%M")})
                st.session_state.awaiting_reply = False
                st.rerun()

    if backend == "none":
        st.markdown('<div style="margin:6px 0 10px;padding:10px 14px;background:rgba(255,107,107,0.09);border:1px solid rgba(255,107,107,0.24);border-radius:8px;font-size:.82rem;color:#ffc0c0;line-height:1.6;"><b>No AI backend.</b> Cloud: add <code style="background:#252c36;padding:1px 6px;border-radius:4px;font-family:monospace;color:#ffc53d;">GROQ_API_KEY</code> in Secrets. Local: run <code style="background:#252c36;padding:1px 6px;border-radius:4px;font-family:monospace;color:#ffc53d;">ollama serve</code></div>', unsafe_allow_html=True)

    user_input = st.chat_input("Describe symptoms or ask about treatment…", key="maizebot_input")

    # Suggestion pills
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:.48rem;letter-spacing:2px;text-transform:uppercase;color:#8b949e;margin:8px 0 6px;">Suggestions</div>', unsafe_allow_html=True)
    cols = st.columns(len(QUICK_PROMPTS))
    for i,(icon,label) in enumerate(QUICK_PROMPTS):
        with cols[i]:
            if st.button(f"{icon} {label}", key=f"qp_{i}"):
                st.session_state.pending_qp = label

    if st.session_state.pending_qp:
        user_input = st.session_state.pending_qp
        st.session_state.pending_qp = None

    if user_input and user_input.strip():
        st.session_state.messages.append({"role":"user","content":user_input.strip(),"ts":datetime.now().strftime("%H:%M")})
        st.session_state.awaiting_reply = True
        st.rerun()