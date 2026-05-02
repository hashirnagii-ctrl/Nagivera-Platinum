import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import requests
import json

# --- CONFIG ---
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011"
NAGIVERA_KEY = "sk-or-v1-c4689f48111df8ff64acad..." # Ensure this is your fresh key

NAGI_V_MODELS = {
    "Nagi V (Core-Flash)": {"id": "glm-4-7-flash", "type": "local"},
    "Nagi V (Logic-Pro)": {"id": "deepseek-v3.2", "type": "local"},
    "Nagi V (Ultra-Lite)": {"id": "stable-lm-3b", "type": "local"},
    "Nagi 3.1 (Cloud)": {"id": "google/gemini-3.1-flash-lite-preview", "type": "cloud"}
}

def get_db():
    conn = sqlite3.connect('nagi_v_final.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS security_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, attempted_pass TEXT, 
                  timestamp DATETIME, status TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, role TEXT, 
                  model TEXT, message TEXT, timestamp DATETIME)''')
    return conn

def nagivera_engine(model_label, prompt):
    config = NAGI_V_MODELS.get(model_label)
    try:
        if config["type"] == "local":
            response = requests.post("http://localhost:11434/api/generate", 
                                     json={"model": config["id"], "prompt": prompt, "stream": False}, timeout=5)
            return response.json().get('response')
        else:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {NAGIVERA_KEY}"},
                json={"model": config["id"], "max_tokens": 1000, "messages": [{"role": "user", "content": prompt}]})
            return response.json()['choices'][0]['message']['content']
    except:
        return "NAGI SYSTEM ALERT: Neural Link Interrupted. Switch to Cloud or start Ollama."

def main():
    st.set_page_config(page_title="Nagivera v4.3.9", layout="wide")
    db = get_db()

    if 'logged_in' not in st.session_state:
        st.title("RYZEN CORE: INITIALIZE")
        u = st.text_input("NAGI ID")
        p = st.text_input("PASSKEY", type="password")
        if st.button("🚀 BOOT SYSTEM"):
            if u == MASTER_USER and p == MASTER_PASS:
                st.session_state.logged_in = True
                db.execute("INSERT INTO security_logs (username, attempted_pass, timestamp, status) VALUES (?,?,?,?)", (u, p, datetime.now(), "SUCCESS"))
                db.commit()
                st.rerun()
        st.stop()

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("🧬 NAGI V")
        active_nagi = st.selectbox("Neural Core", options=list(NAGI_V_MODELS.keys()))
        if st.button("🛑 SHUTDOWN"):
            st.session_state.logged_in = False
            st.rerun()

    # --- TABS (Admin is back here) ---
    tab1, tab2 = st.tabs(["💬 Neural Link", "🛡️ Admin Control"])

    with tab1:
        if prompt := st.chat_input("Command..."):
            st.chat_message("user").write(prompt)
            ans = nagivera_engine(active_nagi, prompt)
            st.chat_message("assistant").write(ans)
            db.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?,?,?,?,?)", ("hashir", "assistant", active_nagi, ans, datetime.now()))
            db.commit()

    with tab2:
        st.subheader("🕵️ SECURITY SURVEILLANCE")
        st.dataframe(pd.read_sql_query("SELECT * FROM security_logs", db), use_container_width=True)
        st.subheader("📋 MESSAGE ARCHIVE")
        st.dataframe(pd.read_sql_query("SELECT * FROM logs", db), use_container_width=True)

if __name__ == "__main__":
    main()
