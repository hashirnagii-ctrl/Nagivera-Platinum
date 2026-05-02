import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

API_SECRET = "AIzaSyDxtxyI0s2L7gpyTyz2blQCOmEBv0Is18o"
genai.configure(api_key=API_SECRET)

# THE 2026 NAGI 2.5 STACK
NAGI_VERSIONS = {
    "Nagi 2.5 (Lite)": "gemini-2.5-flash-lite", 
    "Nagi 2.5 (Flash)": "gemini-2.5-flash",     
    "Nagi 2.5 (Pro)": "gemini-2.5-pro"          
}

# ==========================================
# 2. IMAGE HANDLER (Fixed to navigera.png)
# ==========================================
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Mapping to your specific filename
nagi_img_b64 = get_image_base64("navigera.png")

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
# 4. NEURAL ENGINE
# ==========================================
def nagi_v_engine(nagi_label, prompt):
    try:
        model_id = NAGI_VERSIONS.get(nagi_label)
        nagi_core = genai.GenerativeModel(model_name=model_id)
        directive = f"System: {nagi_label} | Founder: {OWNER_NAME}. You are an elite Nagi Intelligence core."
        response = nagi_core.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        err = str(e).replace("Gemini", "Nagi Core").replace("Google", "System")
        return f"NAGI SYSTEM ALERT: {err}"

# ==========================================
# 5. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V", page_icon="💎", layout="wide")

    # --- CUSTOM STYLING (YouTube Style & Backlight Effect) ---
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #0f0f0f; }} 
        [data-testid="stSidebar"] {{ background-color: #1a1a1a; }}
        
        /* The Black Hole Banner with Backlight Glow */
        .banner-container {{
            width: 100%;
            height: 250px;
            background-image: url('data:image/png;base64,{nagi_img_b64 if nagi_img_b64 else ""}');
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            background-color: black;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 1px solid #333;
            /* Backlight Effect */
            box-shadow: 0px 0px 20px 2px rgba(255, 255, 255, 0.05);
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

    # --- TOP BANNER (Displays navigera.png) ---
    st.markdown('<div class="banner-container"></div>', unsafe_allow_html=True)

    # --- SIDEBAR CONTROLS ---
    with st.sidebar:
        st.markdown("### 🛠 SYSTEM CONTROLS")
        st.divider()
        active_version = st.select_slider("Intelligence Level", options=list(NAGI_VERSIONS.keys()))
        st.divider()
        if st.button("🔍 System Research", use_container_width=True):
            st.cache_data.clear()
            st.success("Optimization Applied.")
        if st.button("🛑 Terminate Session", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.caption(f"Operator: {st.session_state.user.upper()}")

    # --- CHAT INTERFACE ---
    db = get_db()
    logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
    for r, m in logs:
        with st.chat_message(r): st.write(m)

    if prompt := st.chat_input(f"Communicate with {active_version}..."):
        with st.chat_message("user"): st.write(prompt)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_version, prompt, datetime.now()))
        db.commit()
        ans = nagi_v_engine(active_version, prompt)
        with st.chat_message("assistant"): st.write(ans)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_version, ans, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
