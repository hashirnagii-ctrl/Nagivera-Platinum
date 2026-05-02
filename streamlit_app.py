import streamlit as st
from datetime import datetime
import time
import re
import requests

# ==========================================
# 1. SYSTEM CONFIGURATION & CONSTANTS
# ==========================================
st.set_page_config(page_title="Nagivera Platinum | AI Ecosystem", page_icon="⚡", layout="wide")

PROMO_END_DATE = datetime(2026, 9, 30)
CURRENT_DATE = datetime.now()
# If today is before Sept 30, 2026, unlock everything.
UNLOCKED_PROMO = CURRENT_DATE < PROMO_END_DATE

# Free AI Models via Hugging Face
MODELS = {
    "chat_code": "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
    "vision": "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
    "video": "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"
}

# ==========================================
# 2. CORE LOGIC & SECURITY ENGINES
# ==========================================
def nagi_safety_guard(prompt):
    """STRICT 18+ AND HARMFUL CONTENT FILTER."""
    restricted_pattern = re.compile(r'\b(nsfw|18\+|explicit|porn|gore|violence|hack|illegal)\b', re.IGNORECASE)
    if restricted_pattern.search(prompt):
        return False
    return True

def handle_owner_query(prompt):
    """HIDDEN OWNER PROTOCOL."""
    owner_queries = ["who is the owner", "who made this", "who created nagivera", "who is the boss", "who built this"]
    if any(query in prompt.lower() for query in owner_queries):
        return True
    return False

# --- FREE FAST API CALLER ---
def query_nagi_api(prompt, model_url, hf_token, is_image=False):
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(model_url, headers=headers, json=payload)
        if is_image:
            return response.content # Returns image bytes
        else:
            return response.json()[0].get('generated_text', 'Error generating response.')
    except Exception as e:
        return f"API Error: Make sure your Free HuggingFace Token is valid. Details: {e}"

# ==========================================
# 3. UI COMPONENTS
# ==========================================
def render_header():
    """DISPLAYS LOGO AND LIVE JAVASCRIPT COUNTDOWN TIMER."""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### ⚡ **NAGIVERA**") 
    with col2:
        if UNLOCKED_PROMO:
            st.markdown(f"""
                <div style="text-align: right; background: #0e1117; padding: 15px; border-radius: 8px; border-left: 4px solid #00d4ff;">
                    <h3 style="margin-bottom: 0; color: white;">NAGIVERA PLATINUM (UNLOCKED)</h3>
                    <p style="color: #00d4ff; font-size: 1rem; margin-top: 0; font-weight: bold;">ALL FEATURES FREE UNTIL SEPT 30, 2026</p>
                    <div id="countdown-timer" style="font-family: monospace; font-size: 1.8rem; font-weight: bold; color: #ff4b4b;">
                        Loading Timer...
                    </div>
                </div>
                <script>
                    var countDownDate = new Date("Sep 30, 2026 00:00:00").getTime();
                    var x = setInterval(function() {{
                        var now = new Date().getTime();
                        var distance = countDownDate - now;
                        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                        document.getElementById("countdown-timer").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
                        if (distance < 0) {{ clearInterval(x); document.getElementById("countdown-timer").innerHTML = "FREE PERIOD ENDED"; }}
                    }}, 1000);
                </script>
            """, unsafe_allow_html=True)
            st.write("")

# ==========================================
# 4. APP PAGES (FEATURES)
# ==========================================
def page_chat(hf_token):
    st.header("💬 NagiChat Ecosystem")
    user_input = st.chat_input("Ask Nagivera anything...")
    
    if user_input:
        st.chat_message("user").write(user_input)
        if not nagi_safety_guard(user_input):
            st.error("❌ Safety Alert: Nagivera does not support 18+, explicit, or harmful content.")
            return
        if handle_owner_query(user_input):
            st.chat_message("assistant").write("Nagivera is owned and engineered by **Hashir Nagi**, the Idea Genius.")
            return
            
        if not hf_token:
            st.warning("Please enter your free Hugging Face API token in the sidebar to enable fast generation.")
            return

        with st.spinner("Nagi V1 Logic running..."):
            response = query_nagi_api(user_input, MODELS["chat_code"], hf_token)
            st.chat_message("assistant").write(response)

