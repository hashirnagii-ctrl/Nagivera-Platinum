import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime
import re

# ==========================================
# 1. SYSTEM ARCHITECTURE & MASTER BRANDING
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

# Secure Backend Configuration (Hidden from User)
API_SECRET = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=API_SECRET)

# THE TRIPLE-TIER NAGI SYSTEM
# Mapping internal IDs to your custom Nagi Versions
NAGI_CORES = {
    "Nagi v1.0 (Light)": "gemini-1.5-flash-8b", # Near-instant speed
    "Nagi v2.0 (Pro)": "gemini-1.5-flash",      # High-performance balance
    "Nagi v3.0 (Ultra)": "gemini-1.5-pro"       # Maximum expert reasoning
}

# ==========================================
# 2. DATA PERSISTENCE LAYER
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_master.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    conn.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. SANITIZED NEURAL ENGINE
# ==========================================
def nagi_v_engine(nagi_label, prompt):
    try:
        model_id = NAGI_CORES.get(nagi_label)
        nagi_core = genai.GenerativeModel(model_name=model_id)
        
        # Directive to ensure the AI knows its identity
        directive = f"System: {nagi_label} | Founder: {OWNER_NAME}. You are a custom Nagi Intelligence."
        response = nagi_core.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    
    except Exception as e:
        # BRAND SANITIZATION: Removes any mention of Google/Gemini from raw error messages
        raw_error = str(e)
        sanitized_error = raw_error.replace("Gemini", "Nagi").replace("Google", "Nagi System")
        return f"NAGI CORE ERROR: {sanitized_error}"

# ==========================================
# 4. NAGI V OPERATING SYSTEM UI
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V Platinum", page_icon="💎", layout="wide")

    # Hide Streamlit branding for a cleaner "Nagi" feel
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- SECURE LOGIN PORTAL ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI V: SYSTEM ACCESS")
        
        tab_login, tab_reg = st.tabs(["Secure Login", "Register Identity"])
        
        with tab_login:
            u_log = st.text_input("Nagi ID", key="l_u").lower().strip()
            p_log = st.text_input("Nagi Passkey", type="password", key="l_p")
            
            if st.button("Initialize Neural Link"):
                db = get_db()
                res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                db.close()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                    st.rerun()
                else:
                    st.error("Authentication Failed: Identity not recognized.")

        with tab_reg:
            u_reg = st.text_input("New Nagi ID", key="r_u").lower().strip()
            p_reg = st.text_input("New Nagi Passkey", type="password", key="r_p")
            if st.button("Encrypt Identity"):
                if u_reg and p_reg:
                    db = get_db()
                    try:
                        db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                        db.commit()
                        st.success(f"Identity '{u_reg}' secured.")
                    except: st.error("ID Cluster Occupied.")
                    db.close()
        st.stop()

    # --- MAIN OPERATING ENVIRONMENT ---
    with st.sidebar:
        st.header("Nagi V Control")
        st.caption(f"Operator: {st.session_state.user.upper()}")
        st.divider()
        
        # Pure Nagi Branding in the selection
        active_version = st.selectbox("Select Nagi Intelligence Version", list(NAGI_CORES.keys()))
        
        if st.button("Terminate Session"):
            st.session_state.logged_in = False
            st.rerun()

    # Admin visibility logic
    is_dev = st.session_state.role == "Developer"
    tabs = st.tabs(["Nagi Neural Link", "Nagi Admin Control"]) if is_dev else [st.container()]

    # --- CHAT INTERFACE ---
    with (tabs[0] if is_dev else tabs[0]):
        db = get_db()
        logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
        
        for r, m in logs:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input(f"Command {active_version}..."):
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_version, user_prompt, datetime.now()))
            db.commit()
            
            # Execute engine and display response
            resp = nagi_v_engine(active_version, user_prompt)
            
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_version, resp, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # --- ADMIN CONTROL CENTER ---
    if is_dev:
        with tabs[1]:
            st.subheader("🔑 Managed Identity Directory")
            db = get_db()
            st.dataframe(pd.read_sql_query("SELECT username, role FROM accounts", db), use_container_width=True)

            st.subheader("📜 Global Nagi Logs")
            st.dataframe(pd.read_sql_query("SELECT timestamp, username, model, message FROM logs ORDER BY id DESC", db), use_container_width=True)
            
            if st.button("🗑️ Wipe All Logs"):
                db.execute("DELETE FROM logs")
                db.commit()
                st.warning("All neural logs have been cleared.")
                st.rerun()
            db.close()

if __name__ == "__main__":
    main()
