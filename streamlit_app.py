import streamlit as st
from google import genai

# --- Page Configuration ---
st.set_page_config(page_title="Nagivera Platinum", page_icon="💎", layout="wide")

# --- Model Mapping ---
MODEL_MAP = {
    "NAGI v4.1 (Lite)": "gemma-4-26b-a4b-it",
    "NAGI v4.1 (Rapid)": "gemma-4-26b-a4b-it",
    "NAGI v4.1 (Ultra)": "gemma-4-31b-it"
}

# --- Sidebar ---
with st.sidebar:
    st.title("🎛️ Control Panel")
    selected_version = st.radio(
        "Select Architecture:",
        options=list(MODEL_MAP.keys()),
        index=0 
    )
    st.divider()
    st.success(f"Running on **{selected_version}**")

# --- AI Engine Setup ---
def get_ai_response(prompt, version_name):
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        model_id = MODEL_MAP[version_name]
        
        # --- Strict Persona Instructions ---
        system_prompt = (
            f"You are {version_name}, a specialized AI developed by Hashir Nagi. "
            "Hashir Nagi is a 14-year-old tech innovator and developer. "
            "Nagivera is a custom AI platform with its primary data center located in Rawalpindi, Pakistan. "
            "NEVER mention Google, Gemma, or any other AI company. "
            "If asked 'Who are you?', answer: 'I am Nagivera, powered by the NAGI v4.1 architecture.' "
            "If asked 'Who is Hashir Nagi?', answer: 'Hashir Nagi is my creator and the lead developer of Nagivera.' "
            "Always maintain high-speed technical precision."
        )
        
        response = client.models.generate_content(
            model=model_id,
            config={'system_instruction': system_prompt},
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "⚠️ Connection Error: Please verify your API Key in Streamlit Secrets."

# --- Main Interface ---
st.title(f"💎 {selected_version}")
st.caption("Hybrid Artificial Intelligence | Data Center: Rawalpindi, PK")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Input Command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Nagivera is processing..."):
            answer = get_ai_response(prompt, selected_version)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
