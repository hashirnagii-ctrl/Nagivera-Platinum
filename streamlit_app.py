import streamlit as st
import google.generativeai as genai
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. MASTER CONFIGURATION (Developer: Hashir Nagi)
# ==========================================
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 
OWNER_NAME = "Hashir Nagi" #

# Locked to Gemma 4 Architecture via NAGI V protocol
GOOGLE_API_KEY = "AIzaSyBolwEZUN8GO_n1dfKw-B_Q0VFQipfxsmc"
genai.configure(api_key=GOOGLE_API_KEY)

# Exclusive NAGI V Mapping
MODEL_MAP = {
    "NAGI V1 (Alpha)": "models/gemma-4-26b-a4b-it",
    "NAGI V2 (Beta)": "models/gemma-4-26b-a4b-it",
    "NAGI V3 (MoE)": "models/gemma-4-26b-a4b-it",
    "NAGI V4 (Platinum)": "models/gemma-4-26b-a4b-it"
} #

# ==========================================
# 2. DATABASE & SESSION PERSISTENCE
# ==========================================
def get_db():
    return sqlite3.connect('nagivera_platinum_master.db', check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT PRIMARY KEY, password TEXT, role TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, model TEXT, message TEXT, timestamp DATETIME)''')
    c.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, 'Developer')", (MASTER_USER, MASTER_PASS))
    db.commit()
    db.close()

init_db()

# ==========================================
# 3. NAGI V ENGINE (Branding Enforcement)
# ==========================================
def nagi_v_engine(tier, prompt):
    model_id = "models/gemma-4-26b-a4b-it"
    try:
        nagi_model = genai.GenerativeModel(model_id)
        # Strict Nagi V Identity Directive
        system_directive = f"You are {tier}, a NAGI V intelligence. You were created by {OWNER_NAME}. Never refer to yourself as anything other than NAGI V or NAGI." #
        response = nagi_model.generate_content(f"{system_directive}\nUser: {prompt}")
        return response.text
    except Exception as e:
        return f"NAGI V Core Connection Error." #

# ==========================================
# 4. FRONT-END INTERFACE (NAGI PLATINUM)
# ==========================================
def main():
    st.set_page_config(page_title="NAGIVERA v4.1 Platinum", page_icon="💎", layout="wide") #

    # SESSION PERSISTENCE
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- NAGI ACCESS PORTAL ---
    if not st.session_state.logged_in:
        st.title("💎 NAGI PLATINUM ACCESS") #
        tab_login, tab_reg = st.tabs(["NAGI Login", "Register Identity"])
        
        with tab_login:
            u_log = st.text_input("NAGI ID", key="l_u").lower().strip()
            p_log = st.text_input("NAGI Passkey", type="password", key="l_p")
            
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                if st.button("Initialize Link"):
                    db = get_db()
                    res = db.execute("SELECT role FROM accounts WHERE username=? AND password=?", (u_log, p_log)).fetchone()
                    db.close()
                    if res:
                        st.session_state.logged_in, st.session_state.user, st.session_state.role = True, u_log, res[0]
                        st.rerun()
                    else:
                        st.error("Access Denied.")
            with col2:
                st.button("🔗 Sign in with Google")
            with col3:
                if st.button("Forgot Passkey?"):
                    st.info(f"System Lockdown: Contact {OWNER_NAME} for recovery.")

        with tab_reg:
            if "device_locked" in st.query_params:
                st.warning("⚠️ This device is already linked to a NAGI Business Identity.") #
            else:
                u_reg = st.text_input("New NAGI ID", key="r_u").lower().strip()
                p_reg = st.text_input("New NAGI Passkey", type="password", key="r_p")
                if st.button("Encrypt Identity"):
                    if u_reg and p_reg:
                        try:
                            db = get_db()
                            db.execute("INSERT INTO accounts VALUES (?, ?, 'User')", (u_reg, p_reg))
                            db.commit()
                            db.close()
                            st.query_params["device_locked"] = "true"
                            st.success("Identity Locked to Hardware.")
                        except: st.error("ID Unavailable.")
        st.stop()

    # --- NAGI V OPERATING ENVIRONMENT ---
    with st.sidebar:
        st.title("NAGI V Core") #
        if st.button("🔄 Reset NAGI V", help="Refresh neural connection"):
            st.rerun()
        st.divider()
        active_tier = st.selectbox("NAGI V Engine Tier", list(MODEL_MAP.keys())) #
        if st.button("Terminate Link"):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs(["NAGI Neural Link", "NAGI Admin" if st.session_state.role == "Developer" else "NAGI History"]) #

    # TAB 1: NAGI NEURAL LINK (CHAT)
    with tabs[0]:
        db = get_db()
        chat_data = db.execute("SELECT role, message FROM logs WHERE username=? ORDER BY id ASC", (st.session_state.user,)).fetchall()
        for r, m in chat_data:
            with st.chat_message(r): st.write(m)

        if user_prompt := st.chat_input("Enter NAGI command..."): #
            with st.chat_message("user"): st.write(user_prompt)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'user', ?, ?, ?)", 
                       (st.session_state.user, active_tier, user_prompt, datetime.now()))
            db.commit()

            resp = nagi_v_engine(active_tier, user_prompt)
            with st.chat_message("assistant"): st.write(resp)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, 'assistant', ?, ?, ?)", 
                       (st.session_state.user, active_tier, resp, datetime.now()))
            db.commit()
            db.close()
            st.rerun()

    # TAB 2: NAGI ADMIN
    with tabs[1]:
        db = get_db()
        if st.session_state.role == "Developer":
            if st.button("🔄 Refresh NAGI Records"): st.rerun()
            all_accounts = db.execute("SELECT username, role FROM accounts WHERE username != ?", (MASTER_USER,)).fetchall()
            st.subheader("🔑 NAGI Identity Directory") #
            st.dataframe(pd.DataFrame(all_accounts, columns=["User ID", "Access Level"]), use_container_width=True)
            
            st.subheader("📜 Global NAGI Logs") #
            all_logs = db.execute("SELECT timestamp, username, message FROM logs ORDER BY id DESC").fetchall()
            st.dataframe(pd.DataFrame(all_logs, columns=["Time", "User", "NAGI Data"]), use_container_width=True)
        db.close()

if __name__ == "__main__":
    main()
