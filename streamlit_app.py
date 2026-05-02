import streamlit as st
import sqlite3
from datetime import datetime, timezone
import time

# ==========================================
# 1. CORE PLATFORM CONFIGURATION
# ==========================================
# The ironclad deadline for the "Early Bird" period
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
OWNER_NAME = "Hashir Nagi"
PLATFORM_NAME = "Nagivera v4.1"

# ==========================================
# 2. THE DEVELOPER DATABASE (Persistent)
# ==========================================
def get_db():
    # This creates a real database file on your system
    conn = sqlite3.connect('nagivera_developer.db', check_same_thread=False)
    return conn

def init_db():
    db = get_db()
    cursor = db.cursor()
    # Table for all accounts (Developer + Users)
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts 
                     (username TEXT PRIMARY KEY, password TEXT, role TEXT, image_limit INTEGER DEFAULT 5)''')
    # Table for every single chat ever sent (The Developer's Log)
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_logs 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. THE NAGI V MULTIMODAL ENGINE
# ==========================================
def nagi_v_engine(username, tier, prompt):
    """
    All AI logic is now funneled through the 'Nagi V' brand.
    """
    now = datetime.now(timezone.utc)
    is_free = now < DEADLINE
    prompt_low = prompt.lower()

    # OWNER PROTOCOL: Identify the Idea Genius
    if "owner" in prompt_low or "who made you" in prompt_low:
        return f"I am a Nagi V Series model. My architect and owner is the Idea Genius, **{OWNER_NAME}**."

    # Tier-based Response Logic
    if tier == "Nagi V1 (Lite)":
        response = f"**[Nagi V1 Lite]** Logic active. Processed: '{prompt}'"
    elif tier == "Nagi V2 (Pro)":
        if not is_free:
            # Add logic here to check the 5-image limit from the database
            response = "**[Nagi V2 Pro]** Restricted Mode: Image generation limit check active."
        else:
            response = f"**[Nagi V2 Pro]** Unlimited Mode: Rendering high-detail visual for '{prompt}'."
    elif tier == "Nagi V3 (Ultra)":
        if not is_free:
            response = "🚫 **[Nagi V3 Ultra]** Motion Engine locked. Past Sept 30, 2026."
        else:
            response = f"**[Nagi V3 Ultra]** Cinematic Motion Engine rendering unlimited video for '{prompt}'."
    else:
        response = "Engine Error: Tier not recognized."

    # SAVE TO DEVELOPER DATABASE
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO chat_logs (username, role, model, message, timestamp) VALUES (?, ?, ?, ?, ?)",
              (username, 'assistant', tier, response, datetime.now()))
    db.commit()
    db.close()
    
    return response

# ==========================================
# 4. DEVELOPER INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title=PLATFORM_NAME, page_icon="⚡", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- SIDEBAR: SECURE LOGIN & DB STATUS ---
    st.sidebar.title("NAGIVERA SECURE ACCESS")
    
    if not st.session_state.logged_in:
        user = st.sidebar.text_input("Username")
        pw = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login to Nagivera"):
            db = get_db()
            c = db.cursor()
            c.execute("SELECT * FROM accounts WHERE username=? AND password=?", (user, pw))
            account = c.fetchone()
            if account:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
            else:
                # Auto-create first developer account
                c.execute("INSERT INTO accounts (username, password, role) VALUES (?, ?, 'Developer')", (user, pw))
                db.commit()
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()
        st.stop()

    # --- MAIN DASHBOARD (LOGGED IN) ---
    st.sidebar.success(f"Logged in: {st.session_state.user}")
    active_tier = st.sidebar.selectbox("Active Nagi V Model", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Ultra)"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"⚡ {PLATFORM_NAME} Dashboard")
    
    # NAVIGATION
    tab_chat, tab_logs = st.tabs(["Nagi V Chat", "Developer Database (Logs)"])

    # --- TAB: CHAT INTERFACE ---
    with tab_chat:
        # Load chat history from DB
        db = get_db()
        c = db.cursor()
        c.execute("SELECT role, message FROM chat_logs WHERE username=? ORDER BY id ASC", (st.session_state.user,))
        history = c.fetchall()
        
        for role, msg in history:
            with st.chat_message(role):
                st.write(msg)

        # Input
        user_input = st.chat_input("Command the Nagi V engines...")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            
            # Save User message
            c.execute("INSERT INTO chat_logs (username, role, model, message, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (st.session_state.user, 'user', 'User', user_input, datetime.now()))
            db.commit()

            # Generate and Save AI Response
            response = nagi_v_engine(st.session_state.user, active_tier, user_input)
            with st.chat_message("assistant"):
                st.write(response)

    # --- TAB: DEVELOPER LOGS ---
    with tab_logs:
        st.header("Global Platform Logs")
        st.write("This is the raw database for the developer to monitor activity.")
        db = get_db()
        # Fetch all logs from all users
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM chat_logs", db)
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
