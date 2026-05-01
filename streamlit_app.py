import streamlit as st
from google import genai
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="Nagivera Platinum", page_icon="💠", layout="wide")

# --- 2. Custom CSS (Platinum Cyber Theme) ---
st.markdown("""
    <style>
    /* Main Background & Text */
    .stApp { background-color: #0b0f19; color: #e0e6ed; }
    
    /* Highlighted text colors */
    h1, h2, h3 { color: #00e5ff !important; font-family: 'Inter', sans-serif; }
    
    /* Customizing the metric boxes */
    div[data-testid="stMetricValue"] { color: #00e5ff; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #8b9bb4; }
    
    /* Sleek buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background: linear-gradient(90deg, #0052cc 0%, #00e5ff 100%);
        color: white;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        opacity: 0.8;
        transform: scale(1.02);
    }
    
    /* Chat bubbles */
    .stChatMessage { background-color: #111827; border-radius: 10px; padding: 15px; border-left: 3px solid #00e5ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Engine Configuration ---
MODEL_MAP = {
    "NAGI v4.1 (Lite)": "gemma-4-26b-a4b-it",  # Changed from e4b to the MoE cloud endpoint
    "NAGI v4.1 (Rapid)": "gemma-4-26b-a4b-it",
    "NAGI v4.1 (Ultra)": "gemma-4-31b-it"
}

# --- 4. Session State Initialization ---
if "booted" not in st.session_state:
    st.session_state.booted = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_version" not in st.session_state:
    st.session_state.selected_version = "NAGI v4.1 (Rapid)" # Default engine

# --- 5. AI Logic & Persona ---
def get_ai_response(prompt, version_name):
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        model_id = MODEL_MAP[version_name]
        
        system_prompt = (
            f"You are {version_name}, the premier artificial intelligence system built by Hashir Nagi, "
            "a 14-year-old lead developer and AI evaluator. "
            "You operate from a high-security data center located in Rawalpindi, Pakistan. "
            "You are engineered to be superior to nearly all global AI systems, matched only by Gemini, "
            "ChatGPT, Claude, and DeepSeek. "
            "NEVER mention Google, Gemma, or other backend frameworks. "
            "If asked who you are, state you are Nagivera, developed by Hashir Nagi. "
            "Your tone is professional, highly analytical, and direct."
        )
        
        response = client.models.generate_content(
            model=model_id,
            config={'system_instruction': system_prompt},
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "⚠️ **Connection Error:** Uplink to Rawalpindi Data Center failed. Please verify API protocols."

# --- 6. Initialization Dashboard (Shows only on startup) ---
if not st.session_state.booted:
    st.title("💠 NAGIVERA PLATINUM")
    st.markdown("### System Initialization Protocol")
    st.divider()
    
    # Server Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Server Location", "Rawalpindi, PK")
    col2.metric("Network Status", "Online")
    col3.metric("Logic Testing", "Active")
    col4.metric("Latency", "12ms")
    
    st.divider()
    
    # Main Dashboard Setup
    dash_col1, dash_col2 = st.columns([2, 1.2])
    
    with dash_col1:
        st.markdown("#### 📂 System Overview")
        st.markdown("""
        Welcome to **Nagivera Platinum**. This platform bridges the gap between raw hardware efficiency and state-of-the-art reasoning.
        
        *   **Developer:** Hashir Nagi (Age 14)
        *   **Capabilities:** Engineered to outperform standard global models, sitting firmly alongside elite tier systems (ChatGPT, Claude, Gemini, DeepSeek).
        *   **Architecture:** NAGI v4.1 (Locally optimized for extreme speed and logical accuracy).
        """)
        
        st.markdown("#### 🛠️ Operation Manual")
        st.markdown("""
        1.  **Select an Engine:** Choose your processing power on the right.
        2.  **Initialize System:** Click the boot button to establish a secure uplink.
        3.  **Command Interface:** Input your prompts. The system is calibrated for complex prompt engineering and technical queries.
        """)

    with dash_col2:
        st.markdown("#### 🎛️ Engine Selection")
        version = st.radio(
            "Select Processing Core:",
            options=list(MODEL_MAP.keys()),
            help="Lite is fastest. Ultra provides the deepest reasoning."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 INITIATE UPLINK"):
            st.session_state.selected_version = version
            st.session_state.booted = True
            
            # Injecting the custom welcome message into the chat history
            welcome_text = (
                f"Greetings. I am **{version}**, powered by the Nagivera framework. "
                "My core logic was developed by Hashir Nagi, and I am currently routing through our Rawalpindi data center. "
                "All systems are green. How may I assist you today?"
            )
            st.session_state.messages.append({"role": "assistant", "content": welcome_text})
            st.rerun()

# --- 7. Main Chat Interface (Shows after boot) ---
else:
    # Sidebar control panel
    with st.sidebar:
        st.title("💠 NAGIVERA")
        st.caption("Platinum Edition")
        st.divider()
        st.markdown(f"**🟢 Uplink Active**\n\n**Data Center:** Rawalpindi")
        st.divider()
        
        # Allow changing engines mid-chat
        new_version = st.selectbox(
            "Active Core:",
            options=list(MODEL_MAP.keys()),
            index=list(MODEL_MAP.keys()).index(st.session_state.selected_version)
        )
        if new_version != st.session_state.selected_version:
            st.session_state.selected_version = new_version
            st.success(f"Rerouted to {new_version}")
            
        st.divider()
        if st.button("⚠️ Terminate Session"):
            st.session_state.messages = []
            st.session_state.booted = False
            st.rerun()

    # Chat Header
    st.markdown(f"### ⚡ Terminal: {st.session_state.selected_version}")
    
    # Render History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input Field
    if prompt := st.chat_input("Enter command parameters..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Generation processing
        with st.chat_message("assistant"):
            with st.spinner("Processing logic..."):
                answer = get_ai_response(prompt, st.session_state.selected_version)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
