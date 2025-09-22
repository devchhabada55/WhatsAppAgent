from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -----------------------------
#  CONFIGURATION
# -----------------------------
app = Flask(__name__)

WEBHOOK_PATH = "/whatsapp"

# Gemini API setup (from env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")  # lightweight + fast

COMPANY_NAME = "Mahaveer Securities"
COMPANY_SERVICES = """
- Stock Market Advisory 📈
- Mutual Fund Guidance 💹
- Portfolio Management 🏦
- 24x7 Financial Assistance 🕐
- Investment & Retirement Planning 💼
"""

WELCOME_MESSAGE = f"""
👋 Welcome to {COMPANY_NAME}!

I’m your 24×7 Financial Assistant 🤖.  
You can ask me about:
- Stock market updates 📊
- Mutual funds 💹
- Investment advice 💼
- Our services and offers 🎯

How may I assist you today?
"""

# -----------------------------
#  GEMINI FUNCTION
# -----------------------------
def ask_gemini(user_message):
    prompt = f"""
You are the official AI assistant for {COMPANY_NAME}.
Your role is:
1. Provide financial insights, guidance, and explain terms clearly.
2. Act as a marketing agent: promote company services where relevant.
3. Be polite, professional, and available 24x7.
4. Never give illegal or financial-guarantee advice. Keep it safe.

Company Services:
{COMPANY_SERVICES}

User asked:
{user_message}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Sorry, I couldn’t process that request. Error: {str(e)}"

# -----------------------------
#  TWILIO WEBHOOK
# -----------------------------
@app.route(WEBHOOK_PATH, methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.lower() in ["hi", "hello", "start"]:
        msg.body(WELCOME_MESSAGE)
    else:
        reply = ask_gemini(incoming_msg)
        msg.body(reply)

    return str(resp)

# -----------------------------
#  RUN ON RENDER
# -----------------------------
if __name__ == "__main__":
    # Render dynamically sets the PORT environment variable
    port = int(os.getenv("PORT", 5000))  # default 5000 for local testing
    debug = os.getenv("DEBUG", "True").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
