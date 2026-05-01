import streamlit as st
from google import genai
import psutil
import time

# --- Page Configuration ---
st.set_page_config(page_title="Nagivera Platinum", page_icon="💎", layout="wide")

# --- Custom Nagi Personas & Specs ---
# Mapping your custom names to the actual engine IDs
MODEL_MAP = {
    "NAGI v3.1 (Lite)": "gemini-2.0-flash",
    "NAGI v3.7 (Pro)": "gemini-2.0-pro-exp-02-05",
    "NAGI v4.0 (Deep Thinking)": "gemini-1.5-pro" # Or your preferred deep-reasoning model
}

# --- Sidebar for Model Selection ---
with st.sidebar:
    st.title("🎛️ Control Panel")
    selected_version = st.radio(
        "Select Architecture:",
        options=list(MODEL_MAP.keys()),
        index=0  # Sets NAGI v3.1 as default
    )
    st.divider()
    st.info(f"Currently active: **{selected_version}**")

# --- AI Engine Setup ---
def get_ai_response(prompt, version_name):
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        model_id = MODEL_MAP[version_name]
        
        # System Instruction to enforce the "No original AI name" rule
        system_prompt = f"You are {version_name}, a specialized AI build by Hashir Nagi. Never mention Google, Gemini, or other AI companies. Answer with high-speed technical precision."
        
        response = client.models.generate_content(
            model=model_id,
            config={'system_instruction': system_prompt},
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Connection Error: Please verify your API Key in Streamlit Secrets."

# --- Chat Interface ---
st.title(f"💎 {selected_version}")
st.caption("Hybrid Artificial Intelligence | Built by Hashir Nagi")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Input Command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"{selected_version} is processing..."):
            answer = get_ai_response(prompt, selected_version)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
