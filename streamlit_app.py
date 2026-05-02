import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. SYSTEM ARCHITECTURE & BRANDING
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Secure API Configuration
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# MAPPING GOOGLE CORES TO NAGI VERSIONS
# We assign your specific version numbers to the best performing models.
NAGI_VERSION_MAP = {
    "Nagi v1.5 (High-Speed)": "models/gemini-1.5-flash",
    "Nagi v1.7 (Deep Reasoning)": "models/gemini-1.5-pro",
    "Nagi v2.5 (Pro-Expert)": "models/gemini-1.5-pro-002",
    "Nagi v2.7 (Ultra-Fast)": "models/gemini-1.5-flash-002",
    "Nagi v1.2 (Legacy Core)": "models/gemini-1.0-pro"
}

# ==========================================
# 2. DATABASE ENGINE
# ==========================================
def get_db():
    conn = sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    # Seed Master Developer Account
    conn.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. NAGI V INTELLIGENCE LAYER
# ==========================================
def nagi_v_engine(nagi_version_name, prompt):
    try:
        # Pull the actual Google model path from our Nagi Map
        actual_model_path = NAGI_VERSION_MAP.get(nagi_version_name)
        
        nagi_core = genai.GenerativeModel(model_name=actual_model_path)
        
        # System instruction forces the AI to acknowledge its Nagi identity
        directive = f"You are {nagi_version_name}, a custom-built intelligence by {OWNER_NAME}."
        response = nagi_core.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"NAGI V CORE ERROR: {str(e)}"

# ==========================================
# 4. NAGI V OPERATING SYSTEM UI
# ==========================================
def main():
    st.set_page_config(page_title="NAGI V Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- THE SECURE LOGIN PORTAL ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI V: SYSTEM ACCESS")
        
        tab_login, tab_reg = st.tabs(["Neural Login", "Register Identity"])
        
        with tab_login:
            u_log = st.text_input("NAGI ID", key="l_u").lower().strip()
            p_log = st.text_input("NAGI Passkey", type="password", key="l_p")
            
            if st.button("Initialize Link"):
                db = get_db()
                res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                db.close()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Identity Credentials.")

        with tab_reg:
            u_reg = st.text_input("New NAGI ID", key="r_u").lower().strip()
            p_reg = st.text_input("New NAGI Passkey", type="password", key="r_p")
            if st.button("Encrypt & Save Identity"):
                if u_reg and p_reg:
                    db = get_db()
                    try:
                        db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                        db.commit()
                        st.success(f"Identity '{u_reg}' has been secured to the database.")
                    except: st.error("ID Cluster Occupied. Try a different username.")
                    db.close()
        st.stop()

    # --- MAIN ENVIRONMENT ---
    with st.sidebar:
        st.header(f"NAGI V Control")
        st.caption(f"Operator: {st.session_state.user.upper()}")
        
        st.divider()
        # User selects the AI by your custom Nagi Version names
        active_nagi_version = st.selectbox("Select Nagi Intelligence Version", list(NAGI_VERSION_MAP.keys()))
        
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    # TABS: ADMIN CONTROL LOCKED TO DEVELOPER ROLE
    if st.session_state.role == "Developer":
        tab_chat, tab_admin = st.tabs(["NAGI Neural Link", "NAGI Admin Control"])
    else:
        tab_chat = st.tabs(["NAGI Neural Link"])[0]
        tab_admin = None

    # --- TAB 1: NEURAL LINK (CHAT) ---
    with tab_chat:
        db = get_db()
        # Limit history for peak performance
        logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
        
        for r, m in logs:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input(f"Command {active_nagi_version}..."):
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_nagi_version, user_prompt, datetime.now()))
            db.commit()
            
            # Send to engine
            resp = nagi_v_engine(active_nagi_version, user_prompt)
            
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_nagi_version, resp, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # --- TAB 2: ADMIN CONTROL (DEVELOPER ONLY) ---
    if tab_admin:
        with tab_admin:
            st.subheader("🔑 Identity Management")
            db = get_db()
            users_df = pd.read_sql_query("SELECT username, role FROM accounts", db)
            st.dataframe(users_df, use_container_width=True)

            st.subheader("📜 Global Network Logs")
            logs_df = pd.read_sql_query("SELECT timestamp, username, model, message FROM logs ORDER BY id DESC", db)
            st.dataframe(logs_df, use_container_width=True)
            
            if st.button("🗑️ Purge Global History"):
                db.execute("DELETE FROM logs")
                db.commit()
                st.warning("All neural logs have been cleared.")
                st.rerun()
            db.close()

if __name__ == "__main__":
    main()
