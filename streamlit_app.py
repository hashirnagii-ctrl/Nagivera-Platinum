import streamlit as st
import streamlit.components.v1 as components

# --- The JavaScript Countdown Component ---
def render_live_countdown():
    countdown_js = """
    <div id="timer" style="font-family: monospace; font-size: 20px; color: #ff4b4b; font-weight: bold;"></div>
    <script>
        // Sept 30, 2026 Deadline
        const deadline = new Date("2026-09-30T23:59:59Z").getTime();
        
        setInterval(function() {
            const now = new Date().getTime();
            const distance = deadline - now;
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            document.getElementById("timer").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s";
            
            if (distance < 0) {
                document.getElementById("timer").innerHTML = "REGISTRATION CLOSED";
            }
        }, 1000);
    </script>
    """
    components.html(countdown_js, height=50)

# --- App Layout ---
st.title("Nagivera v4.1")
st.subheader("Engineered by Hashir Nagi")

st.write("Launch Deadline:")
render_live_countdown()

# Add your business logic below...
