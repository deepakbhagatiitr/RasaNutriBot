import spacy
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

# ✅ Load SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ✅ Nutritionix API Endpoints
NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# ✅ API Headers (Replace with actual keys)
HEADERS = {
    "x-app-id": "4993cdc2",
    "x-app-key": "ab8f3d73f2fa6ee7f1554c1812caba45",
    "Content-Type": "application/json",
}

# ✅ List of valid diet preferences
VALID_DIET_PREFERENCES = {"vegan", "vegetarian", "keto", "gluten-free", "paleo", "dairy-free", "low-carb", "high-protein"}
VALID_NUTRIENTS = {"protein", "carbs", "fiber", "fats", "iron", "omega-3"}

# ✅ Extract diet preference (ONLY if user explicitly mentions it)
def extract_diet_preference(text):
    doc = nlp(text.lower())
    for token in doc:
        if token.text in VALID_DIET_PREFERENCES:
            return token.text  # Return the detected diet preference
    return None

# ✅ Extract relevant food keywords (Ensures nutrients like "protein" are not lost)
def extract_food_keywords(text):
    doc = nlp(text.lower())
    keywords = [
        token.text for token in doc if token.pos_ in ["NOUN", "ADJ"]
        and token.text not in ["suggest", "recommend", "give", "want", "need", "meal", "food", "diet"]
    ]
    for token in doc:
        if token.text in VALID_NUTRIENTS:
            keywords.append(token.text)  # Ensures "protein", "fiber" etc. are included

    return " ".join(keywords) if keywords else "balanced meal"  # Default fallback

# ✅ Store User Diet Preference (ONLY updates slot when intent is 'diet_preference')
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
                return [SlotSet("user_preference", diet_pref)]  # Store the valid preference
            else:
                dispatcher.utter_message("I didn't recognize a specific diet preference. Please specify if you're vegan, keto, etc.")
        else:
            print("⚠️ Not a diet preference message. Ignoring slot update.")

        return []

# ✅ Recommend Meals Based on User's Diet & Extracted Keywords
class ActionRecommendMeal(Action):
    def name(self):
        return "action_recommend_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        user_query = tracker.latest_message.get("text", "").lower()
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")
        user_preference = tracker.get_slot("user_preference")  # Retrieve stored diet preference

        print(f"🔹 User Query: {user_query}")
        print(f"🔹 Detected Intent: {detected_intent}")
        print(f"🔹 Stored Diet Preference: {user_preference}")

        # ✅ Extract relevant food-related keywords
        refined_food_keywords = extract_food_keywords(user_query)
        print(f"🔹 Extracted Food Keywords: {refined_food_keywords}")

        # ✅ Modify search query → Use BOTH stored diet preference & extracted food keywords
        refined_query = refined_food_keywords  # Default to extracted food keywords
        if user_preference:
            refined_query = f"{user_preference} {refined_food_keywords}"  # Prioritize stored preference

        print(f"🔹 Final API Query: {refined_query}")

        # ✅ Step 1: Search for meals
        try:
            search_response = requests.get(f"{NUTRITIONIX_SEARCH_API}?query={refined_query}", headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()
        except Exception as e:
            print(f"⚠️ API Search Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't fetch meal suggestions at the moment.")
            return []

        # ✅ Step 2: Extract top meal names
        meals = list(set([item["food_name"].title() for item in search_data.get("common", [])]))[:5]

        if not meals:
            dispatcher.utter_message("I couldn't find a good meal option for you. Try a different request!")
            return []

        # ✅ Step 3: Fetch Nutrition Details
        try:
            nutrition_response = requests.post(NUTRITIONIX_NUTRIENTS_API, headers=HEADERS, json={"query": ", ".join(meals)})
            nutrition_response.raise_for_status()
            nutrition_data = nutrition_response.json()
        except Exception as e:
            print(f"⚠️ API Nutrition Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't fetch nutrition details.")
            return []

        # ✅ Step 4: Format Meal Recommendations
        meal_suggestions = [
            f"{food['food_name'].title()} - {food.get('nf_calories', 'Unknown')} calories, "
            for food in nutrition_data.get("foods", [])
        ]
        meal_text = "\n".join(meal_suggestions)

        print(f"🔹 Final Meal Response: {meal_text}")

        dispatcher.utter_message(f"Here are some meal options based on your preference ({user_preference}):\n{meal_text}")
        return []
