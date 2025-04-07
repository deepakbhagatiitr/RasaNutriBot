import os
import json
import requests
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from sklearn.preprocessing import LabelEncoder


# Rasa Chatbot API URL
RASA_URL = "https://rasa-server-842373618484.us-central1.run.app/webhooks/rest/webhook"
# https://rasa-server-842373618484.us-central1.run.app
# Flask App Initialization
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for cross-origin requests


def get_rasa_response(user_message):
    """
    Sends user input to the Rasa chatbot and retrieves the chatbot's response.

    Args:
        user_message (str): The user's query.

    Returns:
        str: The chatbot's response message.
    """
    try:
        rasa_response = requests.post(RASA_URL, json={"sender": "user", "message": user_message})
        if rasa_response.status_code == 200:
            responses = rasa_response.json()
            if responses and isinstance(responses, list) and "text" in responses[0]:
                return responses[0]["text"]
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Rasa API Error: {e}")  # Log error to console
    return ""  

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Handles incoming user requests via a webhook and returns appropriate responses.

    Returns:
        JSON: Response with fulfillment text.
    """
    req = request.get_json()
    user_query = req.get("queryResult", {}).get("queryText", "").strip()

    if not user_query:
        return jsonify({"fulfillmentText": "Invalid request. No user message received."})

    # ✅ Step 1: Get chatbot response from Rasa
    rasa_response = get_rasa_response(user_query)

    # ✅ Step 2: Check if Rasa already provided meal recommendations
    if "Here are some meal options:" in rasa_response:
        return jsonify({"fulfillmentText": rasa_response})  # Avoid duplicate API calls

    return jsonify({"fulfillmentText": rasa_response})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
