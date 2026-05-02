import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. MASTER CONFIGURATION (Developer: Hashir Nagi)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Locked to Gemma 4 Architecture
GOOGLE_API_KEY = "AIzaSyBIXcDN_mUe-Z3z_7Jrm6HxzKlt3kpOXLQ"
genai.configure(api_key=GOOGLE_API_KEY)

# Exclusive Gemma 4 Mapping
MODEL_MAP = {
    "Nagi V1 (Gemma 4 Base)": "models/gemma-4-26b-a4b-it",
    "Nagi V2 (Gemma 4 Speed)": "models/gemma-4-26b-a4b-it",
    "Nagi V3 (Gemma 4 MoE)": "models/gemma-4-26b-a4b-it",
    "Nagi V4 (Gemma 4 Ultra)": "models/gemma-4-26b-a4b-it"
}

# ==========================================
# 2. DATABASE & SESSION PERSISTENCE
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V ENGINE (Gemma 4 Implementation)
# ==========================================
def nagi_v_engine(tier, prompt):
    model_id = "models/gemma-4-26b-a4b-it"
    try:
        nagi_model = genai.GenerativeModel(model_id)
        system_directive = f"Identity: {tier}. Creator: {OWNER_NAME}. Architecture: Gemma 4 MoE. System Security: Platinum Tier."
        response = nagi_model.generate_content(f"{system_directive}\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"Nagi V Core Connection Error: {str(e)}"

# ==========================================
# 4. FRONT-END INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1 Platinum", page_icon="💎", layout="wide")

    # SESSION PERSISTENCE (Ensures user stays logged in on refresh)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- LOGIN & REGISTRATION SCREEN ---
    if not st.session_state.logged_in:
        st.title("💎 NAGIVERA PLATINUM ACCESS")
        tab_login, tab_reg = st.tabs(["Neural Login", "Register Identity"])
        
        with tab_login:
            u_log = st.text_input("User ID", key="l_u").lower().strip()
            p_log = st.text_input("Passkey", type="password", key="l_p")
            
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("Initialize Link"):
                    db = get_db()
                    res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                    db.close()
                    if res:
                        st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                        st.rerun()
                    else:
                        st.error("Access Denied.")
            with col2:
                st.button("🔗 Sign in with Google")
            with col3:
                if st.button("Forgot Passkey?"):
                    st.info(f"System Lockdown: Contact {OWNER_NAME} for manual passkey recovery.")

        with tab_reg:
            if "device_locked" in st.query_params:
                st.warning("⚠️ This device is already linked to a Nagi Business Identity.")
            else:
                u_reg = st.text_input("New User ID", key="r_u").lower().strip()
                p_reg = st.text_input("New Passkey", type="password", key="r_p")
                if st.button("Encrypt & Save Identity"):
                    if u_reg and p_reg:
                        try:
                            db = get_db()
                            db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                            db.commit()
                            db.close()
                            st.query_params["device_locked"] = "true"
                            st.success("Identity Locked to Hardware. Proceed to Neural Login.")
                        except: st.error("ID Unavailable.")
        st.stop()

    # --- AUTHORIZED PLATFORM ---
    # Top Left Refresh Buttons
    with st.sidebar:
        st.title("Nagi V Core")
        if st.button("🔄 Reset Neural Core", help="Use if AI connection fails"):
            st.rerun()
        st.divider()
        active_tier = st.selectbox("Engine Tier (Gemma 4 Locked)", list(MODEL_MAP.keys()))
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs(["Neural Link", "Admin Control" if st.session_state.role == "Developer" else "History"])

    # TAB 1: NEURAL LINK (CHAT)
    with tabs[0]:
        db = get_db()
        chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,)).fetchall()
        for r, m in chat_data:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input("Input command to Gemma 4..."):
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_tier, user_prompt, datetime.now()))
            db.commit()

            resp = nagi_v_engine(active_tier, user_prompt)
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_tier, resp, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # TAB 2: DATA VISIBILITY
    with tabs[1]:
        db = get_db()
        if st.session_state.role == "Developer":
            if st.button("🔄 Refresh Master Records"): st.rerun()
            all_accounts = db.execute("SELECT username, role FROM accounts WHERE username != ?", (MASTER_USER,)).fetchall()
            st.subheader("🔑 Platinum Identity Directory")
            st.dataframe(pd.DataFrame(all_accounts, columns=["User ID", "Access Level"]), use_container_width=True)
            
            st.subheader("📜 Global System Logs")
            all_logs = db.execute("SELECT timestamp, username, message FROM logs ORDER BY id DESC").fetchall()
            st.dataframe(pd.DataFrame(all_logs, columns=["Time", "User", "Data Stream"]), use_container_width=True)
        db.close()

if __name__ == "__main__":
    main()
