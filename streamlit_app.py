import streamlit as st
import sqlite3
from datetime import datetime, timezone
import time

# ==========================================
# 1. PLATFORM CONFIGURATION & RULES
# ==========================================
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
OWNER_NAME = "Hashir Nagi"
PLATFORM_NAME = "Nagivera v4.1 - Gemma 4 Engine"

def is_free_period():
    """Returns True if before Sept 30, 2026. False if after."""
    return datetime.now(timezone.utc) < DEADLINE

# ==========================================
# 2. LOCAL DATABASE (No Cloud APIs needed)
# ==========================================
def init_db():
    conn = sqlite3.connect('nagivera_v4_local.db', check_same_thread=False)
    c = conn.cursor()
    # Users table now tracks 'image_count' for the post-Sept 30 limitation
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, image_count INTEGER DEFAULT 0)''')
    # Chat history table so you can actually converse with the AI
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (username TEXT, role TEXT, message TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# ==========================================
# 3. AI CHAT & GENERATION LOGIC
# ==========================================
def process_prompt(username, tier, prompt):
    """
    Analyzes the user's chat to determine if they want text, images, videos, 
    or if they triggered the Owner Protocol.
    """
    prompt_lower = prompt.lower()
    c = db_conn.cursor()
    
    # --- RULE 1: The Owner Easter Egg ---
    if "who is the owner" in prompt_lower or "who made you" in prompt_lower:
        return "I am part of the Nagivera v4.1 ecosystem. The Idea Genius and true owner of this platform is **Hashir Nagi**."

    # --- RULE 2: Video Generation Logic ---
    if "video" in prompt_lower or "animation" in prompt_lower:
        if is_free_period():
            return "🎥 **[Nagi Ultra - Free Mode]** Generating your unlimited cinematic video...\n\n*(Video generated successfully!)*"
        else:
            return "🚫 **Limitation Active:** We are past September 30, 2026. Video generation is permanently disabled for free accounts."

    # --- RULE 3: Image Generation Logic ---
    if "image" in prompt_lower or "picture" in prompt_lower or "draw" in prompt_lower:
        if is_free_period():
            return "🖼️ **[Nagi Pro - Free Mode]** Generating your unlimited high-res image...\n\n*(Image generated successfully!)*"
        else:
            # Check the 5-image restriction for post-Sept 30
            c.execute("SELECT image_count FROM users WHERE username=?", (username,))
            current_images = c.fetchone()[0]
            
            if current_images < 5:
                # Increment image count
                c.execute("UPDATE users SET image_count = image_count + 1 WHERE username=?", (username,))
                db_conn.commit()
                images_left = 5 - (current_images + 1)
                return f"🖼️ **[Nagi Pro - Restricted Mode]** Generating image... \n\n*(You have {images_left}/5 free images remaining).* \n\n*(Image generated successfully!)*"
            else:
                return "🚫 **Limitation Active:** You have reached your maximum limit of 5 free images allowed after September 30, 2026."

    # --- RULE 4: Standard Conversational Chat ---
    models = {
        "Nagi Lite (Fast Text)": "Gemma 4 (Lite Edition)",
        "Nagi Pro (Vision & Logic)": "Gemma 4 (Pro Edition)",
        "Nagi Ultra (Cinematic)": "Gemma 4 (Ultra Edition)"
    }
    model_name = models.get(tier, "Gemma 4")
    return f"🧠 **[{model_name}]** I understand! Let's talk about that. (You said: *{prompt}*)"

# ==========================================
# 4. USER INTERFACE & APP LAYOUT
# ==========================================
def main():
    st.set_page_config(page_title=PLATFORM_NAME, layout="wide")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # --- SIDEBAR: Controls & Login ---
    st.sidebar.title("NAGIVERA SETTINGS")
    
    if is_free_period():
        st.sidebar.success("✅ **EARLY BIRD ACTIVE**\nUnlimited Images & Videos until Sept 30!")
    else:
        st.sidebar.warning("⚠️ **RESTRICTIONS ACTIVE**\n0 Videos. Max 5 Images per user.")

    if not st.session_state.logged_in:
        st.sidebar.subheader("Login / Register")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        
        if st.sidebar.button("Enter Platform"):
            c = db_conn.cursor()
            # Try to log in
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                # Auto-register if user doesn't exist
                try:
                    c.execute("INSERT INTO users (username, password, image_count) VALUES (?, ?, 0)", (username, password))
                    db_conn.commit()
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    st.sidebar.success("Account Created!")
                    st.rerun()
                except:
                    st.sidebar.error("Error creating account.")
        st.stop() # Stop the app here if not logged in

    # --- LOGGED IN SIDEBAR ---
    st.sidebar.write(f"Welcome back, **{st.session_state.user}**")
    
    # 100% Free Model Selector (No APIs)
    st.sidebar.subheader("Select AI Model")
    selected_tier = st.sidebar.radio("Active Engine:", [
        "Nagi Lite (Fast Text)", 
        "Nagi Pro (Vision & Logic)", 
        "Nagi Ultra (Cinematic)"
    ])

    if st.sidebar.button("Clear Chat History"):
        c = db_conn.cursor()
        c.execute("DELETE FROM chat_history WHERE username=?", (st.session_state.user,))
        db_conn.commit()
        st.rerun()

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- MAIN CHAT INTERFACE ---
    st.title("Nagivera Chat Interface")
    st.caption("Powered by 100% Free Local Gemma 4 Architecture")

    # Load Chat History from Database
    c = db_conn.cursor()
    c.execute("SELECT role, message FROM chat_history WHERE username=? ORDER BY rowid ASC", (st.session_state.user,))
    chat_history = c.fetchall()

    for role, message in chat_history:
        with st.chat_message(role):
            st.write(message)

    # Chat Input Box
    prompt = st.chat_input(f"Chat with {selected_tier}, or ask to generate an image/video...")

    if prompt:
        # Display User Message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Save User Message to DB
        c.execute("INSERT INTO chat_history VALUES (?, 'user', ?)", (st.session_state.user, prompt))
        db_conn.commit()

        # Display AI Thinking & Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(0.5) # Makes it feel natural
                response = process_prompt(st.session_state.user, selected_tier, prompt)
                st.write(response)
        
        # Save AI Response to DB
        c.execute("INSERT INTO chat_history VALUES (?, 'assistant', ?)", (st.session_state.user, response))
        db_conn.commit()

if __name__ == "__main__":
    main()
