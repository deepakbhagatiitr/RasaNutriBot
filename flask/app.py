import os
import json
import requests
import spacy
import nltk
import torch
import tensorflow as tf
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from dotenv import load_dotenv
from sklearn.preprocessing import LabelEncoder

# Load environment variables
load_dotenv()



# Load ML Models (Placeholder)
tf_model = tf.keras.models.Sequential()
torch_model = torch.nn.Linear(10, 1)
label_encoder = LabelEncoder()

# Nutritionix API Endpoints
NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# API Headers
HEADERS = {
    "x-app-id": os.getenv("NUTRITIONIX_APP_ID"),
    "x-app-key": os.getenv("NUTRITIONIX_API_KEY"),
    "Content-Type": "application/json",
}

# Rasa Chatbot API URL
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

# Flask App
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def extract_food_keywords(text):
    """Extract relevant food-related keywords from user query using NLP"""
    doc = nlp(text.lower())  # Process query using spaCy NLP model
    
    # ✅ Define stop words to ignore
    stop_words = {"suggest", "meal", "diet", "food", "recommend", "want", "give", "a", "for", "me", "to", "some"}
    
    # ✅ Extract only meaningful food-related words (NOUNS & ADJECTIVES)
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "ADJ"] and token.text not in stop_words]
    
    return " ".join(keywords) if keywords else "high protein meal"  # Default fallback

def get_meal_suggestions(query):
    """Fetch dynamic meal recommendations from Nutritionix API"""
    try:
        # ✅ Extract relevant food keywords
        refined_query = extract_food_keywords(query)

        # ✅ Step 1: Search for relevant meals
        search_response = requests.get(
            f"{NUTRITIONIX_SEARCH_API}?query={refined_query}",
            headers=HEADERS
        )
        search_response.raise_for_status()
        search_data = search_response.json()

        # ✅ Step 2: Extract **only meal-related items** (No drinks, snacks)
        meals = list(set([
            item["food_name"].title()
            for item in search_data.get("common", [])
            if "drink" not in item["food_name"].lower() and
               "soda" not in item["food_name"].lower() and
               "whiskey" not in item["food_name"].lower() and
               "coke" not in item["food_name"].lower()
        ]))[:5]  # Get exactly 5 meal suggestions

        if not meals:
            return ["No suitable meals found. Try specifying a different query."]

        # ✅ Step 3: Fetch nutrition details for the **5 meals**
        nutrition_response = requests.post(
            NUTRITIONIX_NUTRIENTS_API,
            headers=HEADERS,
            json={"query": ", ".join(meals)}
        )
        nutrition_response.raise_for_status()
        nutrition_data = nutrition_response.json()

        # ✅ Step 4: Extract meal names and calories, removing duplicates
        seen = set()  # To track unique meals
        meal_suggestions = []
        
        for food in nutrition_data.get("foods", []):
            meal_name = food["food_name"].title()
            calories = food.get("nf_calories", "Unknown")
            meal_entry = f"{meal_name} - {calories} calories"

            if meal_entry not in seen:  # Avoid duplicate meals
                meal_suggestions.append(meal_entry)
                seen.add(meal_entry)

        return meal_suggestions if meal_suggestions else ["No nutritional info available."]
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API Error: {e}")
        return ["Error fetching meal data. Please try again later."]

def get_rasa_response(user_message):
    """Send user input to Rasa chatbot and get response"""
    try:
        rasa_response = requests.post(RASA_URL, json={"sender": "user", "message": user_message})
        if rasa_response.status_code == 200:
            responses = rasa_response.json()
            if responses and isinstance(responses, list) and "text" in responses[0]:
                return responses[0]["text"]
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Rasa API Error: {e}")
    return ""  

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming user requests and respond accordingly"""
    req = request.get_json()
    user_query = req.get("queryResult", {}).get("queryText", "").strip()

    if not user_query:
        return jsonify({"fulfillmentText": "Invalid request. No user message received."})

    # ✅ Step 1: Get Rasa response
    rasa_response = get_rasa_response(user_query)

    # ✅ Step 2: Check if Rasa already provided meal recommendations
    if "Here are some meal options:" in rasa_response:
        return jsonify({"fulfillmentText": rasa_response})  # Avoid duplicate calls

    # ✅ Step 3: Check if the user asked about meals, food, or diet
    # if any(keyword in user_query.lower() for keyword in ["meal", "food", "diet", "nutrition"]):
    #     meal_suggestions = get_meal_suggestions(user_query)
    #     meal_text = "\n".join(meal_suggestions)

    #     # ✅ Ensure "Here are some healthy meal options:" appears only once
    #     if "Here are some healthy meal options:" in rasa_response:
    #         rasa_response = rasa_response.replace("Here are some healthy meal options:", "").strip()

    #     # ✅ Format response to avoid duplication
    #     if rasa_response.strip():
    #         rasa_response += f"\nHere are some healthy meal options:\n{meal_text}"
    #     else:
    #         rasa_response = f"Here are some healthy meal options:\n{meal_text}"

    return jsonify({"fulfillmentText": rasa_response})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
