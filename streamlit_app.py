import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. MASTER CONFIGURATION & SECURITY
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" # Case-sensitive
OWNER_NAME = "Hashir Nagi"
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

# API Configuration - Update with your real key
GOOGLE_API_KEY = "AIzaSyDoji3yAGbR3B53Rh4EcklNPfVVfy1lpT0"
genai.configure(api_key=GOOGLE_API_KEY)

# Map Nagi tiers to valid Google AI models
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
    now = datetime.now(timezone.utc)
    is_free_period = now < DEADLINE
    prompt_low = prompt.lower()
    
    # --- RULE 1: OWNER PROTOCOL ---
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    # --- RULE 2: SERVICE RESTRICTIONS ---
    if not is_free_period and "video" in prompt_low:
        return "🚫 **[Nagi V3 Ultra]** Motion Engine is locked. Video generation phase ended on September 30, 2026."

    # --- RULE 3: CORE AI LOGIC ---
    try:
        model_name = MODEL_MAP.get(tier, "gemini-1.5-flash")
        nagi_model = genai.GenerativeModel(model_name)
        
        context = f"You are Nagivera {tier}. Your creator is Hashir Nagi. Answer with high-level intelligence."
        
        if not prompt:
            return "Engine standing by."
            
        response = nagi_model.generate_content(f"{context}\nUser: {prompt}")
        return response.text

    except Exception as e:
        return f"**[{tier}]** Intelligence error: {str(e)}"

# ==========================================
# 4. MAIN INTERFACE LOGIC
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1", page_icon="⚡", layout="wide")

    # Initialize Session State
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = "Guest"

    # --- SECURE LOGIN GATE ---
    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA SECURE ACCESS")
        u_input = st.sidebar.text_input("Username").lower().strip()
        p_input = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
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
                elif u_input == MASTER_USER:
                    st.sidebar.error("Access Denied: Incorrect Password for Master Account.")
                else:
                    try:
                        c.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                        db.commit()
                        st.session_state.logged_in = True
                        st.session_state.user = u_input
                        st.session_state.role = "User"
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.sidebar.error("Login failed. Check your password.")
        st.stop()

    # --- AUTHORIZED DASHBOARD ---
    st.sidebar.success(f"Access Granted: {st.session_state.user}")
    st.sidebar.info(f"Role: {st.session_state.role}")
    
    active_model = st.sidebar.selectbox("Active Nagi V Model", list(MODEL_MAP.keys()))
    
    if st.sidebar.button("Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- NAVIGATION TABS ---
    tab_titles = ["Nagi V Chat"]
    if st.session_state.role == "Developer":
        tab_titles.append("Developer Database (Logs)")
    
    tabs = st.tabs(tab_titles)

    # TAB 1: CHAT SYSTEM
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

            with st.spinner(f"{active_model} processing..."):
                response = nagi_v_engine(st.session_state.user, active_model, user_prompt)
            
            with st.chat_message("assistant"):
                st.write(response)
            
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)",
                      (st.session_state.user, active_model, response, datetime.now()))
            db.commit()

    # TAB 2: SYSTEM LOGS (Developer Only)
    if len(tabs) > 1:
        with tabs[1]:
            st.header("Master Control Center")
            db = get_db()
            df = pd.read_sql_query("SELECT * FROM logs", db)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Clear Global History"):
                c = db.cursor()
                c.execute("DELETE FROM logs")
                db.commit()
                st.rerun()

if __name__ == "__main__":
    main()
