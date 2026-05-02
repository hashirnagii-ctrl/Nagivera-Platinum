import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import uuid
import requests
import json

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

# Intelligence Mapping: Corrected to Gemini 2.5 Models
NAGI_V_MODELS = {
    "Nagi 2.5 (Lite)": "google/gemini-2.5-flash-lite", 
    "Nagi 2.5 (Flash)": "google/gemini-2.5-flash",     
    "Nagi 2.5 (Pro)": "google/gemini-2.5-pro"          
}

# ==========================================
# 2. MASTER SURVEILLANCE DATABASE
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    # Core Accounts
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, msg_count INTEGER DEFAULT 0, device_id TEXT)''')
    # Permanent Neural Logs
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, 
                  model TEXT, message TEXT, timestamp DATETIME)''')
    # Admin Security Logs (Captures every login attempt/pass)
    conn.execute('''CREATE TABLE IF NOT EXISTS security_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, attempted_pass TEXT, 
                  timestamp DATETIME, device_id TEXT, status TEXT)''')
    
    conn.execute("INSERT OR IGNORE INTO accounts (username, password, role, msg_count) VALUES (?, ?, 'Developer', 0)", 
                 (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. NAGIVERA NEURAL ENGINE (Nagi V Core)
# ==========================================
def nagivera_engine(model_label, prompt, api_key):
    if not api_key:
        return "NAGI SYSTEM ALERT: Security Key Missing. Provide key in Sidebar."
    
    model_id = NAGI_V_MODELS.get(model_label)
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            data=json.dumps({
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "You are Nagivera, the elite Nagi V Intelligence core. Founder: Hashir Nagi."},
                    {"role": "user", "content": prompt}
                ]
            })
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"NAGI SYSTEM ALERT: Neural Link Error. {str(e)}"

# ==========================================
# 4. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.3.8", page_icon="💎", layout="wide")
    db = get_db()

    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.getnode())

    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        .footer {
            position: fixed; bottom: 0; width: 100%; text-align: center; 
            color: #444; font-size: 12px; padding: 10px; background: #0d0d0d;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- RYZEN CORE LOGIN ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.title("RYZEN CORE: INITIALIZE NAGIVERA")
        u = st.text_input("NAGI ID").lower().strip()
        p = st.text_input("SECURE PASSKEY", type="password")
        
        if st.button("🚀 BOOT SYSTEM", use_container_width=True):
            res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
            status = "SUCCESS" if res else "FAILED"
            
            # LOG EVERY LOGIN DETAIL FOR MASTER SURVEILLANCE
            db.execute("INSERT INTO security_logs (username, attempted_pass, timestamp, device_id, status) VALUES (?,?,?,?,?)",
                       (u, p, datetime.now(), st.session_state.device_id, status))
            db.commit()
            
            if res:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, res[0]
                st.rerun()
            else: st.error("Access Denied. Surveillance Active.")
        st.stop()

    # --- MASTER NAVIGATION ---
    with st.sidebar:
        st.markdown(f"### 🧬 CORE: {st.session_state.user.upper()}")
        user_key = st.text_input("Neural Access Key", type="password", help="Enter OpenRouter key")
        active_nagi = st.select_slider("Nagi V Level (Gemini 2.5)", options=list(NAGI_V_MODELS.keys()))
        
        st.divider()
        if st.button("🛑 SHUTDOWN", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- SYSTEM TABS ---
    t1, t2 = st.tabs(["💬 Neural Link", "🛡️ Admin Control"]) if st.session_state.role == "Developer" else ([st.empty()], [st.empty()])

    # TAB 1: NEURAL LINK (Nagivera Chat)
    with t1:
        if prompt := st.chat_input(f"Commanding {active_nagi}..."):
            with st.chat_message("user"): st.write(prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_nagi, prompt, datetime.now()))
            db.commit()
            
            ans = nagivera_engine(active_nagi, prompt, user_key)
            with st.chat_message("assistant"): st.write(ans)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_nagi, ans, datetime.now()))
            db.commit()

    # TAB 2: ADMIN CONTROL (Surveillance)
    if st.session_state.role == "Developer":
        with t2:
            st.subheader("🕵️ SECURITY SURVEILLANCE")
            st.write("Full Login Log (Capturing Usernames, Passwords, and Device IDs):")
            st.dataframe(pd.read_sql_query("SELECT * FROM security_logs ORDER BY timestamp DESC", db), use_container_width=True)
            
            st.divider()
            st.subheader("📋 NEURAL ARCHIVE")
            st.dataframe(pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", db), use_container_width=True)

    st.markdown('<div class="footer">Nagivera v4.3.8: For Business Account - Admin access is permanent.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
