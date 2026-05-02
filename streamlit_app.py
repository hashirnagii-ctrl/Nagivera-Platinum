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
# 2. AUTO-DISCOVERY & ERROR SANITIZATION
# ==========================================
@st.cache_data
def get_verified_nagi_cores():
    """Fetches and sanitizes models to eliminate name format errors."""
    try:
        working_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Store the short name to prevent "unexpected format" errors
                clean_name = m.name.replace("models/", "")
                working_models.append(clean_name)
        
        # Prioritize high-performance cores
        return sorted(working_models, key=lambda x: "flash" in x or "pro" in x, reverse=True)
    except Exception as e:
        return [f"KEY_ERROR: {str(e)}"]

# ==========================================
# 3. NAGI V STABILIZED ENGINE
# ==========================================
def nagi_v_engine(clean_model_id, prompt):
    try:
        # Re-apply prefix only if needed by specific backend
        full_model_path = f"models/{clean_model_id}"
        model = genai.GenerativeModel(full_model_path)
        
        directive = f"Identity: NAGI V. Creator: {OWNER_NAME}. Response Mode: Expert Reasoning."
        response = model.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"NAGI V CORE ERROR: {str(e)}"

# ==========================================
# 4. NAGI V PLATINUM INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="NAGI V Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- ENHANCED LOGIN PORTAL ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI V SECURE ACCESS")
        
        tab1, tab2 = st.tabs(["NAGI Login", "Register Identity"])
        
        with tab1:
            u_log = st.text_input("NAGI ID", key="l_u").lower().strip()
            p_log = st.text_input("Passkey", type="password", key="l_p")
            
            col_a, col_b = st.columns([1, 2])
            with col_a:
                if st.button("Initialize Link"):
                    db = sqlite3.connect('nagivera_platinum_master.db')
                    res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                    db.close()
                    if res:
                        st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                        st.rerun()
                    else:
                        st.error("Invalid Credentials.")
            
            with col_b:
                st.button("🔴 Sign in with Google (OAuth)")

            st.write("---")
            if st.button("Forgot Passkey / Password?"):
                st.info(f"System lockdown active. Please contact {OWNER_NAME} for manual passkey override.")

        with tab2:
            u_reg = st.text_input("New NAGI ID", key="r_u").lower().strip()
            p_reg = st.text_input("New Passkey", type="password", key="r_p")
            if st.button("Encrypt Identity"):
                if u_reg and p_reg:
                    db = sqlite3.connect('nagivera_platinum_master.db')
                    try:
                        db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                        db.commit()
                        st.success("Identity Secured.")
                    except: st.error("ID Already Exists.")
                    db.close()
        st.stop()

    # --- NAGI V OPERATING ENVIRONMENT ---
    verified_models = get_verified_nagi_cores()

    with st.sidebar:
        st.header("NAGI V Terminal")
        if st.button("🔄 REFRESH NEURAL NET"):
            st.cache_data.clear()
            st.rerun()
            
        st.divider()
        active_model_id = st.selectbox("Active NAGI Core", verified_models)
        
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    # --- CHAT UI ---
    db = sqlite3.connect('nagivera_platinum_master.db')
    chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in chat_data:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Command NAGI V..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_model_id, user_prompt, datetime.now()))
        db.commit()
        
        resp = nagi_v_engine(active_model_id, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_model_id, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
