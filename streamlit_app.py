import streamlit as st
import sqlite3
import datetime
import time
from gradio_client import Client # For accessing free community models

# --- CONFIGURATION & DATABASE ---
deadline = datetime.datetime(2026, 9, 30, 0, 0, 0)
MODELS = {
    "Nagi V1 (Lite)": "Text & Logic",
    "Nagi V2 (Pro)": "High-Res Image (FLUX/SDXL)",
    "Nagi V3 (Platinum)": "Cinematic Video (Kling/Wan 2.2)"
}

conn = sqlite3.connect('nagivera_v4.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY, username TEXT, tokens INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS ideas 
             (id INTEGER PRIMARY KEY, content TEXT, rewarded INTEGER)''')
conn.commit()

# --- STYLING & UI ---
st.set_page_config(page_title="Nagivera v4.1", layout="wide")

# Live Countdown Timer (JavaScript)
timer_js = f"""
<div id="nagivera-timer" style="text-align:center; font-size:24px; font-weight:bold; color:#ff4b4b; padding:10px; border:2px solid #ff4b4b; border-radius:10px; margin-bottom:20px;">
    Nagivera Launch Countdown: <span id="time"></span>
</div>
<script>
var countDownDate = new Date("{deadline.strftime('%b %d, %Y %H:%M:%S')}").getTime();
var x = setInterval(function() {{
  var now = new Date().getTime();
  var distance = countDownDate - now;
  var days = Math.floor(distance / (1000 * 60 * 60 * 24));
  var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  var seconds = Math.floor((distance % (1000 * 60)) / 1000);
  document.getElementById("time").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
  if (distance < 0) {{
    clearInterval(x);
    document.getElementById("time").innerHTML = "NAGIVERA IS LIVE";
  }}
}}, 1000);
</script>
"""

# --- SIDEBAR & AUTH ---
st.sidebar.image("https://via.placeholder.com/150?text=NAGIVERA+LOGO", width=150) # Replace with your logo URL
st.sidebar.title("NAGIVERA v4.1")
username = st.sidebar.text_input("Username", value="Guest")

# Initialize User
c.execute("SELECT tokens FROM users WHERE username=?", (username,))
user_data = c.fetchone()
if not user_data:
    c.execute("INSERT INTO users (username, tokens) VALUES (?, ?)", (username, 50))
    conn.commit()
    tokens = 50
else:
    tokens = user_data[0]

st.sidebar.write(f"🪙 **Tokens:** {tokens}")

# --- MAIN INTERFACE ---
st.components.v1.html(timer_js, height=100)

menu = ["NagiChat", "NagiMotion (Video)", "NagiVision (Image)", "Community Voice"]
choice = st.sidebar.selectbox("Navigate", menu)

# --- MODEL INTEGRATIONS ---

def generate_video(prompt):
    # This uses a public Gradio space for Kling/Wan 2.2 models often available for free in 2026
    try:
        # Example using the Wan 2.2 Community Space (Free Tier)
        client = Client("Wan-AI/Wan2.1-T2V-720P") 
        result = client.predict(
            prompt=prompt,
            negative_prompt="low quality, blurry, 18+, unsafe",
            api_name="/predict"
        )
        return result # Path to video
    except Exception as e:
        return f"Error connecting to free generator: {e}"

# --- APP LOGIC ---

if choice == "NagiMotion (Video)":
    st.header("🎬 Nagi V3 (Platinum) Video Generator")
    st.warning("⚠️ THIS GENERATOR IS ONLY FOR BEFORE 30TH SEP AFTER THAT IT WILL BE REMOVED")
    
    prompt = st.text_area("Describe your video (Strict 18+ filter active):")
    if st.button("Generate Video (Cost: 10 Tokens)"):
        if tokens >= 10:
            if prompt:
                with st.spinner("Calling Kling/Wan AI Engines..."):
                    video_path = generate_video(prompt)
                    if "Error" not in video_path:
                        st.video(video_path)
                        tokens -= 10
                        c.execute("UPDATE users SET tokens=? WHERE username=?", (tokens, username))
                        conn.commit()
                    else:
                        st.error(video_path)
            else:
                st.error("Please enter a prompt.")
        else:
            st.error("Insufficient Tokens! Submit an idea in Community Voice to earn more.")

elif choice == "Community Voice":
    st.header("💡 Nagivera Voice")
    st.write("Submit features you want to see. Earn **10 Tokens** for every idea submitted!")
    new_idea = st.text_input("Your Idea:")
    if st.button("Submit Idea"):
        if new_idea:
            c.execute("INSERT INTO ideas (content, rewarded) VALUES (?, 1)", (new_idea,))
            c.execute("UPDATE users SET tokens = tokens + 10 WHERE username=?", (username,))
            conn.commit()
            st.success("Idea submitted! 10 Tokens added to your account.")
            st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("Nagivera v4.1 | Developed for the future of AI. All rights reserved until 2026.")
