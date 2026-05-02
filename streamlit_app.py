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

# Intelligence Mapping: Verified Compatible Models for Nagi V
NAGI_V_MODELS = {
    "Nagi 2.5 (Lite)": "google/gemini-2.5-flash-lite", 
    "Nagi 2.5 (Flash)": "google/gemini-2.5-flash",     
    "Nagi 2.5 (Pro)": "google/gemini-2.5-pro",
    "Nagi 3.1 (Experimental)": "google/gemini-3.1-flash-lite-preview"
}

# ==========================================
# 2. MASTER SURVEILLANCE DATABASE
# ==========================================
def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    # Core Accounts
    conn.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, msg_count INTEGER DEFAULT 0, device_id TEXT)''')
    
    # Permanent Neural Logs (Chat History)
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, 
                  model TEXT, message TEXT, timestamp DATETIME)''')
    
    # MASTER SECURITY LOGS (Captures Login Name, Password, Status, and Device ID)
    conn.execute('''CREATE TABLE IF NOT EXISTS security_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, attempted_pass TEXT, 
                  timestamp DATETIME, device_id TEXT, status TEXT)''')
    
    conn.execute("INSERT OR IGNORE INTO accounts (username, password, role, msg_count) VALUES (?, ?, 'Developer', 0)", 
                 (MASTER_USER, MASTER_PASS))
    conn.commit()
    return conn

# ==========================================
# 3. NAGIVERA NEURAL ENGINE
# ==========================================
def nagivera_engine(model_label, prompt, api_key):
    if not api_key:
        return "NAGI SYSTEM ALERT: Neural Access Key Missing. Provide key in Sidebar."
    
    model_id = NAGI_V_MODELS.get(model_label)
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8501", 
                "X-Title": "Nagivera v4.3.8",
            },
            data=json.dumps({
                "model": model_id,
                "messages": [
                    {"role": "system", "content": f"You are Nagivera, the elite Nagi V Intelligence core. Founder: {OWNER_NAME}. Character: Insightful, technical, and supportive."},
                    {"role": "user", "content": prompt}
                ]
            })
        )
        res_json = response.json()
        
        # Check if 'choices' exists to avoid the error seen in image_7b8dd5.png
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            error_details = res_json.get('error', {}).get('message', 'Unknown API Error')
            return f"NAGI SYSTEM ALERT: API rejected request. Reason: {error_details}"
            
    except Exception as e:
        return f"NAGI SYSTEM ALERT: Neural Link Interrupted. {str(e)}"

# ==========================================
# 4. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.3.8", page_icon="💎", layout="wide")
    db = get_db()

    # Generate or retrieve unique device hardware ID
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

    # --- RYZEN CORE LOGIN SYSTEM ---
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.title("RYZEN CORE: INITIALIZE NAGIVERA")
        u = st.text_input("NAGI ID").lower().strip()
        p = st.text_input("SECURE PASSKEY", type="password")
        
        if st.button("🚀 BOOT SYSTEM", use_container_width=True):
            res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u, p)).fetchone()
            status = "SUCCESS" if res else "FAILED"
            
            # CRITICAL: Record every login detail immediately
            db.execute("INSERT INTO security_logs (username, attempted_pass, timestamp, device_id, status) VALUES (?,?,?,?,?)",
                       (u, p, datetime.now(), st.session_state.device_id, status))
            db.commit()
            
            if res:
                st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u, res[0]
                st.rerun()
            else: st.error("Access Denied. Hardware ID Logged.")
        st.stop()

    # --- SIDEBAR: NAGI PERSONALIZATION ---
    with st.sidebar:
        st.markdown(f"### 🧬 CORE: {st.session_state.user.upper()}")
        user_key = st.text_input("Neural Access Key", type="password", help="Enter your sk-or-v1... key")
        active_nagi = st.select_slider("Nagi V Intelligence Level", options=list(NAGI_V_MODELS.keys()))
        
        st.divider()
        if st.button("🚲 Cycle Maintenance AI", use_container_width=True):
            st.toast("Drivetrain repair logic synced.")
        if st.button("💻 RYZEN Tuning", use_container_width=True):
            st.toast("Hardware optimization protocols active.")
            
        st.divider()
        if st.button("🛑 SHUTDOWN SESSION", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- MAIN SYSTEM TABS ---
    is_dev = st.session_state.role == "Developer"
    tab_list = ["💬 Neural Link"]
    if is_dev: tab_list.append("🛡️ Admin Control")
    
    main_tabs = st.tabs(tab_list)

    # TAB 1: NEURAL LINK (The Chat Engine)
    with main_tabs[0]:
        # Display session history from DB
        chat_logs = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id DESC LIMIT 20", (st.session_state.user,)).fetchall()[::-1]
        for r, m in chat_logs:
            with st.chat_message(r): st.write(m)

        if prompt := st.chat_input(f"Commanding {active_nagi}..."):
            with st.chat_message("user"): st.write(prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_nagi, prompt, datetime.now()))
            db.commit()
            
            # Call the engine
            ans = nagivera_engine(active_nagi, prompt, user_key)
            
            with st.chat_message("assistant"): st.write(ans)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_nagi, ans, datetime.now()))
            db.commit()

    # TAB 2: ADMIN CONTROL (Surveillance Dashboard)
    if is_dev:
        with main_tabs[1]:
            st.subheader("🕵️ MASTER SURVEILLANCE: LOGIN ATTEMPTS")
            st.info("Records every login name and password attempted on this device.")
            security_df = pd.read_sql_query("SELECT * FROM security_logs ORDER BY timestamp DESC", db)
            st.dataframe(security_df, use_container_width=True)
            
            st.divider()
            st.subheader("📋 GLOBAL CHAT ARCHIVE")
            global_chat_df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", db)
            st.dataframe(global_chat_df, use_container_width=True)

    st.markdown('<div class="footer">Nagivera v4.3.8: Secure Business Environment. Admin access is absolute.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
