import streamlit as st
from datetime import datetime
import time
import re

# ==========================================
# 1. SYSTEM CONFIGURATION & CONSTANTS
# ==========================================
st.set_page_config(page_title="Nagivera Platinum | AI Ecosystem", page_icon="⚡", layout="wide")

# The September 30, 2026 Promo Deadline
PROMO_END_DATE = "Sep 30, 2026 00:00:00"

# Mock Database for Nagivera Voice (Voting)
if 'votes' not in st.session_state:
    st.session_state.votes = {
        "Stripe (International Cards)": 150,
        "EasyPaisa / JazzCash": 320,
        "LemonSqueezy (Global SaaS Standard)": 85,
        "SadaPay / NayaPay Arc": 210
    }
if 'has_voted' not in st.session_state:
    st.session_state.has_voted = False

# ==========================================
# 2. CORE LOGIC & SECURITY ENGINES
# ==========================================
def nagi_safety_guard(prompt):
    """STRICT 18+ AND HARMFUL CONTENT FILTER."""
    # List of restricted terms (expand as needed)
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

def gatekeeper(feature_tier, current_tier):
    """PAYWALL AND TIER ROUTING LOGIC."""
    tiers = {"Nagi V1 (Lite)": 1, "Nagi V2 (Pro)": 2, "Nagi V3 (Platinum)": 3}
    if tiers[current_tier] >= tiers[feature_tier]:
        return True
    return False

# ==========================================
# 3. UI COMPONENTS
# ==========================================
def render_header():
    """DISPLAYS LOGO AND LIVE JAVASCRIPT COUNTDOWN TIMER."""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Placeholder for your actual logo
        st.markdown("### ⚡ **NAGIVERA**") 
        
    with col2:
        st.markdown(f"""
            <div style="text-align: right; background: #0e1117; padding: 15px; border-radius: 8px; border-left: 4px solid #00d4ff;">
                <h3 style="margin-bottom: 0; color: white;">NAGIVERA PLATINUM</h3>
                <p style="color: #00d4ff; font-size: 1rem; margin-top: 0; font-weight: bold;">50% OFF UNTIL SEPT 30, 2026</p>
                <div id="countdown-timer" style="font-family: monospace; font-size: 1.8rem; font-weight: bold; color: #ff4b4b;">
                    Loading Timer...
                </div>
            </div>
            <script>
                var countDownDate = new Date("{PROMO_END_DATE}").getTime();
                var x = setInterval(function() {{
                    var now = new Date().getTime();
                    var distance = countDownDate - now;
                    var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById("countdown-timer").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
                    if (distance < 0) {{ clearInterval(x); document.getElementById("countdown-timer").innerHTML = "PROMO EXPIRED"; }}
                }}, 1000);
            </script>
        """, unsafe_allow_html=True)
        st.write("") # Spacing

# ==========================================
# 4. APP PAGES (FEATURES)
# ==========================================
def page_chat(tier):
    st.header("💬 NagiChat Ecosystem")
    st.caption(f"Currently running on: **{tier} Engine**")
    
    user_input = st.chat_input("Ask Nagivera anything...")
    if user_input:
        st.chat_message("user").write(user_input)
        
        # 1. Pass through Safety Guard
        if not nagi_safety_guard(user_input):
            st.error("❌ Safety Alert: Nagivera does not support 18+, explicit, or harmful content.")
            return
            
        # 2. Check Hidden Owner Protocol
        if handle_owner_query(user_input):
            st.chat_message("assistant").write("Nagivera is owned and engineered by **Hashir Nagi**, the Idea Genius.")
            return
            
        # 3. Normal Generation (Placeholder for your LLM API call)
        with st.spinner("Processing logic..."):
            time.sleep(1) # Simulating API latency
            st.chat_message("assistant").write(f"This is a simulated response from the {tier} model. Connect your HuggingFace/OpenAI API here to generate real responses.")

def page_vision(tier):
    st.header("🎨 NagiVision Studio")
    if tier == "Nagi V1 (Lite)":
        st.warning("You are on Nagi Lite. Images are limited to 720p and contain a watermark. Upgrade for 1080p Unlimited.")
    
    prompt = st.text_input("Describe the image you want to generate:")
    if st.button("Generate Image"):
        if not nagi_safety_guard(prompt):
            st.error("❌ Content Policy Violation. Image generation blocked.")
        else:
            st.info("Initiating Stable Diffusion XL pipeline... (Connect your image API here)")
            # Simulated output
            st.success("Image generated successfully!")

