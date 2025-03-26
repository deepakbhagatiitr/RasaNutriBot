import spacy
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import random  

FOLLOW_UP_RESPONSES = [
    "Do you have any dietary preferences? 🍽️ (e.g., vegan, keto) Let me know so I can tailor my recommendations!",
    "What kind of meals do you prefer?"
]

nlp = spacy.load("en_core_web_sm")

NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"

HEADERS = {
    "x-app-id": "4993cdc2",
    "x-app-key": "ab8f3d73f2fa6ee7f1554c1812caba45",
    "Content-Type": "application/json",
}

VALID_DIET_PREFERENCES = {
    "vegan", "vegetarian", "keto", "gluten-free", "paleo",
    "dairy-free", "low-carb", "high-protein", "weight-loss"
}

VALID_NUTRIENTS = {"protein", "carbs", "fiber", "fats", "iron", "omega-3"}

def extract_diet_preference(text):
    doc = nlp(text.lower())
    for token in doc:
        if token.text in VALID_DIET_PREFERENCES:
            return token.text  
    return None

def extract_food_keywords(text):
    """Extract relevant food-related keywords using NLP with better filtering."""
    doc = nlp(text.lower())  
    
    stop_words = {"suggest", "recommend", "give", "want", "need", "meal", "food", "foods", "diet", 
                  "some", "for", "me", "to", "a", "the", "that", "which"}
    
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "ADJ"] and token.text not in stop_words]

    text_lower = text.lower()
    if "weight loss" in text_lower or "weight-loss" in text_lower:
     keywords = ["low calorie"]  
    elif "weight gain" in text_lower or "weight-gain" in text_lower:
     keywords = ["high calorie"]  
    return " ".join(set(keywords)) if keywords else "healthy meal"  

class ActionStoreUserPreference(Action):
    def name(self):
        return "action_store_user_preference"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_message = tracker.latest_message.get("text", "").lower()
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")

        print(f"🔹 User Message: {user_message}")
        print(f"🔹 Detected Intent: {detected_intent}")

        if detected_intent == "diet_preference":
            diet_pref = extract_diet_preference(user_message)
            print(f"🔹 Extracted Diet Preference: {diet_pref}")

            if diet_pref:
                dispatcher.utter_message(f"Got it! You prefer {diet_pref}. I'll suggest meals accordingly.")
                return [SlotSet("user_preference", diet_pref)]  
            else:
                dispatcher.utter_message("I didn't recognize a specific diet preference. Please specify if you're vegan, keto, etc.")
        else:
            print("⚠️ Not a diet preference message. Ignoring slot update.")

        return []

class ActionRecommendMeal(Action):
    def name(self):
        return "action_recommend_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_query = tracker.latest_message.get("text", "").lower()
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")
        user_preference = tracker.get_slot("user_preference")  

        print(f"🔹 User Query: {user_query}")
        print(f"🔹 Detected Intent: {detected_intent}")
        print(f"🔹 Stored Diet Preference: {user_preference}")

        
        refined_food_keywords = extract_food_keywords(user_query)
        print(f"🔹 Extracted Food Keywords: {refined_food_keywords}")

        
        refined_query = refined_food_keywords  
        if user_preference:
            refined_query = f"{user_preference} {refined_food_keywords}"  

        print(f"🔹 Final API Query: {refined_query}")

        
        try:
            search_response = requests.get(f"{NUTRITIONIX_SEARCH_API}?query={refined_query}", headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()
        except Exception as e:
            print(f"⚠️ API Search Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't fetch meal suggestions at the moment.")
            return []

        meals = list(set([item["food_name"].title() for item in search_data.get("common", [])]))[:5]

        if not meals:
            dispatcher.utter_message("I’m not sure about that food item. Can you specify more details?")
            return []

        try:
            nutrition_response = requests.post(NUTRITIONIX_NUTRIENTS_API, headers=HEADERS, json={"query": ", ".join(meals)})
            nutrition_response.raise_for_status()
            nutrition_data = nutrition_response.json()
        except Exception as e:
            print(f"⚠️ API Nutrition Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't fetch nutrition details.")
            return []

        excluded_items = {
        "protein", "carbs", "fiber", "fats", "iron", "omega-3", "sodium", "sugar",  
        
        }

        seen_meals = set()  
        meal_suggestions = []

        for food in nutrition_data.get("foods", []):
            meal_name = food["food_name"].title()
            
            
            if meal_name.lower() in excluded_items:
                continue  

            meal_entry = f"{meal_name} - {food.get('nf_calories', 'Unknown')} calories"
            
            if meal_name not in seen_meals:  
                seen_meals.add(meal_name)
                meal_suggestions.append(meal_entry)

        meal_text = "\n".join(meal_suggestions)  
        follow_up_responses = [
                    "Do you have any dietary preferences? 🍽️ (e.g., vegan, keto) Let me know so I can tailor my recommendations!",
                    "What kind of meals do you prefer?"
                ]
        follow_up_message = random.choice(follow_up_responses) if not user_preference else None

        full_response = f"Here are some meal options:\n{meal_text}"
        if follow_up_message:
            full_response += f"\n{follow_up_message}"  # ✅ Append follow-up message correctly

        print(f"🔹 Final Response Sent to Frontend:\n{full_response}")  # ✅ Debugging step
        dispatcher.utter_message(text=full_response)  # ✅ Ensure text is explicitly passed
        return []

class ActionHandleFeedback(Action):
    def name(self):
        return "action_handle_feedback"

    def run(self, dispatcher, tracker, domain):
        feedback = tracker.get_slot("feedback_type")

        if feedback == "positive":
            dispatcher.utter_message("I'm glad you liked it! Let me know if you need more recommendations.")
        elif feedback == "negative":
            dispatcher.utter_message("I'm sorry you didn't enjoy it. Would you like another suggestion?")
        else:
            dispatcher.utter_message("Thanks for your feedback! It helps me to improve.")
        return []