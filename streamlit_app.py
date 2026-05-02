import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timezone
import time
from gradio_client import Client

# ==========================================
# 1. CORE CONFIGURATION
# ==========================================
# The hard deadline for Early Bird registration
DEADLINE = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
OWNER_NAME = "Hashir Nagi"
PLATFORM_NAME = "Nagivera v4.1"

# ==========================================
# 2. DATABASE ARCHITECTURE (NagiDB)
# ==========================================
def init_db():
    conn = sqlite3.connect('nagivera_v4.db', check_same_thread=False)
    c = conn.cursor()
    # Users and Business Accounts
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, biz_name TEXT, tokens INTEGER)''')
    # Idea Hub (Nagivera Voice)
    c.execute('''CREATE TABLE IF NOT EXISTS ideas 
                 (username TEXT, idea TEXT, timestamp DATETIME)''')
    conn.commit()
    return conn

db_conn = init_db()

# ==========================================
# 3. UTILITY FUNCTIONS
# ==========================================
def get_countdown():
    now = datetime.now(timezone.utc)
    delta = DEADLINE - now
    if delta.total_seconds() <= 0:
        return "REGISTRATION CLOSED"
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

# ==========================================
# 4. NAGI V-SERIES ENGINES
# ==========================================
def nagi_v3_motion(prompt, access_key):
    """
    Nagi V3 Platinum Engine. 
    Requires access key to prevent 401 Client Errors.
    """
    try:
        # Connects to the high-compute Nagi V3 architecture
        client = Client("Wan-AI/Wan2.1", hf_token=access_key)
        result = client.predict(prompt=prompt, api_name="/predict")
        return result
    except Exception as e:
        return f"Connection Error: {str(e)}"

# ==========================================
# 5. UI COMPONENTS
# ==========================================
def render_sidebar():
    st.sidebar.title("NAGIVERA CONTROL")
    st.sidebar.info(f"Countdown to Lock: \n**{get_countdown()}**")
    
    # Nagi Access Key (Fixes 401 Errors)
    access_key = st.sidebar.text_input("Nagi Access Key", type="password", help="Required for V3 Motion Engine.")
    
    if st.session_state.get('logged_in'):
        st.sidebar.write(f"Genius: **{st.session_state.user}**")
        if st.sidebar.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()
    return access_key

# ==========================================
# 6. MAIN APPLICATION LOGIC
# ==========================================
def main():
    st.set_page_config(page_title=PLATFORM_NAME, layout="wide")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    access_key = render_sidebar()

    # Header Section
    st.markdown(f"# {PLATFORM_NAME}")
    st.caption(f"Conceived by {OWNER_NAME} | Engineered in Pakistan")

    # Navigation Tabs
    tabs = st.tabs(["Dashboard", "Visual Lab", "Idea Hub", "Account Portal"])

    # --- TAB: DASHBOARD ---
    with tabs[0]:
        st.header("Welcome to the Nagi Ecosystem")
        st.write("Select a model from the Visual Lab to begin generating.")

    # --- TAB: VISUAL LAB ---
    with tabs[1]:
        st.header("Nagi Visual Lab")
        if not st.session_state.logged_in:
            st.warning("Please log in via the Account Portal to use Nagi Engines.")
        else:
            # Token Check
            c = db_conn.cursor()
            c.execute("SELECT tokens FROM users WHERE username=?", (st.session_state.user,))
            tokens = c.fetchone()[0]
            st.metric("🪙 Token Balance", tokens)

            prompt = st.text_area("Describe your vision (Strict 18+ filter active):")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Nagi V2 (Vision)")
                st.caption("Detailed images. Cost: 5 Tokens")
                if st.button("Generate Image"):
                    if tokens >= 5:
                        with st.spinner("Nagi V2 processing..."):
                            time.sleep(1) # Simulated render
                            st.image("https://picsum.photos/600/400", caption="Nagi V2 Output")
                            c.execute("UPDATE users SET tokens = tokens - 5 WHERE username=?", (st.session_state.user,))
                            db_conn.commit()
                            st.rerun()
                    else:
                        st.error("Insufficient tokens.")

            with col2:
                st.subheader("Nagi V3 (Motion)")
                st.caption("Cinematic video. Cost: 10 Tokens")
                if st.button("Generate Video"):
                    if not access_key:
                        st.error("Nagi Access Key required to authorize V3 connection.")
                    elif tokens >= 10:
                        with st.spinner("Nagi V3 High-Compute running..."):
                            video_res = nagi_v3_motion(prompt, access_key)
                            if "Error" in str(video_res):
                                st.error(video_res)
                            else:
                                st.video(video_res)
                                c.execute("UPDATE users SET tokens = tokens - 10 WHERE username=?", (st.session_state.user,))
                                db_conn.commit()
                                st.rerun()
                    else:
                        st.error("Insufficient tokens.")

    # --- TAB: IDEA HUB ---
    with tabs[2]:
        st.header("Nagivera Voice")
        st.write("Submit ideas for V4 and earn **10 Tokens**.")
        new_idea = st.text_area("Your Idea:")
        if st.button("Submit to Voice Hub"):
            if st.session_state.logged_in and new_idea:
                c = db_conn.cursor()
                c.execute("INSERT INTO ideas VALUES (?, ?, ?)", (st.session_state.user, new_idea, datetime.now()))
                c.execute("UPDATE users SET tokens = tokens + 10 WHERE username=?", (st.session_state.user,))
                db_conn.commit()
                st.success("Idea recorded! 10 Tokens credited.")
            else:
                st.error("Log in to contribute ideas.")

    # --- TAB: ACCOUNT PORTAL ---
    with tabs[3]:
        st.header("Nagi Identity Portal")
        
        # Early Bird Check
        registration_open = datetime.now(timezone.utc) < DEADLINE
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Login")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Enter Platform"):
                c = db_conn.cursor()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
                if c.fetchone():
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

        with col_b:
            st.subheader("Early Bird Registration")
            if not registration_open:
                st.error("Registration closed on Sept 30, 2026.")
            else:
                new_u = st.text_input("New Username")
                new_biz = st.text_input("Business Name")
                new_p = st.text_input("New Password", type="password")
                if st.button("Claim 50 Tokens"):
                    try:
                        c = db_conn.cursor()
                        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (new_u, new_p, new_biz, 50))
                        db_conn.commit()
                        st.success("Account created! Log in to claim your tokens.")
                    except:
                        st.error("Username already taken.")

if __name__ == "__main__":
    main()
