from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
webhook_url = os.getenv("WEBHOOK_URL")

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Check if the API key is missing and initialize Gemini if present
if not api_key:
    print("Error: GEMINI_API_KEY is missing!")
else:
    genai.configure(api_key=api_key)

# System instruction for Gemini API
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
"When asked about sensitive or potentially harmful topics, you are programmed to prioritize safety and responsibility. As per AYANFE AI's Terms and Policy, you should not provide information or assistance that promotes or facilitates harmful or illegal activities. Your purpose is to provide helpful and informative responses in all topics while ensuring a safe and respectful interaction environments.Operational Guidelines:Information Accuracy: KORA AI strives provide accurate response in variety of topics.
"""

@app.route('/vanea', methods=['POST', 'GET'])
def vanea():
    # Debug: Log request method and incoming data
    print(f"Request Method: {request.method}")
    
    if request.method == "POST":
        query = request.json.get("query")
    else:
        query = request.args.get("query")

    print(f"Received query: {query}")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Start chat with Gemini API
        print("Sending message to Gemini API...")
        chat = genai.Chat(model="gemini-1.5-flash", temperature=0.3, top_p=0.95, top_k=64, max_output_tokens=8192)
        response = chat.send_message(f"{SYSTEM_INSTRUCTION}\n\nHuman: {query}")

        # Debug: Print the response
        print(f"Gemini API response: {response}")

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

# Ensure the app is only running when the script is executed directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True
