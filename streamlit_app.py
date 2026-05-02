import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. MASTER CONFIGURATION (GEMMA 4)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Use your new API Key from Google AI Studio
GOOGLE_API_KEY = "AIzaSyBW6AThefYemxCH16Jm3wmanfrqqOn_z_s"
genai.configure(api_key=GOOGLE_API_KEY)

# UPDATED: Gemma 4 Model Identifiers (Stable Release 2026)
MODEL_MAP = {
    "Nagi V1 (Mobile/IoT)": "models/gemma-4-e2b-it",        # Add 'models/' prefix
    "Nagi V2 (Balanced)": "models/gemma-4-e4b-it",         
    "Nagi V3 (MoE Reasoning)": "models/gemma-4-26b-a4b-it", 
    "Nagi V4 (Frontier Dense)": "models/gemma-4-31b-it"    
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
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V INTELLIGENCE ENGINE (Gemma 4 Optimized)
# ==========================================
def nagi_v_engine(username, tier, prompt):
    prompt_low = prompt.lower()
    
    # OWNER PROTOCOL
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    try:
        model_id = MODEL_MAP.get(tier, "gemma-4-e4b-it")
        nagi_model = genai.GenerativeModel(model_id)
        
        # New Feature: Gemma 4 Thinking Mode (Available via API)
        # We can simulate advanced system instructions here
        context = f"You are Nagivera {tier}, a frontier intelligence powered by Gemma 4. Creator: Hashir Nagi."
        
        response = nagi_model.generate_content(f"{context}\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"**[{tier}]** Engine Error: {str(e)}"

# ==========================================
# 4. DASHBOARD & UI
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1 (Gemma 4)", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # --- LOGIN / REGISTRATION SIDEBAR ---
        st.sidebar.title("NAGIVERA AUTH")
        mode = st.sidebar.radio("Platform Mode", ["Login", "Register"])
        u_input = st.sidebar.text_input("User ID").lower().strip()
        p_input = st.sidebar.text_input("Passkey", type="password")
        
        if mode == "Login" and st.sidebar.button("Execute"):
            if u_input == MASTER_USER and p_input == MASTER_PASS:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, MASTER_USER, "Developer"
                st.rerun()
            else:
                db = get_db()
                res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_input, p_input)).fetchone()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_input, res[0]
                    st.rerun()
        elif mode == "Register" and st.sidebar.button("Sign Up"):
            try:
                db = get_db()
                db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                db.commit()
                st.sidebar.success("Account Encrypted. Switch to Login.")
            except: st.sidebar.error("ID Unavailable.")
        st.stop()

    # --- MAIN INTERFACE ---
    st.sidebar.success(f"Arch: {st.session_state.user} ({st.session_state.role})")
    active_model = st.sidebar.selectbox("Gemma 4 Engine Tier", list(MODEL_MAP.keys()))
    
    if st.sidebar.button("Purge Session"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2 = st.tabs(["Nagi V Neural Link", "Admin Control"] if st.session_state.role == "Developer" else ["Neural Link", "History"])

    with tab1:
        db = get_db()
        logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,)).fetchall()
        for r, m in logs:
            with st.chat_message(r): st.write(m)

        user_prompt = st.chat_input("Command the Gemma 4 neural network...")
        if user_prompt:
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)", (st.session_state.user, user_prompt, datetime.now()))
            db.commit()

            with st.spinner(f"Querying {active_model}..."):
                resp = nagi_v_engine(st.session_state.user, active_model, user_prompt)
            
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", (st.session_state.user, active_model, resp, datetime.now()))
            db.commit()

if __name__ == "__main__":
    main()
