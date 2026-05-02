import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. NAGI SYSTEM CONFIGURATION
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

GOOGLE_API_KEY = "AIzaSyBIXcDN_mUe-Z3z_7Jrm6HxzKlt3kpOXLQ"
genai.configure(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. AUTO-DISCOVERY (THE 404 KILLER)
# ==========================================
@st.cache_data
def get_verified_nagi_cores():
    """Dynamically fetches ONLY models guaranteed to work with your API key."""
    try:
        working_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                working_models.append(m.name)
        
        # Sort so the fastest/best models are at the top
        return sorted(working_models, key=lambda x: "flash" in x or "pro" in x, reverse=True)
    except Exception as e:
        return [f"API KEY ERROR: {str(e)}"]

# ==========================================
# 3. CORE UTILITIES & PERSISTENCE
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def nagi_v_engine(actual_model_id, prompt):
    try:
        model = genai.GenerativeModel(actual_model_id)
        # Deep expert reasoning directive, kept short for speed
        directive = f"Identity: NAGI V. Creator: {OWNER_NAME}. Provide expert, fast reasoning."
        response = model.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"NAGI V EXECUTION ERROR: {str(e)}"

# ==========================================
# 4. NAGI V TERMINAL INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="NAGI Platinum Core", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- LOGIN PORTAL ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI V SECURE ACCESS")
        u_log = st.text_input("NAGI ID", key="l_u").lower().strip()
        p_log = st.text_input("NAGI Passkey", type="password", key="l_p")
        
        if st.button("Initialize Link"):
            db = get_db()
            res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
            db.close()
            if res:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                st.rerun()
        st.stop()

    # --- MAIN PLATFORM ---
    verified_models = get_verified_nagi_cores()

    with st.sidebar:
        st.title("NAGI V Terminal")
        st.caption("Auto-Discovery Active: 0% 404 Risk")
        
        if st.button("🔄 REFRESH NETWORK"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        # The dropdown now uses the exact strings Google tells us to use
        active_model_id = st.selectbox("Select Verified Core", verified_models)
        
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    # --- CHAT UI ---
    db = get_db()
    chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in chat_data:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Command NAGI V..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_model_id, user_prompt, datetime.now()))
        
        resp = nagi_v_engine(active_model_id, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_model_id, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
