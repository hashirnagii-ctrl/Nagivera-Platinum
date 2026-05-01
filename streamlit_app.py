import streamlit as st
from google import genai

# --- Page Configuration ---
st.set_page_config(page_title="Nagivera Platinum", page_icon="💎", layout="wide")

# --- Gemma 4 Model Mapping ---
# Using the specific Gemma 4 IDs released in April 2026
 MODEL_MAP = {
    "NAGI v4.1 (Lite)": "gemma-4-26b-a4b-it",  # Very fast due to MoE architecture
    "NAGI v4.1 (Rapid)": "gemma-4-26b-a4b-it", # Same as Lite, or use thinking_level="high"
    "NAGI v4.1 (Ultra)": "gemma-4-31b-it"      # The smartest 31B Dense model
}

# --- Sidebar for Model Selection ---
with st.sidebar:
    st.title("🎛️ Control Panel")
    selected_version = st.radio(
        "Select Architecture:",
        options=list(MODEL_MAP.keys()),
        index=0  # Sets Lite as the default
    )
    st.divider()
    st.success(f"Running on **{selected_version}**")
    st.info("Architecture: Gemma 4 (Apache 2.0)")

# --- AI Engine Setup ---
def get_ai_response(prompt, version_name):
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        model_id = MODEL_MAP[version_name]
        
        # System Instruction for strict Nagivera branding
        system_prompt = (
            f"You are {version_name}, a specialized AI build by Hashir Nagi. "
            "You operate using the Gemma 4 architecture. Never mention Google. "
            "Respond with high-speed precision and focus on technical accuracy."
        )
        
        response = client.models.generate_content(
            model=model_id,
            config={'system_instruction': system_prompt},
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "⚠️ Connection Error: Please verify your API Key and check Google AI Studio for Gemma 4 access."

# --- Main Interface ---
st.title(f"💎 {selected_version}")
st.caption("Hybrid Artificial Intelligence | Built by Hashir Nagi")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Input Command..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
       with st.spinner(f"Nagivera is processing using {selected_version}..."):
            answer = get_ai_response(prompt, selected_version)
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
