import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. MASTER CONFIGURATION
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# HYBRID ENGINE MAPPING
# We use the Flash model for the standard Nagi V tiers to maximize speed.
MODEL_MAP = {
    "NAGI V (Speed-Flash)": "models/gemini-1.5-flash",
    "NAGI V (Gemma 4 Core)": "models/gemma-4-26b-a4b-it",
    "NAGI V (Platinum-Pro)": "models/gemini-1.5-pro"
}

# ==========================================
# 2. PERFORMANCE & PERSISTENCE
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

@st.cache_resource
def load_nagi_engine(model_id):
    return genai.GenerativeModel(model_id)

# ==========================================
# 3. NAGI V HYBRID ENGINE
# ==========================================
def nagi_v_engine(tier, prompt):
    model_id = MODEL_MAP.get(tier, "models/gemini-1.5-flash")
    try:
        nagi_model = load_nagi_engine(model_id)
        # Compact directive for minimal latency
        directive = f"You are {tier}, a NAGI V intelligence by {OWNER_NAME}."
        response = nagi_model.generate_content(f"{directive}\nUser: {prompt}")
        return response.text
    except Exception:
        return "NAGI V Core Connection Error."

# ==========================================
# 4. INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="NAGI Platinum", page_icon="💎", layout="wide")

    # SESSION PERSISTENCE (Refresh Protection)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("💎 NAGI PLATINUM ACCESS")
        u_log = st.text_input("NAGI ID", key="l_u").lower().strip()
        p_log = st.text_input("NAGI Passkey", type="password", key="l_p")
        
        col1, col2 = st.columns([1,4])
        with col1:
            if st.button("Initialize Link"):
                db = get_db()
                res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                db.close()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                    st.rerun()
        with col2:
            st.button("🔗 Sign in with Google")
        st.stop()

    # --- OPERATING ENVIRONMENT ---
    with st.sidebar:
        st.title("NAGI V Core")
        if st.button("🔄 Reset NAGI V"):
            st.rerun()
        st.divider()
        # The user can now choose between the high-speed Flash tier or the Gemma 4 tier
        active_tier = st.selectbox("Select NAGI V Engine", list(MODEL_MAP.keys()))
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    # Optimized History (Limit to 15 messages for extreme speed)
    db = get_db()
    chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in chat_data:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Enter NAGI command..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_tier, user_prompt, datetime.now()))
        
        # Call the hybrid engine
        resp = nagi_v_engine(active_tier, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_tier, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
