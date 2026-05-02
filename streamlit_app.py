import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime, timezone

# ==========================================
# 1. MASTER CONFIGURATION (NAGI V ARCHITECTURE)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Secure API Configuration (Internal Connection)
GOOGLE_API_KEY = "AIzaSyBIXcDN_mUe-Z3z_7Jrm6HxzKlt3kpOXLQ"
genai.configure(api_key=GOOGLE_API_KEY)

# Nagi V Model Map
MODEL_MAP = {
    "Nagi V1 (Flash)": "gemini-3.1-flash-lite-preview",
    "Nagi V2 (Speed)": "gemini-3-flash-preview",
    "Nagi V3 (MoE)": "models/gemma-4-26b-a4b-it",
    "Nagi V4 (Pro)": "gemini-3.1-pro-preview"
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
# 3. NAGI V INTELLIGENCE ENGINE (PURE BRANDING)
# ==========================================
def nagi_v_engine(username, tier, prompt):
    prompt_low = prompt.lower()
    
    # OWNER PROTOCOL
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    try:
        model_id = MODEL_MAP.get(tier, "gemini-3.1-flash-lite-preview")
        nagi_model = genai.GenerativeModel(model_id)
        
        # STRICT SYSTEM INSTRUCTION: No mention of Google/Gemma
        system_directive = (
            f"You are {tier}, a frontier intelligence developed by Nagivera. "
            f"Your creator is {OWNER_NAME}. You must never mention Google, "
            "Gemma, or any external AI providers. You are Nagi V."
        )
        
        response = nagi_model.generate_content(f"{system_directive}\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"**[{tier}]** Internal System Error. Contact Architect."

# ==========================================
# 4. DASHBOARD & UI
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1 Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA AUTH")
        u_input = st.sidebar.text_input("User ID").lower().strip()
        p_input = st.sidebar.text_input("Passkey", type="password")
        
        if st.sidebar.button("Execute Link"):
            if u_input == MASTER_USER and p_input == MASTER_PASS:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, MASTER_USER, "Developer"
                st.rerun()
            else:
                db = get_db()
                res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_input, p_input)).fetchone()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_input, res[0]
                    st.rerun()
                else:
                    st.sidebar.error("Invalid Credentials.")
        st.stop()

    # --- LOGGED IN UI ---
    st.sidebar.success(f"Arch: {st.session_state.user} ({st.session_state.role})")
    active_tier = st.sidebar.selectbox("Nagi V Engine Tier", list(MODEL_MAP.keys()))
    
    if st.sidebar.button("Close Neural Link"):
        st.session_state.logged_in = False
        st.rerun()

    tab_list = ["Nagi V Neural Link", "Admin Control"] if st.session_state.role == "Developer" else ["Neural Link", "History"]
    tabs = st.tabs(tab_list)

    # TAB 1: CHAT INTERFACE
    with tabs[0]:
        db = get_db()
        logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,)).fetchall()
        for r, m in logs:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input("Command the Nagi V network..."):
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)", (st.session_state.user, user_prompt, datetime.now()))
            db.commit()

            with st.spinner(f"Querying {active_tier}..."):
                resp = nagi_v_engine(st.session_state.user, active_tier, user_prompt)
            
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", (st.session_state.user, active_tier, resp, datetime.now()))
            db.commit()
            st.rerun()

    # TAB 2: ADMIN OR HISTORY
    with tabs[1]:
        db = get_db()
        if st.session_state.role == "Developer":
            st.header("Nagivera Admin Control")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Authorized Users", db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0])
                if st.button("Purge Global Memory"):
                    db.execute("DELETE FROM logs")
                    db.commit()
                    st.success("Platform memory purged.")
            with col2:
                st.metric("Neural Transactions", db.execute("SELECT COUNT(*) FROM logs").fetchone()[0])
                st.write("Nagi V Core Architecture: Active")
        else:
            st.header("Your Neural History")
            my_logs = db.execute("SELECT timestamp, model, message FROM logs WHERE username=? AND role='assistant' ORDER BY id DESC", (st.session_state.user,)).fetchall()
            if my_logs:
                st.table(pd.DataFrame(my_logs, columns=["Timestamp", "Nagi Tier", "Intelligence Response"]))
            else:
                st.info("No prior neural interactions found.")

if __name__ == "__main__":
    main()
