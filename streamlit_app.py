import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. MASTER CONFIGURATION & SECURITY
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

# API Configuration
GOOGLE_API_KEY = "AIzaSyDoji3yAGbR3B53Rh4EckLNPfVVfy1lpT0"
genai.configure(api_key=GOOGLE_API_KEY)

MODEL_MAP = {
    "Nagi V1 (Lite)": "gemini-1.5-flash",
    "Nagi V2 (Pro)": "gemini-1.5-flash",
    "Nagi V3 (Ultra)": "gemini-1.5-pro"
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
    # Ensure Developer account is always there
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V INTELLIGENCE ENGINE
# ==========================================
def nagi_v_engine(username, tier, prompt):
    prompt_low = prompt.lower()
    
    # OWNER PROTOCOL
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    try:
        model_name = MODEL_MAP.get(tier, "gemini-1.5-flash")
        nagi_model = genai.GenerativeModel(model_name)
        context = f"You are Nagivera {tier}. Your creator is Hashir Nagi. Answer with high-level intelligence."
        response = nagi_model.generate_content(f"{context}\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"**[{tier}]** Intelligence error: {str(e)}"

# ==========================================
# 4. MAIN INTERFACE LOGIC
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1", page_icon="⚡", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = "Guest"

    # --- SECURE LOGIN & REGISTRATION GATE ---
    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA SECURE ACCESS")
        
        # Toggle between Login and Register
        auth_mode = st.sidebar.radio("Choose Action", ["Login", "Register"])
        
        u_input = st.sidebar.text_input("Username").lower().strip()
        p_input = st.sidebar.text_input("Password", type="password")
        
        if auth_mode == "Login":
            if st.sidebar.button("Login"):
                # Master Check
                if u_input == MASTER_USER and p_input == MASTER_PASS:
                    st.session_state.logged_in = True
                    st.session_state.user = MASTER_USER
                    st.session_state.role = "Developer"
                    st.rerun()
                else:
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
                        st.sidebar.error("Invalid credentials.")
        
        else: # Register Mode
            if st.sidebar.button("Create Account"):
                if u_input == MASTER_USER:
                    st.sidebar.error("This username is reserved.")
                elif len(u_input) < 3 or len(p_input) < 4:
                    st.sidebar.warning("Username/Password too short.")
                else:
                    try:
                        db = get_db()
                        c = db.cursor()
                        c.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                        db.commit()
                        st.sidebar.success("Account created! Please switch to Login.")
                    except sqlite3.IntegrityError:
                        st.sidebar.error("Username already exists.")
        st.stop()

    # --- AUTHORIZED DASHBOARD ---
    st.sidebar.success(f"Access Granted: {st.session_state.user}")
    st.sidebar.info(f"Role: {st.session_state.role}")
    
    active_model = st.sidebar.selectbox("Active Nagi V Model", list(MODEL_MAP.keys()))
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- NAVIGATION TABS ---
    tab_titles = ["Nagi V Chat"]
    if st.session_state.role == "Developer":
        tab_titles.append("Developer Database (Logs)")
    
    tabs = st.tabs(tab_titles)

    with tabs[0]:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,))
        for role, msg in c.fetchall():
            with st.chat_message(role):
                st.write(msg)

        user_prompt = st.chat_input("Command the Nagi V engines...")
        if user_prompt:
            with st.chat_message("user"):
                st.write(user_prompt)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)",
                      (st.session_state.user, user_prompt, datetime.now()))
            db.commit()

            with st.spinner("Processing..."):
                response = nagi_v_engine(st.session_state.user, active_model, user_prompt)
            
            with st.chat_message("assistant"):
                st.write(response)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)",
                      (st.session_state.user, active_model, response, datetime.now()))
            db.commit()

    if len(tabs) > 1:
        with tabs[1]:
            st.header("Master Control Center")
            db = get_db()
            df = pd.read_sql_query("SELECT * FROM logs", db)
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
