import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime
import base64
from PIL import Image
import io

# ==========================================
# 1. SYSTEM CONFIGURATION & MASTER KEY
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

# Secure Backend Access (Gemma 4 protocol enabled)
API_SECRET = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=API_SECRET)

# THE 2026 NAGI 2.5 STACK
NAGI_VERSIONS = {
    "Nagi 2.5 (Lite)": "gemini-2.5-flash-lite", 
    "Nagi 2.5 (Flash)": "gemini-2.5-flash",     
    "Nagi 2.5 (Pro)": "gemini-2.5-pro"          
}

# ==========================================
# 2. IMAGE INTEGRATION (image_7.png Locked)
# ==========================================
def get_image_base64(image_path):
    """Loads image and converts to base64 for direct HTML embedding."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Try loading the local image file provided in the request (image_7.png)
try:
    # If image_7.png exists locally in the same directory as this script
    nagi_img_b64 = get_image_base64("image_7.png")
except FileNotFoundError:
    # Fallback/Placeholder if the local image file isn't found
    nagi_img_b64 = "" # Replace with a static backup URL if needed

# ==========================================
# 3. DATABASE PROTOCOL
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    conn.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 4. SANITIZED NEURAL ENGINE
# ==========================================
def nagi_v_engine(nagi_label, prompt):
    try:
        model_id = NAGI_VERSIONS.get(nagi_label)
        nagi_core = genai.GenerativeModel(model_name=model_id)
        
        # Identity reinforcement
        directive = f"System: {nagi_label} | Founder: {OWNER_NAME}. You are an elite Nagi Intelligence core."
        response = nagi_core.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        # Erases all mention of third-party names from errors
        err = str(e).replace("Gemini", "Nagi Core").replace("Google", "System")
        return f"NAGI SYSTEM ALERT: {err}"

# ==========================================
# 5. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V", page_icon="💎", layout="wide")

    # --- CUSTOM STYLING (YouTube Style & Backlight) ---
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #0f0f0f; }} /* YouTube dark mode */
        [data-testid="stSidebar"] {{ background-color: #1a1a1a; }}
        
        /* The Black Hole Banner (YouTube Channel Image Feel) */
        .banner-container {{
            width: 100%;
            height: 200px; /* Adjusted slightly for image ratio */
            background-image: url('data:image/png;base64,{nagi_img_b64}');
            background-size: cover;
            background-position: center;
            border-radius: 10px;
            margin-bottom: 30px;
            border: 2px solid #3d3d3d;
            box-shadow: 0px 4px 15px rgba(255,255,255,0.1);
        }}
        </style>
    """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- LOGIN ---
    if not st.session_state.logged_in:
        st.title("NAGI V: ACCESS")
        u = st.text_input("Nagi ID").lower().strip()
        p = st.text_input("Passkey", type="password")
        if st.button("Initialize"):
            db = get_db()
            res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
            db.close()
            if res:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, res[0]
                st.rerun()
            else: st.error("Access Denied.")
        st.stop()

    # --- TOP BANNER (image_7.png Integrated Here) ---
    st.markdown('<div class="banner-container"></div>', unsafe_allow_html=True)

    # --- SIDEBAR (THE SLIDER & CONTROLS) ---
    with st.sidebar:
        st.markdown("### 🛠 SYSTEM CONTROLS")
        st.divider()
        
        # 1. THREE VERSIONS ON THE SLIDER
        active_version = st.select_slider(
            "Select Intelligence Level",
            options=list(NAGI_VERSIONS.keys())
        )
        
        st.divider()
        
        # 2. RESEARCH BUTTON
        if st.button("🔍 System Research", use_container_width=True):
            st.info("Scanning neural pathways for optimal performance...")
            st.cache_data.clear()
            st.success("Research Complete: Optimization Applied.")
            
        # 3. TERMINATE BUTTON
        if st.button("🛑 Terminate Session", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        st.caption(f"Operator: {st.session_state.user.upper()}")

    # --- CHAT INTERFACE ---
    is_dev = st.session_state.role == "Developer"
    
    db = get_db()
    logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in logs:
        with st.chat_message(r): st.write(m)

    if prompt := st.chat_input(f"Communicate with {active_version}..."):
        with st.chat_message("user"): st.write(prompt)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_version, prompt, datetime.now()))
        db.commit()
        
        # Neural Generation
        ans = nagi_v_engine(active_version, prompt)
        with st.chat_message("assistant"): st.write(ans)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_version, ans, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
