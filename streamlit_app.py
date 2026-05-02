import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. MASTER CONFIGURATION & SECURITY
# ==========================================
# Credentials for the Idea Genius
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011"  # Note: This is case-sensitive (Capital H)
OWNER_NAME = "Hashir Nagi"
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

# API Configuration
try:
    # Replace with your actual Gemini API Key
    genai.configure(api_key="AIzaSyBW6AThefYemxCH16Jm3wmanfrqqOn_z_s")
    model = genai.GenerativeModel("gemma-4-27b-it")
except Exception:
    model = None

# ==========================================
# 2. DATABASE SYSTEM
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    # Account Table: username is PRIMARY KEY to ensure uniqueness
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Ensure the Developer account exists
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    # Chat Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V INTELLIGENCE ENGINE
# ==========================================
# DEFINED BEFORE main() to prevent NameError
def nagi_v_engine(username, tier, prompt):
    now = datetime.now(timezone.utc)
    is_free_period = now < DEADLINE
    prompt_low = prompt.lower()
    
    # --- RULE 1: OWNER PROTOCOL ---
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    # --- RULE 2: SERVICE RESTRICTIONS (Post Sept 30) ---
    if not is_free_period:
        if "video" in prompt_low:
            return "🚫 **[Nagi V3 Ultra]** Motion Engine is locked. Video generation phase ended on September 30, 2026."

    # --- RULE 3: CORE AI LOGIC ---
    try:
        if model:
            context = f"You are Nagivera {tier}. Your creator is Hashir Nagi. Provide high-intelligence responses."
            response = model.generate_content(f"{context}\nUser: {prompt}")
            return response.text
        return f"**[{tier}]** Local processing active. (Connect API Key for full Nagi V Intelligence)."
    except Exception as e:
        return f"**[{tier}]** Intelligence error: {str(e)}"

# ==========================================
# 4. MAIN INTERFACE LOGIC
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1", page_icon="⚡", layout="wide")

    # --- SESSION STATE INITIALIZATION ---
    # Fixes AttributeError by ensuring these keys exist immediately
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
            # 1. Check for Master Developer (Developer Access)
            if u_input == MASTER_USER and p_input == MASTER_PASS:
                st.session_state.logged_in = True
                st.session_state.user = MASTER_USER
                st.session_state.role = "Developer"
                st.rerun()
            
            # 2. Check Database for existing standard users
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
                
                # 3. SAFETY GATE: Prevent IntegrityError if user 'hashir' uses wrong password
                elif u_input == MASTER_USER:
                    st.sidebar.error("Access Denied: Incorrect Password for Master Account.")
                
                # 4. Auto-register new Guest Users
                else:
                    try:
                        c.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                        db.commit()
                        st.session_state.logged_in = True
                        st.session_state.user = u_input
                        st.session_state.role = "User"
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.sidebar.error("Username taken. Please check your password or choose another name.")
        st.stop()

    # --- AUTHORIZED DASHBOARD ---
    st.sidebar.success(f"Access Granted: {st.session_state.user}")
    st.sidebar.info(f"Role: {st.session_state.role}")
    
    active_model = st.sidebar.selectbox("Active Nagi V Model", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Ultra)"])
    
    if st.sidebar.button("Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # --- NAVIGATION TABS ---
    # Only the Master Developer can see the database logs
    tab_titles = ["Nagi V Chat"]
    if st.session_state.user == MASTER_USER and st.session_state.role == "Developer":
        tab_titles.append("Developer Database (Logs)")
    
    tabs = st.tabs(tab_titles)

    # TAB 1: CHAT SYSTEM
    with tabs[0]:
        db = get_db()
        c = db.cursor()
        
        # Load chat history
        c.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,))
        for role, msg in c.fetchall():
            with st.chat_message(role):
                st.write(msg)

        # Chat Input logic
        user_prompt = st.chat_input("Command the Nagi V engines...")
        if user_prompt:
            with st.chat_message("user"):
                st.write(user_prompt)
            
            # Save user message
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)",
                      (st.session_state.user, user_prompt, datetime.now()))
            db.commit()

            # Process AI response
            with st.spinner("Nagi V Engine processing..."):
                response = nagi_v_engine(st.session_state.user, active_model, user_prompt)
            
            with st.chat_message("assistant"):
                st.write(response)
            
            # Save assistant message
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)",
                      (st.session_state.user, active_model, response, datetime.now()))
            db.commit()

    # TAB 2: SYSTEM LOGS (Developer Only)
    if "Developer Database (Logs)" in tab_titles:
        with tabs[1]:
            st.header("Master Control Center")
            st.info("Global system logs and database management.")
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
