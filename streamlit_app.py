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

# RE-VERIFY THIS KEY in your Google AI Studio
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_MAP = {
    "NAGI V (Flash)": "models/gemini-1.5-flash",
    "NAGI V (Gemma 4 Core)": "models/gemma-4-26b-a4b-it",
    "NAGI V (Pro)": "models/gemini-1.5-pro"
}

# ==========================================
# 2. CORE UTILITIES
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

@st.cache_resource
def get_model(model_id):
    return genai.GenerativeModel(model_id)

def nagi_v_engine(tier, prompt):
    model_id = MODEL_MAP.get(tier, "models/gemini-1.5-flash")
    try:
        model = get_model(model_id)
        # Simplified directive to reduce 'Token Overhead' which causes slowness
        response = model.generate_content(f"You are {tier} by {OWNER_NAME}. User: {prompt}")
        return response.text
    except Exception as e:
        # TRAP THE REAL ERROR: This will help us see WHY it is failing
        return f"NAGI V DEBUG ERROR: {str(e)}"

# ==========================================
# 3. INTERFACE & PERSISTENCE
# ==========================================
def main():
    st.set_page_config(page_title="NAGI Platinum", layout="wide")

    # SESSION PERSISTENCE (Refresh Lock)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("💎 NAGI PLATINUM ACCESS")
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

    # SIDEBAR CONTROLS
    with st.sidebar:
        st.title("NAGI V Core")
        if st.button("🔄 EMERGENCY RESET"):
            st.cache_resource.clear() # Clears the "stuck" model memory
            st.rerun()
        active_tier = st.selectbox("Engine Tier", list(MODEL_MAP.keys()))
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    # CHAT INTERFACE
    db = get_db()
    # Loading only 10 messages for max speed
    chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 10", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in chat_data:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Command NAGI V..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_tier, user_prompt, datetime.now()))
        
        # Call Engine
        resp = nagi_v_engine(active_tier, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_tier, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
