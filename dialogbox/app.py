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


load_dotenv()


nlp = spacy.load("en_core_web_sm")
nltk.download("punkt")
classifier = pipeline("zero-shot-classification")


tf_model = tf.keras.models.Sequential()  
torch_model = torch.nn.Linear(10, 1)  
label_encoder = LabelEncoder()


NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"


HEADERS = {
    "x-app-id": os.getenv("NUTRITIONIX_APP_ID"),
    "x-app-key": os.getenv("NUTRITIONIX_API_KEY"),
    "Content-Type": "application/json",
}


RASA_URL = "http://localhost:5005/webhooks/rest/webhook"


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_meal_suggestions(query):
    """Fetch dynamic meal recommendations from Nutritionix API"""
    try:
        
        search_query = f"healthy {query} meal"

        
        search_response = requests.get(
            f"{NUTRITIONIX_SEARCH_API}?query={search_query}",
            headers=HEADERS
        )
        search_response.raise_for_status()
        search_data = search_response.json()

        
        meals = [
            item["food_name"].title() 
            for item in search_data.get("common", []) 
            if not any(
                excluded in item["food_name"].lower() 
                for excluded in ["mcnugget", "fast food", "burger", "fries"]
            )
        ][:3]  

        if not meals:
            return ["No healthy meals found. Try a different query!"]

        
        nutrition_response = requests.post(
            NUTRITIONIX_NUTRIENTS_API,
            headers=HEADERS,
            json={"query": ", ".join(meals)}  
        )
        nutrition_response.raise_for_status()
        nutrition_data = nutrition_response.json()

        
        meal_suggestions = [
            f"{food['food_name'].title()} - {food.get('nf_calories', 'Unknown')} calories"
            for food in nutrition_data.get("foods", [])
        ]

        return meal_suggestions if meal_suggestions else ["No nutritional info available."]
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API Request Error: {e}")
        return ["Sorry, we couldn't fetch meal suggestions right now."]
    
    except Exception as e:
        print(f"⚠️ Unexpected Error: {e}")
        return ["An error occurred while fetching meal data. Please try again later."]

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

    
    rasa_response = get_rasa_response(user_query)

    
    if any(keyword in user_query.lower() for keyword in ["meal", "food", "diet", "nutrition"]):
        
        meal_suggestions = get_meal_suggestions(user_query)

        
        meal_text = "\n".join(meal_suggestions)

        
        if rasa_response.strip():  
            rasa_response += f"\nHere are some healthy meal options:\n{meal_text}"
        else:
            rasa_response = f"Here are some healthy meal options:\n{meal_text}"  

    return jsonify({"fulfillmentText": rasa_response})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
