import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime
import uuid

# ==========================================
# 1. DATABASE & SECURITY PROTOCOL
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, msg_count INTEGER DEFAULT 0, device_id TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, 
                  model TEXT, message TEXT, timestamp DATETIME, hidden_from_user INTEGER DEFAULT 0)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS security_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, attempted_pass TEXT, 
                  timestamp DATETIME, device_id TEXT, status TEXT)''')
    conn.commit()
    return conn

# ==========================================
# 2. INTERFACE & NAVIGATION
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V Platinum", page_icon="💎", layout="wide")
    db = get_db()

    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.getnode())

    # --- 1. THE PERFECT PERSONALIZED LOGIN ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.title("⚡ NAGIVERA V4.3: INITIALIZE")
        
        # Hardware-themed Login Section
        st.markdown("### 🖥️ RYZEN CORE AUTHENTICATION")
        u = st.text_input("NAGI ID", help="Enter your verified identifier").lower().strip()
        p = st.text_input("SECURE PASSKEY", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 BOOT SYSTEM", use_container_width=True):
                res = db.execute("SELECT role, msg_count FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
                db.execute("INSERT INTO security_logs (username, attempted_pass, timestamp, device_id, status) VALUES (?,?,?,?,?)",
                           (u, p, datetime.now(), st.session_state.device_id, "SUCCESS" if res else "FAILED"))
                db.commit()
                if res:
                    st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, res[0]
                    st.session_state.page = "Business Account"
                    st.rerun()
                else: st.error("Authentication Error: Invalid Passkey.")
        
        with col2:
            if st.button("📝 REGISTER NEW NODE", use_container_width=True):
                st.info(f"Registering Device ID: {st.session_state.device_id}")
        st.stop()

    # --- 2. EASY-USE NAVIGATION ---
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💼 BUSINESS DASHBOARD", use_container_width=True):
            st.session_state.page = "Business Account"
            st.rerun()
    with c2:
        if st.button("💬 NEURAL LINK (CHAT)", use_container_width=True):
            st.session_state.page = "Neural Link"
            st.rerun()
    with c3:
        if st.button("🛑 SYSTEM SHUTDOWN", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- 3. PAGE LOGIC ---
    
    # PAGE: BUSINESS DASHBOARD (Personalized with Hardware & Focus)
    if st.session_state.page == "Business Account":
        st.header(f"💼 BUSINESS ACCOUNT: {st.session_state.user.upper()}")
        
        # New Business Personalization Section
        col_spec, col_stat = st.columns(2)
        with col_spec:
            st.subheader("🖥️ Hardware Topology")
            st.write(f"**Processor Architecture:** Ryzen Series")
            st.write(f"**Primary Device ID:** `{st.session_state.device_id}`")
            st.write(f"**Project Branch:** Nagivera v4.3.8")
        
        with col_stat:
            st.subheader("🛠️ Current Focus")
            st.write("• Mechanical: Bicycle Drivetrain Optimization")
            st.write("• Technical: AI Platform Scaling")
            st.write("• Creative: UI/Web Design Forge")

        st.divider()
        st.subheader("🔒 Permanent History Archive")
        user_history = db.execute("SELECT model, message, timestamp FROM logs WHERE username=? AND hidden_from_user=0 ORDER BY id DESC LIMIT 10", 
                                 (st.session_state.user,)).fetchall()
        
        if user_history:
            for mod, msg, ts in user_history:
                with st.expander(f"Log Instance: {ts}"):
                    st.write(msg)
        else:
            st.write("History view is currently clear.")

        if st.button("Archive View (Admin keeps full log)"):
            db.execute("UPDATE logs SET hidden_from_user=1 WHERE username=?", (st.session_state.user,))
            db.commit()
            st.rerun()

    # PAGE: NEURAL LINK (Chat with Quick-Actions)
    elif st.session_state.page == "Neural Link":
        st.sidebar.title("🧬 NEURAL SHORTCUTS")
        if st.sidebar.button("🚲 Cycle Maintenance Guide"):
            st.session_state.chat_input = "Show me the bicycle drivetrain repair checklist."
        if st.sidebar.button("💻 RYZEN Tuning"):
            st.session_state.chat_input = "Provide optimization scripts for my Ryzen setup."
        
        st.subheader("Neural Link Connected")
        if prompt := st.chat_input("Type your command..."):
            with st.chat_message("user"): st.write(prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp, hidden_from_user) VALUES (?, 'user', 'Nagi-V', ?, ?, 0)", 
                       (st.session_state.user, prompt, datetime.now()))
            db.commit()
            with st.chat_message("assistant"):
                st.write("Command logged. Processing via Nagivera Core...")

    # --- 4. ADMIN CONTROL (Developer Only) ---
    if st.session_state.role == "Developer":
        with st.sidebar:
            st.divider()
            if st.button("⚠️ MASTER LOGS"):
                st.session_state.page = "Admin"
                st.rerun()

    if st.session_state.get('page') == "Admin":
        st.title("MASTER SECURITY LOGS")
        st.write("Every password used and login attempt captured:")
        st.dataframe(pd.read_sql_query("SELECT * FROM security_logs", db), use_container_width=True)
        st.write("Total Chat Archive:")
        st.dataframe(pd.read_sql_query("SELECT * FROM logs", db), use_container_width=True)

    # MANDATORY FOOTER
    st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: #000; text-align: center; padding: 10px; color: #555;">
            For Business Account: Only you and the Admin can see your history.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
