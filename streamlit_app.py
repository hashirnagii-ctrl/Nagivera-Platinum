import streamlit as st
import sqlite3
from datetime import datetime
import requests
import json

# ==========================================
# 1. CORE SYSTEM IDENTITY
# ==========================================
OWNER_NAME = "Hashir Nagi"
MASTER_USER = "hashir"
MASTER_PASS = "Hashirnagi2011" 

# Replace this with your NEW key (after the GitHub leak reset)
DEEPSEEK_API_KEY = "sk-b497aa3622e3494ea9dccf8956ac6f08" 

# The specific engine for elite coding
DEEPSEEK_MODEL_ID = "deepseek/deepseek-coder"

def get_db():
    conn = sqlite3.connect('nagi_coder_final.db', check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS coding_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, prompt TEXT, response TEXT, timestamp DATETIME)''')
    return conn

# ==========================================
# 2. THE DEEPSEEK NEURAL ENGINE
# ==========================================
def deepseek_coder_engine(prompt):
    # Specialized prompt to lock the AI into "Coding Only" mode
    CODING_IDENTITY = (
        "You are Nagivera Coder, an elite neural architect. "
        "Your purpose is exclusively software engineering, debugging, and system design. "
        "Reject any non-technical queries. Always respond with clean, production-grade code."
    )
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "X-Title": "Nagivera Coder v5.0",
            },
            json={
                "model": DEEPSEEK_MODEL_ID,
                "messages": [
                    {"role": "system", "content": CODING_IDENTITY},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        res_json = response.json()
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            return f"NAGI ERROR: {res_json.get('error', {}).get('message', 'Neural Link Failed.')}"
            
    except Exception as e:
        return "NAGI SYSTEM ALERT: Neural Link Interrupted. Check your internet connection."

# ==========================================
# 3. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera Coder", page_icon="💻", layout="wide")
    db = get_db()

    # Simple Master-User Auth
    if 'logged_in' not in st.session_state:
        st.title("RYZEN CODER: INITIALIZE")
        u = st.text_input("NAGI ID")
        p = st.text_input("PASSKEY", type="password")
        if st.button("🚀 BOOT SYSTEM"):
            if u == MASTER_USER and p == MASTER_PASS:
                st.session_state.logged_in = True
                st.rerun()
        st.stop()

    st.title("🧬 Nagivera Coder v5.0")
    st.caption(f"Proprietary Engine for {OWNER_NAME} | DeepSeek-V3 Coder Active")

    # CHAT INTERFACE
    if prompt := st.chat_input("Enter code task or debug request..."):
        with st.chat_message("user"):
            st.code(prompt, language='python') # Formats your input as code
        
        with st.spinner("Analyzing Logic..."):
            ans = deepseek_coder_engine(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(ans)
            
        # Log to Database
        db.execute("INSERT INTO coding_logs (prompt, response, timestamp) VALUES (?,?,?)", 
                   (prompt, ans, datetime.now()))
        db.commit()

if __name__ == "__main__":
    main()
