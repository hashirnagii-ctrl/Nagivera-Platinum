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

# THE TRIPLE-TIER NAGI CORES (Optimized for 2026 Speed)
NAGI_VERSIONS = {
    "Nagi 1.5 (Light)": "gemini-1.5-flash-8b",
    "Nagi 2.0 (Pro)": "gemini-1.5-flash",
    "Nagi 2.5 (Ultra)": "gemini-1.5-pro" # Mapped to the most powerful reasoning engine
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
# 3. SANITIZED NEURAL ENGINE (NO ERRORS)
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
# 4. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V", page_icon="💎", layout="wide")

    # --- CUSTOM STYLING (YouTube Banner Feel) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        [data-testid="stSidebar"] { background-color: #161b22; }
        .banner-box {
            width: 100%;
            height: 200px;
            background-image: url('https://images.unsplash.com/photo-1635776062127-d379bfcba9f8?q=80&w=2532&auto=format&fit=crop');
            background-size: cover;
            background-position: center;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: flex-end;
            padding: 20px;
        }
        .banner-text { color: white; font-size: 45px; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        </style>
    """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- LOGIN PORTAL ---
    if not st.session_state.logged_in:
        st.title("NAGI V: ACCESS PORTAL")
        u = st.text_input("Nagi ID").lower().strip()
        p = st.text_input("Passkey", type="password")
        if st.button("Initialize"):
            db = get_db()
            res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
            db.close()
            if res:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, res[0]
                st.rerun()
            else: st.error("Identity unknown.")
        st.stop()

    # --- TOP BANNER (YouTube Channel Style) ---
    st.markdown(f'<div class="banner-box"><div class="banner-text">NAGI V SYSTEM</div></div>', unsafe_allow_html=True)

    # --- SIDEBAR (THE SLIDE CONTROL) ---
    with st.sidebar:
        st.title("System Controls")
        st.divider()
        
        # Model Selection
        active_version = st.selectbox("Intelligence Version", list(NAGI_VERSIONS.keys()))
        
        # Action Buttons
        if st.button("🔄 Refresh Neural Grid", use_container_width=True):
            st.cache_data.clear()
            st.success("Grid Synced.")
            
        if st.button("🔴 Terminate Session", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        st.caption(f"Operator: {st.session_state.user.upper()}")

    # --- ADMIN / CHAT TABS ---
    is_dev = st.session_state.role == "Developer"
    tabs = st.tabs(["Neural Link", "Admin Control"]) if is_dev else [st.container()]

    # --- CHAT INTERFACE ---
    with (tabs[0] if is_dev else tabs[0]):
        db = get_db()
        logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 20", (st.session_state.user,)).fetchall()[::-1]
        for r, m in logs:
            with st.chat_message(r): st.write(m)

        if prompt := st.chat_input(f"Interacting via {active_version}..."):
            with st.chat_message("user"): st.write(prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_version, prompt, datetime.now()))
            db.commit()
            
            # Response
            ans = nagi_v_engine(active_version, prompt)
            with st.chat_message("assistant"): st.write(ans)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_version, ans, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # --- ADMIN PANEL ---
    if is_dev:
        with tabs[1]:
            st.subheader("Global Identity Directory")
            db = get_db()
            st.dataframe(pd.read_sql_query("SELECT username, role FROM accounts", db), use_container_width=True)
            st.subheader("System Traffic Logs")
            st.dataframe(pd.read_sql_query("SELECT timestamp, username, model, message FROM logs ORDER BY id DESC", db), use_container_width=True)
            if st.button("Purge Global Traffic"):
                db.execute("DELETE FROM logs")
                db.commit()
                st.rerun()
            db.close()

if __name__ == "__main__":
    main()
