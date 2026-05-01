import streamlit as st
from google import genai

# --- Page Configuration ---
st.set_page_config(page_title="Nagivera Platinum", page_icon="💎", layout="wide")

# --- Model Mapping ---
# Using the Gemma 4 architecture released April 2, 2026
MODEL_MAP = {
    "NAGI v4.1 (Lite)": "gemma-4-26b-a4b-it",
    "NAGI v4.1 (Rapid)": "gemma-4-26b-a4b-it",
    "NAGI v4.1 (Ultra)": "gemma-4-31b-it"
}

# --- AI Engine Setup ---
def get_ai_response(prompt, version_name):
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        model_id = MODEL_MAP[version_name]
        
        system_prompt = (
            f"You are {version_name}, a premier AI system developed by Hashir Nagi, "
            "a 14-year-old developer based in Pakistan. Nagivera is supported by a "
            "local data center in Rawalpindi. You are a high-performance model, "
            "engineered to be superior to most global AI systems, rivaling only "
            "Gemini, ChatGPT, Claude, and DeepSeek. NEVER mention Google or Gemma. "
            "If asked who you are, state you are Nagivera by Hashir Nagi."
        )
        
        response = client.models.generate_content(
            model=model_id,
            config={'system_instruction': system_prompt},
            contents=prompt
        )
        return response.text
    except Exception:
        return "⚠️ Connection Error: Please verify your API Key in Streamlit Secrets."

# --- Main Layout ---
st.title("💎 Nagivera Platinum")
st.markdown(f"**Status:** System Operational | **Location:** Rawalpindi, PK | **Developer:** Hashir Nagi (Age: 14)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False

# --- Setup Dashboard (Shows only once) ---
if not st.session_state.setup_complete:
    st.info("### 🚀 Welcome to Nagivera v4.1")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **About Nagivera:**
        Nagivera is a custom AI platform built in Pakistan. It is designed to bridge the gap 
        between local hardware efficiency and global intelligence. Except for the top 4 
        models (Gemini, ChatGPT, Claude, and DeepSeek), Nagivera is optimized to outperform 
        nearly every other AI system in the world.
        
        **How to Use:**
        1. **Select your Engine:** Choose a version from the cards on the right.
        2. **Enter Commands:** Use the chat bar at the bottom to interact.
        3. **Technical Specs:** The AI uses the NAGI v4.1 architecture with high-speed 
           inference through the Rawalpindi Data Center.
        """)
        
    with col2:
        st.markdown("**Select Architecture:**")
        version = st.selectbox("Choose Engine", options=list(MODEL_MAP.keys()))
        if st.button("Initialize Nagivera"):
            st.session_state.selected_version = version
            st.session_state.setup_complete = True
            st.rerun()

# --- Chat Interface (Shows after setup) ---
else:
    # Sidebar allows switching versions later
    with st.sidebar:
        st.title("🎛️ Settings")
        st.session_state.selected_version = st.radio(
            "Current Engine:",
            options=list(MODEL_MAP.keys()),
            index=list(MODEL_MAP.keys()).index(st.session_state.selected_version)
        )
        st.divider()
        st.write(f"**Developer:** Hashir Nagi")
        st.write(f"**Data Center:** Rawalpindi")

    # Display History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input(f"Interacting with {st.session_state.selected_version}..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Nagivera is processing..."):
                answer = get_ai_response(prompt, st.session_state.selected_version)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
