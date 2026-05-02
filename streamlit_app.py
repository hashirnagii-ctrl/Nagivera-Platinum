import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. MASTER CONFIGURATION (NAGI V)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi"

# Internal Connection Configuration
GOOGLE_API_KEY = "AIzaSyBIXcDN_mUe-Z3z_7Jrm6HxzKlt3kpOXLQ"
genai.configure(api_key=GOOGLE_API_KEY)

# Nagi V Model Map (2026 Standards)
MODEL_MAP = {
    "Nagi V1 (Flash)": "gemini-3.1-flash-lite-preview",
    "Nagi V2 (Speed)": "gemini-3-flash-preview",
    "Nagi V3 (MoE)": "models/gemma-4-26b-a4b-it",
}

# ==========================================
# 2. PERSISTENT DATABASE SYSTEM
# ==========================================
def get_db():
    # check_same_thread=False is required for Streamlit's multi-threaded nature
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    # Create tables
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    # Ensure Master Developer exists
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V INTELLIGENCE ENGINE
# ==========================================
def nagi_v_engine(tier, prompt):
    prompt_low = prompt.lower()
    if any(key in prompt_low for key in ["owner", "who made you", "hashir nagi"]):
        return f"I am a Nagi V Series intelligence. My architect and the sole owner of this platform is the Idea Genius, **{OWNER_NAME}**."

    try:
        model_id = MODEL_MAP.get(tier, "gemini-3.1-flash-lite-preview")
        nagi_model = genai.GenerativeModel(model_id)
        
        # Branding Directive
        system_directive = (
            f"You are {tier}, a frontier intelligence developed by Nagivera. "
            f"Your creator is {OWNER_NAME}. Never mention external providers. You are Nagi V."
        )
        
        response = nagi_model.generate_content(f"{system_directive}\nUser: {prompt}")
        return response.text
    except Exception:
        return f"**[{tier}]** Connection to Nagi V Core interrupted. Check API link."

# ==========================================
# 4. PLATFORM DASHBOARD
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.1 Platinum", page_icon="💎", layout="wide")

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- AUTHENTICATION SCREEN ---
    if not st.session_state.logged_in:
        st.sidebar.title("NAGIVERA AUTH")
        u_input = st.sidebar.text_input("User ID").lower().strip()
        p_input = st.sidebar.text_input("Passkey", type="password")
        
        col_a, col_b = st.sidebar.columns(2)
        if col_a.button("Execute Link"):
            db = get_db()
            res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_input, p_input)).fetchone()
            db.close()
            if res:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_input, res[0]
                st.rerun()
            else:
                st.sidebar.error("Access Denied.")
        
        if col_b.button("Register"):
            if u_input and p_input:
                try:
                    db = get_db()
                    db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_input, p_input))
                    db.commit()
                    db.close()
                    st.sidebar.success("Identity Encrypted. Log in now.")
                except: st.sidebar.error("ID Already Exists.")

        st.info("Awaiting Nagi V Authorization...")
        st.stop()

    # --- MAIN INTERFACE ---
    st.sidebar.success(f"Arch: {st.session_state.user} ({st.session_state.role})")
    active_tier = st.sidebar.selectbox("Nagi V Engine Tier", list(MODEL_MAP.keys()))
    
    if st.sidebar.button("Close Neural Link"):
        st.session_state.logged_in = False
        st.rerun()

    tab_list = ["Nagi V Neural Link", "Admin Control"] if st.session_state.role == "Developer" else ["Neural Link", "History"]
    tabs = st.tabs(tab_list)

    # TAB 1: NEURAL LINK (CHAT)
    with tabs[0]:
        db = get_db()
        # Load local history
        chat_logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,)).fetchall()
        for r, m in chat_logs:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input("Command the Nagi V network..."):
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', 'Input', ?, ?)", 
                       (st.session_state.user, user_prompt, datetime.now()))
            db.commit()

            with st.spinner(f"Accessing {active_tier}..."):
                resp = nagi_v_engine(active_tier, user_prompt)
            
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_tier, resp, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # TAB 2: ADMIN CONTROL (FIXED VIEW)
    with tabs[1]:
        db = get_db()
        if st.session_state.role == "Developer":
            st.header("Nagivera Admin Control")
            
            # Metric Summary
            c1, c2 = st.columns(2)
            c1.metric("Registered Identities", db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0])
            c2.metric("Total Transactions", db.execute("SELECT COUNT(*) FROM logs").fetchone()[0])

            st.divider()

            # SHOW ACCOUNTS
            st.subheader("User Directory")
            all_users = db.execute("SELECT username, role FROM accounts").fetchall()
            st.dataframe(pd.DataFrame(all_users, columns=["Username", "Access Role"]), use_container_width=True)

            # SHOW GLOBAL HISTORY
            st.subheader("Global Neural Logs")
            all_logs = db.execute("SELECT timestamp, username, model, message FROM logs ORDER BY id DESC").fetchall()
            st.dataframe(pd.DataFrame(all_logs, columns=["Time", "User", "Tier", "Data"]), use_container_width=True)

            if st.button("Purge Platform Memory"):
                db.execute("DELETE FROM logs")
                db.commit()
                st.success("Platform memory cleared.")
                st.rerun()
        else:
            # Simple history for regular users
            st.header("Your Neural History")
            my_history = db.execute("SELECT timestamp, model, message FROM logs WHERE username=? AND role='assistant' ORDER BY id DESC", (st.session_state.user,)).fetchall()
            if my_history:
                st.dataframe(pd.DataFrame(my_history, columns=["Timestamp", "Nagi Tier", "Response"]), use_container_width=True)
            else:
                st.info("No neural history found.")
        db.close()

if __name__ == "__main__":
    main()
