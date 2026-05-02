import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. SYSTEM ARCHITECTURE
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Secure API Configuration
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. DATABASE ENGINE
# ==========================================
def get_db():
    conn = sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)
    # Ensure tables exist
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    # Seed Master Account
    conn.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. NAGI V INTELLIGENCE LAYER
# ==========================================
@st.cache_data
def discover_nagi_cores():
    """Dynamically fetches models to prevent format errors (The 400/404 Fix)."""
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-1.5-flash", "models/gemini-1.5-pro"]

def nagi_v_engine(model_path, prompt):
    try:
        nagi_core = genai.GenerativeModel(model_name=model_path)
        directive = f"System: NAGI V | Founder: {OWNER_NAME}. Provide expert reasoning."
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

    # --- CLEAN LOGIN INTERFACE ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI V: SECURE ACCESS")
        
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
                    st.error("Access Denied: Invalid Credentials.")

        with tab_reg:
            u_reg = st.text_input("New NAGI ID", key="r_u").lower().strip()
            p_reg = st.text_input("New NAGI Passkey", type="password", key="r_p")
            if st.button("Encrypt Identity"):
                if u_reg and p_reg:
                    db = get_db()
                    try:
                        db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                        db.commit()
                        st.success("Identity Locked to Database.")
                    except: st.error("ID Cluster Occupied.")
                    db.close()
        st.stop()

    # --- MAIN SYSTEM ENVIRONMENT ---
    verified_cores = discover_nagi_cores()

    with st.sidebar:
        st.header("NAGI V Core Control")
        if st.button("🔄 REFRESH NEURAL GRID"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        active_core = st.selectbox("Intelligence Tier", verified_cores)
        
        if st.button("Terminate Session"):
            st.session_state.logged_in = False
            st.rerun()

    # TABS: ADMIN CONTROL IS BACK
    app_tabs = ["NAGI Neural Link", "NAGI Admin Control"]
    # Only show Admin tab to the Developer
    actual_tabs = st.tabs(app_tabs if st.session_state.role == "Developer" else ["NAGI Neural Link"])

    # --- TAB 1: NEURAL LINK (CHAT) ---
    with actual_tabs[0]:
        db = get_db()
        logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
        
        for r, m in logs:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input("Command NAGI V..."):
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_core, user_prompt, datetime.now()))
            db.commit()
            
            resp = nagi_v_engine(active_core, user_prompt)
            
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_core, resp, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # --- TAB 2: ADMIN CONTROL (DEVELOPER ONLY) ---
    if st.session_state.role == "Developer":
        with actual_tabs[1]:
            st.subheader("🔑 Identity Directory")
            db = get_db()
            users_df = pd.read_sql_query("SELECT username, role FROM accounts", db)
            st.dataframe(users_df, use_container_width=True)

            st.subheader("📜 Global Neural Logs")
            logs_df = pd.read_sql_query("SELECT timestamp, username, model, message FROM logs ORDER BY id DESC", db)
            st.dataframe(logs_df, use_container_width=True)
            
            if st.button("🗑️ Purge System Logs"):
                db.execute("DELETE FROM logs")
                db.commit()
                st.warning("System logs cleared.")
                st.rerun()
            db.close()

if __name__ == "__main__":
    main()
