import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. MASTER CONFIGURATION (SECRET)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

GOOGLE_API_KEY = "AIzaSyBIXcDN_mUe-Z3z_7Jrm6HxzKlt3kpOXLQ"
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_MAP = {
    "Nagi V1 (Flash)": "gemini-3.1-flash-lite-preview",
    "Nagi V2 (Speed)": "gemini-3-flash-preview",
    "Nagi V3 (MoE)": "models/gemma-4-26b-a4b-it",
}

# ==========================================
# 2. DATABASE SYSTEM
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    # Master account is inserted but will be filtered out of views
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V ENGINE
# ==========================================
def nagi_v_engine(tier, prompt):
    try:
        model_id = MODEL_MAP.get(tier, "gemini-3.1-flash-lite-preview")
        nagi_model = genai.GenerativeModel(model_id)
        system_directive = f"You are {tier}, a Nagi V intelligence by {OWNER_NAME}. Never mention external providers."
        response = nagi_model.generate_content(f"{system_directive}\nUser: {prompt}")
        return response.text
    except Exception:
        return "Nagi V Core Connection Error."

# ==========================================
# 4. FRONT-END INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1 Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- LOGIN & REGISTRATION SCREEN ---
    if not st.session_state.logged_in:
        st.title("💎 NAGIVERA PLATINUM ACCESS")
        tab_login, tab_reg = st.tabs(["Neural Login", "Register Identity"])
        
        with tab_login:
            u_log = st.text_input("User ID", key="l_u").lower().strip()
            p_log = st.text_input("Passkey", type="password", key="l_p")
            if st.button("Initialize Link"):
                db = get_db()
                res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                db.close()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                    st.rerun()
                else:
                    st.error("Access Denied.")

        with tab_reg:
            st.info("Registration creates a permanent Business Identity.")
            u_reg = st.text_input("New User ID", key="r_u").lower().strip()
            p_reg = st.text_input("New Passkey", type="password", key="r_p")
            if st.button("Encrypt & Save"):
                if u_reg and p_reg:
                    # Prevent anyone from trying to register as the master name
                    if u_reg == MASTER_USER:
                        st.error("Reserved Identity.")
                    else:
                        try:
                            db = get_db()
                            db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                            db.commit()
                            db.close()
                            st.success("Identity Locked.")
                        except: st.error("ID Unavailable.")
        st.stop()

    # --- AUTHORIZED PLATFORM ---
    st.sidebar.title("Nagi V Core")
    active_tier = st.sidebar.selectbox("Engine Tier", list(MODEL_MAP.keys()))
    
    if st.sidebar.button("Terminate Link"):
        st.session_state.logged_in = False
        st.rerun()

    tab_list = ["Neural Link", "Admin Control"] if st.session_state.role == "Developer" else ["Neural Link", "Identity History"]
    tabs = st.tabs(tab_list)

    # TAB 1: NEURAL LINK
    with tabs[0]:
        db = get_db()
        chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,)).fetchall()
        for r, m in chat_data:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input("Input command..."):
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
            st.header("Master Admin Control")
            
            # IDENTITY DIRECTORY (HIDDEN MASTER)
            st.subheader("🔑 Identity Directory")
            # This query specifically EXCLUDES the master user from the list
            all_accounts = db.execute("SELECT username, password, role FROM accounts WHERE username != ?", (MASTER_USER,)).fetchall()
            if all_accounts:
                st.dataframe(pd.DataFrame(all_accounts, columns=["User ID", "Passkey", "Access Level"]), use_container_width=True)
            else:
                st.info("No external identities registered.")

            # GLOBAL HISTORY
            st.subheader("📜 Global Neural History")
            all_logs = db.execute("SELECT timestamp, username, model, message FROM logs ORDER BY id DESC").fetchall()
            st.dataframe(pd.DataFrame(all_logs, columns=["Time", "User", "Tier", "Data"]), use_container_width=True)
        else:
            st.header("Permanent Neural History")
            my_logs = db.execute("SELECT timestamp, model, message FROM logs WHERE username=? AND role='assistant' ORDER BY id DESC", (st.session_state.user,)).fetchall()
            if my_logs:
                st.dataframe(pd.DataFrame(my_logs, columns=["Time", "Tier", "Intelligence Output"]), use_container_width=True)
        db.close()

if __name__ == "__main__":
    main()
