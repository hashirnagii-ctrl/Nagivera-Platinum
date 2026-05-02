import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. OWNER & PLATFORM CONFIGURATION
# ==========================================
OWNER_ID = "hashir"
OWNER_PASS = "Hashirnagi2011"  # Your specific secure password
OWNER_NAME = "Hashir Nagi"
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

# Connect to the real Gemma 4 Intelligence Engine
# Replace with your actual key from https://aistudio.google.com/
try:
    genai.configure(api_key="YOUR_GOOGLE_API_KEY_HERE")
    model = genai.GenerativeModel("gemma-4-27b-it")
except Exception:
    pass

# ==========================================
# 2. PERSISTENT DATABASE ENGINE
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    # Ensure the owner account exists in the database
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('INSERT OR IGNORE INTO accounts VALUES (?, ?, ?)', (OWNER_ID, OWNER_PASS, "Developer"))
    # Global logs table
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. THE NAGI V INTELLIGENCE LOGIC
# ==========================================
def nagi_v_engine(username, tier, prompt):
    prompt_low = prompt.lower()
    
    # OWNER PROTOCOL: Instant Recognition
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    # REAL AI CONVERSATION (Gemma 4 Integration)
    try:
        context = f"You are Nagivera {tier}. Your creator is Hashir Nagi. Answer like a highly advanced AI."
        response = model.generate_content(f"{context}\nUser: {prompt}")
        return response.text
    except Exception:
        # Fallback if API is offline
        return f"**[{tier}]** I am currently processing your request: '{prompt}'. (Connect API for full Gemini-style responses)."

# ==========================================
# 4. MASTER INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1", page_icon="⚡", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- SECURE LOGIN ---
    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA SECURE LOGIN")
        u = st.sidebar.text_input("Username").lower().strip()
        p = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            db = get_db()
            c = db.cursor()
            c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (u, p))
            account = c.fetchone()
            if account:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                # Allow others to register as standard users
                c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, ?)", (u, p, "User"))
                db.commit()
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
        st.stop()

    # --- AUTHORIZED DASHBOARD ---
    st.sidebar.success(f"Verified: {st.session_state.user}")
    active_model = st.sidebar.selectbox("Active Nagi V Model", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Ultra)"])
    
    # TAB LOCK: Only 'hashir' sees the Developer Database
    tabs_to_show = ["Nagi V Chat"]
    if st.session_state.user == OWNER_ID:
        tabs_to_show.append("Developer Database (Logs)")
    
    tabs = st.tabs(tabs_to_show)

    # CHAT TAB
    with tabs[0]:
        db = get_db()
        c = db.cursor()
        # Display chat history from database
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

            # Generate AI Response
            response_text = nagi_v_engine(st.session_state.user, active_model, user_input)
            
            with st.chat_message("assistant"):
                st.write(response_text)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)",
                      (st.session_state.user, active_model, response_text, datetime.now()))
            db.commit()

    # ADMIN LOGS (Strictly for Hashir)
    if st.session_state.user == OWNER_ID:
        with tabs[1]:
            st.header("Master Developer Database")
            st.info("Strictly confidential logs for Hashir Nagi.")
            db = get_db()
            df = pd.read_sql_query("SELECT * FROM logs", db)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Purge Global Logs"):
                c = db.cursor()
                c.execute("DELETE FROM logs")
                db.commit()
                st.rerun()

if __name__ == "__main__":
    main()
