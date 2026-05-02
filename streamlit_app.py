import streamlit as st
import requests
import json
from datetime import datetime

# ==========================================
# 1. CORE SYSTEM IDENTITY
# ==========================================
# OWNER: Hashir Nagi
# ENGINE: DeepSeek V3 (Coding Specialist)

# SECURITY PROTOCOL: Use st.secrets in production!
# For now, I've plugged in the key you provided.
DEEPSEEK_API_KEY = "sk-b497aa3622e3494ea9dccf8956ac6f08"

def nagivera_deepseek_engine(prompt):
    # This system prompt locks Nagivera into 'Coding Only' mode
    system_identity = (
        "You are Nagivera v5.1, a dedicated AI Coding Architect. "
        "Your only purpose is to write, debug, and explain code. "
        "If a user asks a non-coding question, politely refuse and ask for a programming task."
    )
    
    # DeepSeek API Endpoint (Standard OpenAI-compatible format)
    url = "https://api.deepseek.com/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-coder", # Best for programming logic
        "messages": [
            {"role": "system", "content": system_identity},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "NAGI SECURITY ERROR: API Key Invalid or unauthorized."
        else:
            return f"NAGI SYSTEM ERROR: {response.status_code} - {response.text}"
    except Exception as e:
        return f"NAGI LINK FAILURE: {str(e)}"

# ==========================================
# 2. INTERFACE ARCHITECTURE
# ==========================================
def main():
    st.set_page_config(page_title="Nagivera Coder", page_icon="⚡")
    
    st.title("🧬 Nagivera DeepSeek Coder")
    st.info("System Status: Logic-Pro Engine Active | Port: 443")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask Nagivera to write or debug code..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing Neural Logic..."):
                response = nagivera_deepseek_engine(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
