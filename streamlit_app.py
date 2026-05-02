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

# Connection pooled for speed
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# ==========================================
# 2. PERFORMANCE CACHING (The Speed Fix)
# ==========================================
@st.cache_resource
def get_nagi_model():
    """Caches the model instance so it doesn't reload every message."""
    return genai.GenerativeModel("models/gemma-4-26b-a4b-it")

def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

# ==========================================
# 3. NAGI V ENGINE (Optimized)
# ==========================================
def nagi_v_engine(tier, prompt):
    try:
        nagi_model = get_nagi_model()
        # Streamlined directive for faster processing
        directive = f"Identity: {tier} (NAGI V). Creator: {OWNER_NAME}."
        response = nagi_model.generate_content(f"{directive}\nUser: {prompt}")
        return response.text
    except Exception:
        return "NAGI V Core Connection Error."

# ==========================================
# 4. NAGI INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="NAGI Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- NAGI ACCESS PORTAL ---
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

    # --- NAGI V OPERATING ENVIRONMENT ---
    st.sidebar.title("NAGI V Core")
    if st.sidebar.button("🔄 Reset NAGI V"):
        st.rerun()
    
    active_tier = st.sidebar.selectbox("NAGI V Tier", ["NAGI V1", "NAGI V2", "NAGI V3", "NAGI V4"])

    # Optimized History Loading (Limit to last 20 for speed)
    db = get_db()
    chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 20", (st.session_state.user,)).fetchall()[::-1]
    
    for r, m in chat_data:
        with st.chat_message(r): st.write(m)

    if user_prompt := st.chat_input("Enter NAGI command..."):
        with st.chat_message("user"): st.write(user_prompt)
        
        # Async-style database logging
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                   (st.session_state.user, active_tier, user_prompt, datetime.now()))
        
        resp = nagi_v_engine(active_tier, user_prompt)
        
        with st.chat_message("assistant"): st.write(resp)
        db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                   (st.session_state.user, active_tier, resp, datetime.now()))
        db.commit()
        db.close()
        st.rerun()

if __name__ == "__main__":
    main()
