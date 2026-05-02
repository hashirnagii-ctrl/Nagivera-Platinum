import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. SYSTEM CONFIGURATION & MASTER KEY
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

# Secure Backend Access
API_SECRET = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=API_SECRET)

# THE 2026 NAGI 2.5 STACK (Fixed 404 Errors)
NAGI_VERSIONS = {
    "Nagi 2.5 (Lite)": "gemini-2.5-flash-lite", # High-speed cost-effective
    "Nagi 2.5 (Flash)": "gemini-2.5-flash",     # Balanced price/performance
    "Nagi 2.5 (Pro)": "gemini-2.5-pro"          # Advanced reasoning/coding
}

# ==========================================
# 2. DATABASE PROTOCOL
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
# 3. SANITIZED NEURAL ENGINE (Fixed for 2.5)
# ==========================================
def nagi_v_engine(nagi_label, prompt):
    try:
        model_id = NAGI_VERSIONS.get(nagi_label)
        nagi_core = genai.GenerativeModel(model_name=model_id)
        
        # Identity reinforcement - No Vera mention
        directive = f"System: {nagi_label} | Founder: {OWNER_NAME}. You are an elite Nagi Intelligence core."
        response = nagi_core.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        # Erases all mention of third-party names from errors
        err = str(e).replace("Gemini", "Nagi Core").replace("Google", "System")
        return f"NAGI SYSTEM ALERT: {err}"

# ==========================================
# 4. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V", page_icon="💎", layout="wide")

    # --- CUSTOM STYLING (YouTube Style & Backlight) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0f0f0f; } /* YouTube dark mode */
        [data-testid="stSidebar"] { background-color: #1a1a1a; }
        
        /* YouTube-style Top Banner */
        .banner-container {
            width: 100%;
            height: 180px;
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            border-radius: 0 0 15px 15px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-bottom: 2px solid #3d3d3d;
        }
        .banner-text { 
            color: white; 
            font-size: 50px; 
            font-weight: 800; 
            letter-spacing: 2px;
            text-shadow: 0px 4px 10px rgba(0,0,0,0.8);
        }
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

    # --- TOP BANNER (YouTube Channel Image) ---
    st.markdown('<div class="banner-container"><div class="banner-text">NAGI V PLATINUM</div></div>', unsafe_allow_html=True)

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
        st.caption(f"Hardware Mode: RYZEN Core") # Per user preference
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
