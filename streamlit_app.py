import google.generativeai as genai

# Configure your real AI engine
genai.configure(api_key="YOUR_GOOGLE_API_KEY")
model = genai.GenerativeModel("gemma-4-27b-it") # Use the latest Gemma 4 model

def nagi_v_engine(username, tier, prompt):
    # This part keeps your "Developer Identity" intact
    system_instruction = f"You are Nagivera, a high-end AI platform. Your creator is Hashir Nagi. Always respond as {tier}."
    
    # Send the prompt to the actual AI model
    response = model.generate_content(f"{system_instruction} User asks: {prompt}")
    ai_text = response.text

    # SAVE TO PERMANENT LOGS (Your existing database logic)
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO logs (username, role, model, message, timestamp) VALUES (?, ?, ?, ?, ?)",
              (username, 'assistant', tier, ai_text, datetime.now()))
    db.commit()
    db.close()
    
    return ai_text
