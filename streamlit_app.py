import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. SYSTEM ARCHITECTURE (NAGI V)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Your Secure API Key
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. CORE UTILITIES
# ==========================================
def get_db():
    conn = sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    conn.commit()
    return conn

@st.cache_data
def discover_nagi_cores():
    """
    Kills the 400 error by fetching exact model strings 
    directly from the source.
    """
    try:
        # We fetch the exact strings recognized by your API key
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception:
        # Fallback if list_models fails
        return ["models/gemini-1.5-flash", "models/gemini-1.5-pro"]

def nagi_v_engine(model_path, prompt):
    try:
        # Ensures the string is perfectly formatted for the request
        nagi_core = genai.GenerativeModel(model_name=model_path)
        directive = f"System: NAGI V | Founder: {OWNER_NAME} | Mode: Expert Intelligence."
        response = nagi_core.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"CORE INTERRUPT: {str(e)}"

# ==========================================
# 3. INTERFACE (NAGI V OPERATING SYSTEM)
# ==========================================
def main():
    st.set_page_config(page_title="NAGI V Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- CEO-TIER LOGIN INTERFACE ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI V: SECURE INTERFACE")
        
        tab_login, tab_reg = st.tabs(["Neural Login", "New Identity"])
        
        with tab_login:
            u_log = st.text_input("NAGI ID", key="l_u").lower().strip()
            p_log = st.text_input("NAGI Passkey", type="password", key="l_p")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                if st.button("Initialize Link"):
                    db = get_db()
                    res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                    db.close()
                    if res:
                        st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                        st.rerun()
                    else: st.error("Access Denied.")
            
            with c2:
                # REQUESTED: Silent Google Auth Placeholder
                st.button("🔴 Sign in with Google", help="One-tap Neural Link")

            st.write("---")
            # REQUESTED: Forget Password Utility
            if st.button("Forgot Passkey?"):
                st.info(f"Identity recovery protocol initiated. Please verify with {OWNER_NAME} for manual override.")

        with tab_reg:
            u_reg = st.text_input("New NAGI ID", key="r_u").lower().strip()
            p_reg = st.text_input("New NAGI Passkey", type="password", key="r_p")
            if st.button("Encrypt & Save Identity"):
                if u_reg and p_reg:
                    db = get_db()
                    try:
                        db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                        db.commit()
                        st.success("Identity Locked.")
                    except: st.error("ID Cluster Occupied.")
                    db.close()
        st.stop()

    # --- MAIN NAGI V TERMINAL ---
    verified_cores = discover_nagi_cores()

    with st.sidebar:
        st.header("NAGI V Core Control")
        if st.button("🔄 REFRESH NEURAL GRID"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        # Dropdown uses the exact strings that fixed the 400 error
        active_core = st.selectbox("Select Intelligence Core", verified_cores)
        
        if st.button("Terminate Session"):
            st.session_state.logged_in = False
            st.rerun()

    # --- NEURAL CHAT STREAM ---
    db = get_db()
    logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 12", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in logs:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Command NAGI V..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_core, user_prompt, datetime.now()))
        db.commit()
        
        # Call optimized engine
        resp = nagi_v_engine(active_core, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_core, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
