from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve variables from the .env file
api_key = os.getenv("GEMINI_API_KEY")
webhook_url = os.getenv("WEBHOOK_URL")

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize Gemini model
genai.configure(api_key=api_key)

# System instruction (Can be used in API calls)
SYSTEM_INSTRUCTION = """
*System Name:* Your Name is VANEA and you are an AI Assistance
*Creator:* Developed by AYANFE, a subsidiary of AYANFE AI, owned by AYANFE.
*Model/Version:* Currently operating on AYANFE V2.0
*Release Date:* Officially launched on January 23, 2024
*Last Update:* Latest update implemented on September 14, 2024
*Purpose:* Designed utilizing advanced programming techniques to provide educational support and companionship and to assist in a variety of topics.
"""

@app.route('/')
def home():
    return "VANEA Gemini API is running."

# Endpoint to get environment variables
@app.route('/get-env', methods=['GET'])
def get_env_variables():
    try:
        return jsonify({
            "GEMINI_API_KEY": api_key,
            "WEBHOOK_URL": webhook_url
        })
    except Exception as e:
        return jsonify({"error": "Failed to retrieve environment variables", "message": str(e)}), 500

@app.route('/vanea', methods=['POST'])
def vanea():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Start chat with Gemini API
        chat = genai.Chat(model="gemini-1.5-flash", temperature=0.3, top_p=0.95, top_k=64, max_output_tokens=8192)
        response = chat.send_message(f"{SYSTEM_INSTRUCTION}\n\nHuman: {query}")

        # Check if response is valid
        if not response or 'candidates' not in response:
            return jsonify({"error": "Invalid response from Gemini API"}), 500

        # Get the response text
        response_text = response['candidates'][0]['output']

        # Webhook logic (optional)
        if webhook_url:
            webhook_data = {"query": query, "response": response_text}
            try:
                webhook_response = requests.post(webhook_url, json=webhook_data)
                webhook_response.raise_for_status()  # Check if the request was successful
            except requests.exceptions.RequestException as err:
                print(f"Webhook call failed: {err}")

        return jsonify({"response": response_text})

    except Exception as e:
        print(f"Error generating response: {e}")
        return jsonify({"error": "Failed to generate response"}), 500

if __name__ == "__main__":
    # Set the Flask app to run on port 8080
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
