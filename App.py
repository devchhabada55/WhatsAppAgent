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

# Twilio will hit this endpoint
WEBHOOK_PATH = "/whatsapp"

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")   # lightweight + fast

# Company Info (for branding in answers)
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
    """Send customer query to Gemini and get smart response."""
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
    from_number = request.form.get("From")

    resp = MessagingResponse()
    msg = resp.message()

    # First-time greeting
    if incoming_msg.lower() in ["hi", "hello", "start"]:
        msg.body(WELCOME_MESSAGE)
    else:
        # Ask Gemini for smart response
        reply = ask_gemini(incoming_msg)
        msg.body(reply)

    return str(resp)

# -----------------------------
#  RUN LOCALLY
# -----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