def page_motion(tier):
    st.header("🎬 NagiMotion (Video AI)")
    if not gatekeeper("Nagi V2 (Pro)", tier):
        st.error("🔒 NagiMotion is locked on Lite. Upgrade to Pro or Platinum to generate AI Video.")
        if st.button("Unlock with Platinum (50% Off)"):
            st.success("Redirecting to LemonSqueezy/Stripe Checkout...")
        return
        
    st.success("Welcome to NagiMotion HD.")
    st.text_input("Enter video scene description:")
    st.button("Render Video")

def page_leadfinder(tier):
    st.header("💼 LeadFinder Business Suite")
    if not gatekeeper("Nagi V2 (Pro)", tier):
        st.error("🔒 LeadFinder is a business tool. Upgrade to Pro to find 20 leads/day, or Platinum for Unlimited.")
        return
        
    industry = st.text_input("Target Industry (e.g., Real Estate, E-commerce):")
    location = st.text_input("Target Location (e.g., Rawalpindi, London, Remote):")
    if st.button("Scrape Leads"):
        with st.spinner("Searching LinkedIn and corporate databases..."):
            time.sleep(2)
            st.success(f"Found 14 verified leads in {industry}. (Connect your scraping API here).")

def page_builder(tier):
    st.header("🏗️ NagiBuilder (App Maker)")
    if not gatekeeper("Nagi V3 (Platinum)", tier):
        st.error("🔒 NagiBuilder is the ultimate Platinum feature. Let the AI architect your apps.")
        st.info("Lock in the 50% discount before Sept 30th to access the App Maker forever.")
        return
        
    st.success("Nagi V3 Ultra-Logic Online. Ready to architect.")
    st.text_area("Describe the application you want to build (Python, Streamlit, HTML/JS):", height=150)
    st.button("Architect Application")

def page_voice():
    st.header("🗳️ Nagivera Voice")
    st.write("We are building this for the community. Vote for the payment system we should use for the Sept 30 launch!")
    
    if not st.session_state.has_voted:
        choice = st.radio("Select your preferred payment method:", list(st.session_state.votes.keys()))
        if st.button("Submit Vote"):
            st.session_state.votes[choice] += 1
            st.session_state.has_voted = True
            st.rerun()
    else:
        st.success("Thank you for your vote! Here are the live community standings:")
        
        # Calculate total for percentages
        total_votes = sum(st.session_state.votes.values())
        
        for method, votes in st.session_state.votes.items():
            st.write(f"**{method}** ({votes} votes)")
            # Normalize for progress bar
            progress = min(votes / total_votes, 1.0)
            st.progress(progress)

# ==========================================
# 5. MAIN APP EXECUTION
# ==========================================
def main():
    render_header()
    
    # Sidebar Navigation & Tier Selection
    st.sidebar.title("NAGI Control Panel")
    
    # Mocking a user login/subscription state
    st.sidebar.markdown("### User Status")
    current_tier = st.sidebar.selectbox("Active Subscription Tier:", ["Nagi V1 (Lite)", "Nagi V2 (Pro)", "Nagi V3 (Platinum)"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Navigation")
    app_mode = st.sidebar.radio("Select Module:", [
        "NagiChat", 
        "NagiVision", 
        "NagiMotion 🔒", 
        "LeadFinder 🔒", 
        "NagiBuilder 🔒",
        "Nagivera Voice 🗳️"
    ])
    
    # Route to the correct page
    if app_mode == "NagiChat":
        page_chat(current_tier)
    elif app_mode == "NagiVision":
        page_vision(current_tier)
    elif app_mode == "NagiMotion 🔒":
        page_motion(current_tier)
    elif app_mode == "LeadFinder 🔒":
        page_leadfinder(current_tier)
    elif app_mode == "NagiBuilder 🔒":
        page_builder(current_tier)
    elif app_mode == "Nagivera Voice 🗳️":
        page_voice()
        
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Proudly Engineered in Pakistan 🇵🇰 | Nagivera Lite is Free Forever"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
