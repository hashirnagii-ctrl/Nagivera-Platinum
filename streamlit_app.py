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

# Your Google API Key
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# THE FIX: Removed the "models/" prefix that caused the 404 error.
# Using the stable, exact model names for Speed and Deep Reasoning.
MODEL_MAP = {
    "NAGI V (Hyper-Speed)": "gemini-1.5-flash",    # Blazing fast, great for high volume
    "NAGI V (Deep Expert)": "gemini-1.5-pro",      # Slower, but provides expert-level reasoning
}

# ==========================================
# 2. CORE UTILITIES & PERSISTENCE
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

@st.cache_resource
def get_model(model_id):
    # Caching prevents reloading the model every time, ensuring max speed
    return genai.GenerativeModel(model_id)

def nagi_v_engine(tier, prompt):
    model_id = MODEL_MAP.get(tier, "gemini-1.5-flash")
    try:
        model = get_model(model_id)
        # Direct, lightweight system instruction to prevent lag
        directive = f"You are {tier}, an expert AI system named NAGI V. Created by {OWNER_NAME}."
        response = model.generate_content(f"{directive}\n\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"NAGI V SYSTEM ERROR: {str(e)}"

# ==========================================
# 3. INTERFACE (NAGI V TERMINAL)
# ==========================================
def main():
    st.set_page_config(page_title="NAGI Platinum Core", layout="wide")

    # Keep user logged in during refreshes
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

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

    # SIDEBAR
    with st.sidebar:
        st.title("NAGI V Terminal")
        if st.button("🔄 HARD RESET", help="Clears system cache if AI hangs"):
            st.cache_resource.clear()
            st.rerun()
            
        st.divider()
        # User selects between Hyper-Speed or Deep Expert
        active_tier = st.selectbox("Select NAGI V Core", list(MODEL_MAP.keys()))
        
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    # CHAT INTERFACE
    db = get_db()
    # Limit to 15 messages so the UI doesn't get slow over time
    chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 15", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in chat_data:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Command NAGI V..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        # Log user message
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_tier, user_prompt, datetime.now()))
        
        # Generate NAGI V Response
        resp = nagi_v_engine(active_tier, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        
        # Log assistant message
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_tier, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
