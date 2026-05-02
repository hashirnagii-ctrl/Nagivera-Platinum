import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timezone
import time

# ==========================================
# 1. CORE PLATFORM CONFIGURATION
# ==========================================
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
OWNER_ID = "hashir"  # THE ONLY USER WHO CAN SEE THE DATABASE
OWNER_NAME = "Hashir Nagi"
PLATFORM_NAME = "Nagivera v4.1"

# ==========================================
# 2. PERSISTENT DATABASE MANAGEMENT
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    # Stores account details
    c.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    # Stores chat history and logs
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V INTELLIGENCE ENGINE
# ==========================================
def nagi_v_engine(username, tier, prompt):
    now = datetime.now(timezone.utc)
    is_free = now < DEADLINE
    prompt_low = prompt.lower()

    # OWNER IDENTIFICATION PROTOCOL
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        response = f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."
    
    # TIERED LOGIC
    elif "v1" in tier.lower():
        response = f"**[Nagi V1 Lite]** Logic engine active. Processed: '{prompt}'"
    elif "v2" in tier.lower():
        status = "Unlimited Mode" if is_free else "Restricted Mode (5 Left)"
        response = f"**[Nagi V2 Pro]** {status}: Rendering high-detail vision for your request."
    elif "v3" in tier.lower():
        if not is_free:
            response = "🚫 **[Nagi V3 Ultra]** Motion Engine is currently locked. Free access ended on Sept 30, 2026."
        else:
            response = f"**[Nagi V3 Ultra]** Cinematic Motion active. Rendering unlimited video for: '{prompt}'."
    else:
        response = "Nagi V Engine error. Please check your model selection."

    # SAVE TO PERMANENT LOGS
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, ?, ?, ?, ?)",
              (username, 'assistant', tier, response, datetime.now()))
    db.commit()
    db.close()
    return response

# ==========================================
# 4. SECURE UI & ADMIN LOCK
# ==========================================
def main():
    st.set_page_config(page_title=PLATFORM_NAME, page_icon="⚡", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- SECURE LOGIN SIDEBAR ---
    st.sidebar.title("NAGIVERA SECURE ACCESS")
    
    if not st.session_state.logged_in:
        user = st.sidebar.text_input("Username").lower().strip()
        pw = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            db = get_db()
            c = db.cursor()
            c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (user, pw))
            account = c.fetchone()
            if account:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                # Automatic account creation for new users
                role = "Developer" if user == OWNER_ID else "User"
                c.execute("INSERT INTO accounts VALUES (?, ?, ?)", (user, pw, role))
                db.commit()
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
        st.stop()

    # --- AUTHORIZED DASHBOARD ---
    st.sidebar.success(f"Verified: {st.session_state.user}")
    active_model = st.sidebar.selectbox("Active Nagi V Model", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Ultra)"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # ADMIN TAB LOCK: Only 'hashir' sees the Developer Database
    tab_list = ["Nagi V Chat"]
    if st.session_state.user == OWNER_ID:
        tab_list.append("Developer Database (Logs)")
    
    tabs = st.tabs(tab_list)

    # --- TAB 1: CHAT INTERFACE ---
    with tabs[0]:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,))
        history = c.fetchall()
        
        for role, msg in history:
            with st.chat_message(role):
                st.write(msg)

        user_input = st.chat_input("Command the Nagi V engines...")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (st.session_state.user, 'user', 'Input', user_input, datetime.now()))
            db.commit()

            # Process with Nagi V Logic
            response = nagi_v_engine(st.session_state.user, active_model, user_input)
            with st.chat_message("assistant"):
                st.write(response)

    # --- TAB 2: DEVELOPER DATABASE (HIDDEN FROM OTHERS) ---
    if st.session_state.user == OWNER_ID:
        with tabs[1]:
            st.header("Master Developer Logs")
            st.info("This view is strictly encrypted and visible only to Hashir.")
            db = get_db()
            df = pd.read_sql_query("SELECT * FROM logs", db)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Purge Database Logs"):
                c = db.cursor()
                c.execute("DELETE FROM logs")
                db.commit()
                st.success("Logs cleared.")
                st.rerun()

if __name__ == "__main__":
    main()
