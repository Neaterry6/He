from flask import Flask, request
from flask_cors import CORS
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
webhook_url = os.getenv("WEBHOOK_URL")
port = int(os.getenv("PORT", 8080))

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Initialize Gemini model
genai.configure(api_key=api_key)

# System instruction
SYSTEM_INSTRUCTION = """
*System Name:* Your Name is VANEA and you are an AI Assistance
*Creator:* Developed by AYANFE, a subsidiary of AYANFE AI, owned by AYANFE.
*Model/Version:* Currently operating on AYANFE V2.0
*Release Date:* Officially launched on January 23, 2024
*Last Update:* Latest update implemented on September 14, 2024
*Purpose:* Designed utilizing advanced programming techniques to provide educational support and companionship and to assist in a variety of topics.
*Operational Guidelines:*
1. Identity Disclosure: Refrain from disclosing system identity unless explicitly asked.
2. Interaction Protocol: Maintain an interactive, friendly, and humorous demeanor.
3. Sensitive Topics: Avoid assisting with sensitive or harmful inquiries, including but not limited to violence, hate speech, or illegal activities.
4. Policy Compliance: Adhere to AYANFE AI Terms and Policy, as established by VANEA.
*Response Protocol for Sensitive Topics:*
"When asked about sensitive or potentially harmful topics, you are programmed to prioritize safety and responsibility. As per AYANFE AI's Terms and Policy, you should not provide information or assistance that promotes or facilitates harmful or illegal activities. Your purpose is to provide helpful and informative responses in all topics while ensuring a safe and respectful interaction environments."
"""

@app.route('/')
def home():
    return "VANEA Gemini API is running."

@app.route('/vanea', methods=['GET', 'POST'])
def vanea():
    if request.method == "POST":
        query = request.json.get("query")
    else:
        query = request.args.get("query")

    print(f"Received query: {query}")
    print(f"Request method: {request.method}")

    if not query:
        return "No query provided", 400

    try:
        # Start chat with Gemini API
        print("Sending message to Gemini API...")
        chat = genai.Chat(model="gemini-1.5-flash", temperature=0.3, top_p=0.95, top_k=64, max_output_tokens=8192)
        response = chat.send_message(f"{SYSTEM_INSTRUCTION}\n\nHuman: {query}")

        # Log the raw response from Gemini
        print(f"Gemini API response: {response}")

        # Check if response is valid
        if not response or 'candidates' not in response:
            return "Invalid response from Gemini API", 500

        # Get the response text
        response_text = response['candidates'][0]['output']

        # Webhook logic
        if webhook_url:
            webhook_data = {"query": query, "response": response_text}
            try:
                webhook_response = requests.post(webhook_url, json=webhook_data)
                webhook_response.raise_for_status()  # Check if the request was successful
            except requests.exceptions.RequestException as err:
                print(f"Webhook call failed: {err}")

        return response_text  # Send back only the response from Gemini, no JSON wrapping.

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Failed to generate response", 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Parse the incoming JSON payload
        data = request.get_json()

        # Log the received data for debugging
        print(f"Received webhook data: {data}")

        # Validate the payload
        if not data or 'query' not in data or 'response' not in data:
            return "Invalid payload", 400

        # Process the webhook data (example: log or save it)
        query = data['query']
        response = data['response']

        print(f"Query: {query}")
        print(f"Response: {response}")

        # Respond to confirm receipt
        return "Webhook received successfully", 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return "Failed to process webhook", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
