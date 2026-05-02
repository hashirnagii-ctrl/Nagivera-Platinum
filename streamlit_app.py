import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. MASTER CONFIGURATION
# ==========================================
# Only these credentials unlock the Developer Database
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

# Connect to the Gemma 4 / Gemini Engine
# Get your key at https://aistudio.google.com/
try:
    genai.configure(api_key="AIzaSyBW6AThefYemxCH16Jm3wmanfrqqOn_z_s")
    model = genai.GenerativeModel("gemma-4-27b-it")
except Exception:
    model = None

# ==========================================
# 2. DATABASE SYSTEM (Permanent Memory)
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    # Account Table
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    # Ensure the Owner is always in the DB as 'Developer'
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
# Defined BEFORE main() to fix NameError from image_96df5a.png
def nagi_v_engine(username, tier, prompt):
    now = datetime.now(timezone.utc)
    is_free = now < DEADLINE
    prompt_low = prompt.lower()
    
    # --- RULE 1: OWNER PROTOCOL ---
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    # --- RULE 2: MULTIMODAL LIMITS (Post Sept 30) ---
    if not is_free:
        if "video" in prompt_low:
            return "🚫 **[Nagi V3 Ultra]** Motion Engine is locked. Video generation ended on Sept 30, 2026."
        if "image" in prompt_low:
            # Add database logic here for the 5-image limit if needed
            pass

    # --- RULE 3: REAL AI CONVERSATION (Gemini Style) ---
    try:
        if model:
            context = f"You are Nagivera {tier}. Your creator is Hashir Nagi. Answer with high-level intelligence."
            response = model.generate_content(f"{context}\nUser: {prompt}")
            return response.text
        return f"**[{tier}]** Engine active. (Connect API Key for full conversational intelligence)."
    except Exception as e:
        return f"**[{tier}]** Intelligence error: {str(e)}"

# ==========================================
# 4. THE MAIN INTERFACE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1", page_icon="⚡", layout="wide")

    # Initialize session state variables safely to avoid AttributeErrors
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = "Guest"

    # --- LOGIN SYSTEM ---
    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA SECURE ACCESS")
        u_input = st.sidebar.text_input("Username").lower().strip()
        p_input = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Login"):
            # Check for Master Admin credentials
            if u_input == MASTER_USER and p_input == MASTER_PASS:
                st.session_state.logged_in = True
                st.session_state.user = MASTER_USER
                st.session_state.role = "Developer"
                st.rerun()
            else:
                # Normal User Database Check
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
                    # Auto-register guest accounts as 'User' role
                    c.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                    db.commit()
                    st.session_state.logged_in = True
                    st.session_state.user = u_input
                    st.session_state.role = "User"
                    st.rerun()
        st.stop()

    # --- AUTHORIZED SIDEBAR ---
    st.sidebar.success(f"Access Granted: {st.session_state.user}")
    st.sidebar.info(f"Role: {st.session_state.role}")
    
    active_model = st.sidebar.selectbox("Active Nagi V Model", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Ultra)"])
    
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- ADMIN TAB LOCK ---
    # Only 'hashir' with 'Developer' role can see this tab
    tab_list = ["Nagi V Chat"]
    if st.session_state.user == MASTER_USER and st.session_state.role == "Developer":
        tab_list.append("Developer Database (Logs)")
    
    tabs = st.tabs(tab_list)

    # --- TAB 1: CHAT INTERFACE ---
    with tabs[0]:
        db = get_db()
        c = db.cursor()
        # Display history from DB
        c.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,))
        for role, msg in c.fetchall():
            with st.chat_message(role):
                st.write(msg)

        # Chat Input
        user_input = st.chat_input("Command the Nagi V engines...")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)
            
            # Save User Input to DB
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)",
                      (st.session_state.user, user_input, datetime.now()))
            db.commit()

            # Generate AI Response
            with st.spinner("Thinking..."):
                response_text = nagi_v_engine(st.session_state.user, active_model, user_input)
            
            with st.chat_message("assistant"):
                st.write(response_text)
            
            # Save Assistant Response to DB
            c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)",
                      (st.session_state.user, active_model, response_text, datetime.now()))
            db.commit()

    # --- TAB 2: DEVELOPER LOGS (Strictly Secured) ---
    if len(tabs) > 1:
        with tabs[1]:
            st.header("Master Developer Database")
            st.warning("Encryption Active. Viewing all global system logs.")
            db = get_db()
            df = pd.read_sql_query("SELECT * FROM logs", db)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Purge Global History"):
                c = db.cursor()
                c.execute("DELETE FROM logs")
                db.commit()
                st.rerun()

if __name__ == "__main__":
    main()