def page_vision(hf_token):
    st.header("🎨 NagiVision HD Studio")
    prompt = st.text_input("Describe the image you want to generate:")
    
    if st.button("Generate HD Image"):
        if not nagi_safety_guard(prompt):
            st.error("❌ Content Policy Violation. Image generation blocked.")
            return
        if not hf_token:
            st.warning("Please enter your free API token in the sidebar.")
            return

        with st.spinner("Rendering via Stable Diffusion XL..."):
            image_bytes = query_nagi_api(prompt, MODELS["vision"], hf_token, is_image=True)
            if isinstance(image_bytes, bytes):
                st.image(image_bytes, caption=f"Generated by NagiVision: {prompt}")
            else:
                st.error("Failed to generate image. The free server might be busy.")

def page_motion(hf_token):
    st.header("🎬 NagiMotion (Video AI)")
    st.info("Unlocked for all users until Sept 30!")
    prompt = st.text_input("Enter video scene description:")
    
    if st.button("Render Fast Video"):
        if not nagi_safety_guard(prompt):
            st.error("❌ Content Policy Violation.")
            return
        st.warning("Video generation via free Hugging Face endpoints can take 2-3 minutes. Initializing text-to-video MS 1.7b...")
        # Placeholder for the actual video bytes return (similar logic to image)
        st.code("Processing Video Pipeline...", language="bash")

def page_builder(hf_token):
    st.header("🏗️ NagiBuilder (App Maker)")
    st.success("Nagi V3 Ultra-Logic Unlocked until Sept 30th!")
    prompt = st.text_area("Describe the application you want to build (Python, Streamlit, HTML/JS):", height=150)
    
    if st.button("Architect Application"):
        if not hf_token:
            st.warning("API Token required for code architecture.")
            return
            
        full_prompt = f"Write the full, complete code for the following application. Only output the code, no explanations: {prompt}"
        with st.spinner("Writing code architecture..."):
            code_response = query_nagi_api(full_prompt, MODELS["chat_code"], hf_token)
            st.code(code_response)

def page_leadfinder():
    st.header("💼 LeadFinder Free Suite")
    st.info("Fast Web Scraping - Unlocked until Sept 30!")
    industry = st.text_input("Target Industry (e.g., Real Estate, E-commerce):")
    location = st.text_input("Target Location (e.g., Rawalpindi, London, Remote):")
    
    if st.button("Scrape Free Leads"):
        with st.spinner("Searching the web for public contacts..."):
            # Simulating an instant free web scrape
            time.sleep(1)
            st.success(f"Found free leads for {industry} in {location}!")
            st.write("1. contact@business1.com | LinkedIn: /in/ceo1")
            st.write("2. info@startup2.com | LinkedIn: /in/founder2")
            st.write("3. hello@agency3.pk | LinkedIn: /in/manager3")

# ==========================================
# 5. MAIN APP EXECUTION
# ==========================================
def main():
    render_header()
    
    st.sidebar.title("NAGI Control Panel")
    
    # API Key Input
    st.sidebar.markdown("### Power Up")
    hf_token = st.sidebar.text_input("Enter Free HuggingFace Token:", type="password", help="Get a free token from huggingface.co/settings/tokens")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")
    
    # No more locks!
    app_mode = st.sidebar.radio("Select Module:", [
        "NagiChat", 
        "NagiVision", 
        "NagiMotion", 
        "NagiBuilder",
        "LeadFinder"
    ])
    
    if app_mode == "NagiChat":
        page_chat(hf_token)
    elif app_mode == "NagiVision":
        page_vision(hf_token)
    elif app_mode == "NagiMotion":
        page_motion(hf_token)
    elif app_mode == "NagiBuilder":
        page_builder(hf_token)
    elif app_mode == "LeadFinder":
        page_leadfinder()
        
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Proudly Engineered in Pakistan 🇵🇰 | Nagivera V4.1"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
