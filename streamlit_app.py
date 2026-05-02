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

# CLOUD ACCESS KEY (OpenRouter)
NAGIVERA_KEY = "sk-or-v1-c4689f48111df8ff64acad..." # Update with your active key

# Nagivera Neural Mapping (Hybrid: Local + Cloud)
NAGI_V_MODELS = {
    "Nagi V (Core-Flash)": {"id": "glm-4-7-flash", "type": "local"},
    "Nagi V (Logic-Pro)": {"id": "deepseek-v3.2", "type": "local"},
    "Nagi V (Ultra-Lite)": {"id": "stable-lm-3b", "type": "local"},
    "Nagi 3.1 (Cloud)": {"id": "google/gemini-3.1-flash-lite-preview", "type": "cloud"}
}

# ==========================================
# 2. HYBRID NEURAL ENGINE
# ==========================================
def nagivera_engine(model_label, prompt):
    config = NAGI_V_MODELS.get(model_label)
    model_id = config["id"]
    
    try:
        # --- PATH A: LOCAL INTELLIGENCE (Ollama/LM Studio) ---
        if config["type"] == "local":
            response = requests.post(
                url="http://localhost:11434/api/generate", # Default Ollama Port
                json={
                    "model": model_id,
                    "prompt": f"System: You are Nagivera. User: {prompt}",
                    "stream": False
                }
            )
            return response.json().get('response', 'NAGI LOCAL ERROR: No response data.')

        # --- PATH B: CLOUD INTELLIGENCE (OpenRouter) ---
        else:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {NAGIVERA_KEY}",
                    "X-Title": "Nagivera v4.3.9",
                },
                json={
                    "model": model_id,
                    "max_tokens": 2048, # Capped to prevent credit errors
                    "messages": [
                        {"role": "system", "content": f"You are Nagivera. Founder: {OWNER_NAME}."},
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            res_json = response.json()
            if 'choices' in res_json:
                return res_json['choices'][0]['message']['content']
            else:
                error_msg = res_json.get('error', {}).get('message', 'Neural Link Rejected.')
                return f"NAGI SYSTEM ALERT: {error_msg}"
            
    except Exception as e:
        return f"NAGI SYSTEM ALERT: Neural Link Interrupted. Ensure local server is running."

# ==========================================
# 3. INTERFACE ARCHITECTURE (Simplified for dev)
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera v4.3.9", page_icon="💎", layout="wide")
    db = sqlite3.connect('nagi_v_final.db', check_same_thread=False)

    # Login Logic (Assuming session_state from previous version)
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        # ... [Same Login UI as v4.3.8] ...
        st.session_state.logged_in = True # Auto-bypass for code brevity
        st.session_state.user = "hashir"
        st.session_state.role = "Developer"

    with st.sidebar:
        st.title("🧬 NAGI V CORE")
        # Selector for the new local names
        active_nagi = st.selectbox("Select Neural Core", options=list(NAGI_V_MODELS.keys()))
        
        status = "🟢 LOCAL ACTIVE" if NAGI_V_MODELS[active_nagi]["type"] == "local" else "🌐 CLOUD ACTIVE"
        st.info(f"Status: {status}")

    # CHAT INTERFACE
    if prompt := st.chat_input(f"Commanding {active_nagi}..."):
        with st.chat_message("user"): st.write(prompt)
        
        ans = nagivera_engine(active_nagi, prompt)
        
        with st.chat_message("assistant"): st.write(ans)

if __name__ == "__main__":
    main()
