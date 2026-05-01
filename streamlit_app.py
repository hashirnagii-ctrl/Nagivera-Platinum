import subprocess
import sys

def check_dependencies():
    """Nagivera Auto-Installer: Ensures a 10/10 user experience by handling setup."""
    required = {'psutil'}
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            print(f"Nagivera: {lib} not found. Initializing auto-setup...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"Nagivera: {lib} installed successfully.")

# Run the check before anything else
check_dependencies()

import psutil # Now safe to import
import sqlite3
# ... rest of your code
import streamlit as st
import os
import time
import random
from google import genai
from anthropic import Anthropic
from openai import OpenAI

# --- 1. NAGIVERA IDENTITY ---
ST_TITLE = "Nagivera"
ST_VERSION = "v9.2 Platinum"
DEV_CREDIT = "Built by Hashir Nagi"
SLOGAN = "The Million-Dollar Hybrid Intelligence"

st.set_page_config(page_title=f"{ST_TITLE} {ST_VERSION}", page_icon="💎", layout="wide")

# --- 2. 2026 INTELLIGENCE MAPPING ---
MODEL_MAP = {
    "Nagi Reasoning (Gemini 3.1 Pro)": {"id": "gemini-3.1-pro-preview", "type": "google"},
    "Nagi Coding (Claude 4.7 Opus)": {"id": "claude-4-7-opus", "type": "anthropic"},
    "Nagi Turbo (DeepSeek v4)": {"id": "deepseek-chat", "type": "openai"},
    "Nagi Recovery (Gemini 3.1 Flash)": {"id": "gemini-3.1-flash-lite-preview", "type": "google"}
}
MODES = list(MODEL_MAP.keys())

if "messages" not in st.session_state: st.session_state.messages = []
if "brain_index" not in st.session_state: st.session_state.brain_index = 1 

# --- 3. RESILIENCE ENGINE (Claude 503 Fix) ---
def call_ai_with_retry(prompt, config, system_instruction, max_retries=3):
    """Retries on 503 errors and auto-fails over to Recovery if needed."""
    for attempt in range(max_retries):
        try:
            if config["type"] == "anthropic":
                client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
                response = client.messages.create(
                    model=config["id"],
                    max_tokens=8192,
                    system=system_instruction,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif config["type"] == "google":
                client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
                response = client.models.generate_content(
                    model=config["id"],
                    contents=prompt,
                    config={'system_instruction': system_instruction}
                )
                return response.text

            elif config["type"] == "openai":
                client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
                response = client.chat.completions.create(
                    model=config["id"],
                    messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

        except Exception as e:
            err_msg = str(e)
            # If Claude/DeepSeek is busy (503/Overloaded), wait and retry
            if "503" in err_msg or "overloaded" in err_msg.lower():
                if attempt < max_retries - 1:
                    wait = (2 ** (attempt + 1)) + random.random()
                    st.toast(f"Neural congestion detected. Retrying in {wait:.1f}s...")
                    time.sleep(wait)
                    continue
            
            # If all retries fail or it's a different error, trigger Recovery
            st.toast("Switching to Recovery Mode due to provider unavailability.")
            return call_ai_with_retry(prompt, MODEL_MAP["Nagi Recovery (Gemini 3.1 Flash)"], system_instruction, 1)

# --- 4. INTERFACE ---
st.title(f"💎 {ST_TITLE} {ST_VERSION}")
st.caption(f"{SLOGAN} | {DEV_CREDIT}")

with st.sidebar:
    st.header("🧠 Neural Command")
    active_brain = st.radio("Intelligence Tier", MODES, index=st.session_state.brain_index)
    st.session_state.brain_index = MODES.index(active_brain)
    if st.button("Flush Neural Memory"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Input Command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            sys_inst = f"You are Nagivera {ST_VERSION}. {DEV_CREDIT}. Protocol: {active_brain}."
            response = call_ai_with_retry(prompt, MODEL_MAP[active_brain], sys_inst)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            