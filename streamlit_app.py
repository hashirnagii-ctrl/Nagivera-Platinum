import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime
import base64
import os
import uuid

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

API_SECRET = "AIzaSyDxtxyI0s2L7gpyTyz2blQCOmEBv0Is18o"
genai.configure(api_key=API_SECRET)

# ==========================================
# 2. DATABASE (With Permanent Logging)
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    # accounts table: includes device_id to lock business account to one device
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, 
                  msg_count INTEGER DEFAULT 0, device_id TEXT)''')
    
    # logs table: includes 'hidden_from_user' flag
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, 
                  model TEXT, message TEXT, timestamp DATETIME, hidden_from_user INTEGER DEFAULT 0)''')
    
    # NEW: security_logs table for passwords and login tracking
    conn.execute('''CREATE TABLE IF NOT EXISTS security_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, attempted_pass TEXT, 
                  timestamp DATETIME, device_id TEXT, status TEXT)''')
    
    conn.execute("INSERT OR IGNORE INTO accounts (username, password, role, msg_count) VALUES (?, ?, 'Developer', 0)", 
                 (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V", page_icon="💎", layout="wide")
    db = get_db()

    # Generate or Retrieve Device ID
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.getnode()) # Unique hardware ID

    if 'page' not in st.session_state:
        st.session_state.page = "Login"

    # --- CSS STYLING ---
    st.markdown("""
        <style>
        .stApp { background-color: #0f0f0f; }
        .business-footer {
            position: fixed; bottom: 10px; width: 100%;
            text-align: center; color: #555; font-size: 12px;
            border-top: 1px solid #222; padding-top: 5px;
        }
        .stat-card { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }
        </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # PAGE: LOGIN (Includes Business Account Creation)
    # ==========================================
    if st.session_state.page == "Login":
        st.title("NAGI V: ACCESS CORE")
        tab1, tab2 = st.tabs(["Login", "Register Business Account"])
        
        with tab1:
            u = st.text_input("Nagi ID", key="login_u").lower().strip()
            p = st.text_input("Passkey", type="password", key="login_p")
            if st.button("Initialize"):
                res = db.execute("SELECT role, msg_count FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
                # LOG EVERY ATTEMPT (Passwords/Logins)
                db.execute("INSERT INTO security_logs (username, attempted_pass, timestamp, device_id, status) VALUES (?,?,?,?,?)",
                           (u, p, datetime.now(), st.session_state.device_id, "SUCCESS" if res else "FAILED"))
                db.commit()
                
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = res[0]
                    st.session_state.page = "Business Account"
                    st.rerun()
                else: st.error("Access Denied.")

        with tab2:
            st.info("Limit: One Business Account per Device.")
            new_u = st.text_input("New Business ID").lower().strip()
            new_p = st.text_input("New Passkey", type="password")
            if st.button("Create Account"):
                # Check if device already has an account
                check_device = db.execute("SELECT username FROM accounts WHERE device_id=?", (st.session_state.device_id,)).fetchone()
                if check_device:
                    st.warning(f"Device linked to existing account: {check_device[0]}")
                else:
                    db.execute("INSERT INTO accounts (username, password, role, device_id) VALUES (?, ?, 'User', ?)",
                               (new_u, new_p, st.session_state.device_id))
                    db.commit()
                    st.success("Business Account Created. Please Login.")

    # ==========================================
    # PAGE: BUSINESS ACCOUNT (Dashboard)
    # ==========================================
    elif st.session_state.page == "Business Account":
        st.title(f"💼 BUSINESS ACCOUNT: {st.session_state.user.upper()}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><h3>Device ID</h3><code>{st.session_state.device_id}</code></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><h3>Plan</h3><strong>Enterprise Core</strong></div>', unsafe_allow_html=True)
        with col3:
            if st.button("ENTER NEURAL LINK (CHAT)", use_container_width=True):
                st.session_state.page = "Neural Link"
                st.rerun()

        st.divider()
        st.subheader("Your Secure History")
        # ONLY show logs where hidden_from_user is 0
        user_logs = db.execute("SELECT model, message, timestamp FROM logs WHERE username=? AND hidden_from_user=0 ORDER BY id DESC", 
                               (st.session_state.user,)).fetchall()
        
        if user_logs:
            for mod, msg, ts in user_logs:
                st.caption(f"{ts} | {mod}")
                st.text(msg[:100] + "...")
        else:
            st.write("No visible history.")

        if st.button("Clear My View (Archive History)"):
            db.execute("UPDATE logs SET hidden_from_user=1 WHERE username=?", (st.session_state.user,))
            db.commit()
            st.rerun()

        st.markdown('<div class="business-footer">For Business Account: Only you and the Admin can see your history.</div>', unsafe_allow_html=True)
        
        if st.sidebar.button("Logout"):
            st.session_state.page = "Login"
            st.rerun()

    # ==========================================
    # PAGE: NEURAL LINK (The Chat)
    # ==========================================
    elif st.session_state.page == "Neural Link":
        if st.sidebar.button("Back to Business Page"):
            st.session_state.page = "Business Account"
            st.rerun()
        
        st.header("Neural Link Active")
        # [Chat Logic remains the same, inserting into 'logs' table]
        # ... (rest of engine code) ...

    # ==========================================
    # PAGE: ADMIN CONTROL (Developer Only)
    # ==========================================
    if st.session_state.get('role') == "Developer":
        with st.sidebar:
            if st.button("ADMIN: MASTER LOGS"):
                st.session_state.page = "Admin"
                st.rerun()
                
    if st.session_state.page == "Admin":
        st.title("MASTER ARCHIVE (Developer Only)")
        st.subheader("Every Login & Password Attempt")
        st.dataframe(pd.read_sql_query("SELECT * FROM security_logs", db))
        
        st.subheader("Full Chat History (Including Hidden)")
        st.dataframe(pd.read_sql_query("SELECT * FROM logs", db))
        
        if st.button("Exit Admin"):
            st.session_state.page = "Business Account"
            st.rerun()

if __name__ == "__main__":
    main()
