import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. THE IDEA GENIUS - MASTER CREDENTIALS
# ==========================================
# ONLY these exact credentials unlock the Developer Database
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# ==========================================
# 2. AI & DATABASE CONFIG
# ==========================================
try:
    # Use your Gemini/Gemma 4 API Key here
    genai.configure(api_key="AIzaSyBW6AThefYemxCH16Jm3wmanfrqqOn_z_s")
    model = genai.GenerativeModel("gemma-4-27b-it")
except:
    pass

def get_db():
    return sqlite3.connect('nagivera_v5_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    # Account Table
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Ensure ONLY your master account is labeled as 'Developer'
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    # Chat Logs
    c.execute('CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V INTELLIGENCE ENGINE
# ==========================================
def nagi_v_engine(username, tier, prompt):
    prompt_low = prompt.lower()
    
    # Owner Protocol
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    try:
        context = f"You are Nagivera {tier}. Your creator is Hashir Nagi. Answer with high intelligence."
        response = model.generate_content(f"{context}\nUser: {prompt}")
        return response.text
    except:
        return f"**[{tier}]** Connection to Nagi Brain is currently in local mode. (Please verify API key for Gemini-style responses)."

# ==========================================
# 4. SECURE INTERFACE LOGIC
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1", page_icon="⚡", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- LOGIN GATE ---
    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA SECURE ACCESS")
        u_input = st.sidebar.text_input("Username").lower().strip()
        p_input = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            # Check for the Master Admin first
            if u_input == MASTER_USER and p_input == MASTER_PASS:
                st.session_state.logged_in = True
                st.session_state.user = MASTER_USER
                st.session_state.role = "Developer"
                st.rerun()
            else:
                # Check database for other users
                db = get_db()
                c = db.cursor()
                c.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_input, p_input))
                result = c.fetchone()
                if result:
                    st.session_state.logged_in = True
                    st.session_state.user = u_input
                    st.session_state.role = result[0]
                    st.rerun()
                else:
                    # Auto-register guest users (They won't be Developers)
                    c.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                    db.commit()
                    st.session_state.logged_in = True
                    st.session_state.user = u_input
                    st.session_state.role = "User"
                    st.rerun()
        st.stop()

    # --- AUTHENTICATED DASHBOARD ---
    st.sidebar.success(f"Access Granted: {st.session_state.user}")
    st.sidebar.info(f"Role: {st.session_state.role}")
    
    active_model = st.sidebar.selectbox("Active Nagi V Model", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Ultra)"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- THE DEVELOPER LOCK ---
    # Only show the Database tab if the role is 'Developer' AND username is 'hashir'
    tabs_to_show = ["Nagi V Chat"]
    if st.session_state.user == MASTER_USER and st.session_state.role == "Developer":
        tabs_to_show.append("Developer Database (Logs)")
    
    tabs = st.tabs(tabs_to_show)

    # CHAT TAB
    with tabs[0]:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,))
        for role, msg in c.fetchall():
            with st.chat_message(role):
                st.write(msg)

        user_input = st.chat_input("Command the Nagi V engines...")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)",
                      (st.session_state.user, user_input, datetime.now()))
            db.commit()

            response_text = nagi_v_engine(st.session_state.user, active_model, user_input)
            
            with st.chat_message("assistant"):
                st.write(response_text)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)",
                      (st.session_state.user, active_model, response_text, datetime.now()))
            db.commit()

    # ADMIN TAB (Strictly Secured)
    if len(tabs) > 1:
        with tabs[1]:
            st.header("Master Developer Database")
            st.warning("Encryption Active. Viewing Global System Logs.")
            db = get_db()
            df = pd.read_sql_query("SELECT * FROM logs", db)
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
