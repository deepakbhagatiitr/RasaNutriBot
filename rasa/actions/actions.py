import spacy
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import random  

# Follow-up responses for user engagement
FOLLOW_UP_RESPONSES = [
    "Do you have any dietary preferences? 🍽️ (e.g., vegan, keto) Let me know so I can tailor my recommendations!",
    "What kind of meals do you prefer?"
]

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Nutritionix API URLs
NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# API Headers
HEADERS = {
    "x-app-id": "4993cdc2",
    "x-app-key": "ab8f3d73f2fa6ee7f1554c1812caba45",
    "Content-Type": "application/json",
}

# Valid diet preferences
VALID_DIET_PREFERENCES = {
    "vegan", "vegetarian", "keto", "gluten-free", "paleo",
    "dairy-free", "low-carb", "high-protein", "weight-loss"
}

def extract_diet_preference(text):
    """Extract diet preference from user message using phrase matching.

    Args:
        text (str): User input message containing dietary preferences.

    Returns:
        str or None: Detected diet preference if found; otherwise, None.
    """
    doc = nlp(text.lower())  # Convert input text to lowercase for consistency

    # Check for exact phrase matches within the predefined diet preferences
    for diet in VALID_DIET_PREFERENCES:
        if diet in text.lower():  # Match the diet keyword in the user's message
            return diet  # Return the detected diet preference

    return None  # No valid diet preference found



def extract_food_keywords(text):
    """Extract relevant food-related keywords using NLP with better filtering.

    Args:
        text (str): User input message containing food-related requests.

    Returns:
        str: Extracted keywords for food recommendations or a default fallback.
    """
    doc = nlp(text.lower())  # Convert input text to lowercase for consistency

    # Define a set of stop words to ignore (common, non-food-related words)
    stop_words = {
        "suggest", "recommend", "give", "want", "need", "meal", "food", "foods", "diet",
        "some", "for", "me", "to", "a", "the", "that", "which"
    }

    # Extract meaningful food-related words (NOUNS & ADJECTIVES) while ignoring stop words
    keywords = [token.text for token in doc if token.pos_ in ["NOUN", "ADJ"] and token.text not in stop_words]

    # Handle specific cases for weight-related goals
    text_lower = text.lower()
    if "weight loss" in text_lower or "weight-loss" in text_lower:
        keywords = ["low calorie"]  # Prioritize low-calorie options for weight loss
    elif "weight gain" in text_lower or "weight-gain" in text_lower:
        keywords = ["high calorie"]  # Prioritize high-calorie options for weight gain

    # Return extracted keywords (removing duplicates) or a default fallback
    return " ".join(set(keywords)) if keywords else "healthy meal"



class ActionStoreUserPreference(Action):
    
    """Stores the user's diet preference and triggers meal recommendations."""

    def name(self):
        """Returns the action name."""
        return "action_store_user_preference"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        """Extracts and stores user diet preferences, then suggests meals."""
        user_message = tracker.latest_message.get("text", "").lower()
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")

        print(f"🔹 User Message: {user_message}")
        print(f"🔹 Detected Intent: {detected_intent}")

        if detected_intent == "diet_preference":
            diet_pref = extract_diet_preference(user_message)
            print(f"🔹 Extracted Diet Preference: {diet_pref}")

            if diet_pref:
                # Store preference in slot
                user_preference_slot = SlotSet("user_preference", diet_pref)

                # Trigger meal recommendation action
                meal_recommendation = TriggerActionMeal().run(dispatcher, tracker, domain)

                # Send a combined response to avoid multiple frontend messages
                dispatcher.utter_message(text=f"Got it! You prefer {diet_pref}. I'll suggest meals accordingly.\n{meal_recommendation}")

                return [user_preference_slot]  # Update slot with user preference

            else:
                dispatcher.utter_message("I couldn't recognize a diet preference. Are you vegan, keto, etc.?")

        else:
            print("⚠️ Not a diet preference message. Ignoring slot update.")

        return []  # No updates if intent doesn't match




class TriggerActionMeal(Action):
    """Automatic  fetches and returns meal recommendations on storing the diet preference"""

    def name(self):
        """Returns the action name."""
        return "action_trigger_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        """Handles meal suggestion requests by fetching relevant food items and nutrition details."""
        user_query = tracker.latest_message.get("text", "").lower()
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")
        user_preference = tracker.get_slot("user_preference")  

        print(f"🔹 User Query: {user_query}")
        print(f"🔹 Detected Intent: {detected_intent}")
        print(f"🔹 Stored Diet Preference: {user_preference}")
        
        # If no input is provided, prompt the user for preferences
        if not user_query and not user_preference:
            return "Please tell me your food preferences, or I can suggest general healthy meals!"

        # Extract keywords
        refined_food_keywords = extract_diet_preference(user_query)
        print(f"🔹 Extracted Food Keywords: {refined_food_keywords}")

        refined_query = refined_food_keywords  

        print(f"🔹 Final API Query: {refined_query}")

        # Step 1: Fetch meal suggestions from Nutritionix API
        try:
            search_response = requests.get(f"{NUTRITIONIX_SEARCH_API}?query={refined_query}", headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()
        except Exception as e:
            print(f"⚠️ API Search Error: {e}")
            return "Sorry, I couldn't fetch meal suggestions at the moment."
        
        # Extract up to 5 unique meal options
        meals = list(set([item["food_name"].title() for item in search_data.get("common", [])]))[:5]

        if not meals:
            return "I’m not sure about that food item. Can you specify more details?"

        # Step 2: Fetch detailed nutrition information
        try:
            nutrition_response = requests.post(NUTRITIONIX_NUTRIENTS_API, headers=HEADERS, json={"query": ", ".join(meals)})
            nutrition_response.raise_for_status()
            nutrition_data = nutrition_response.json()
        except Exception as e:
            print(f"⚠️ API Nutrition Error: {e}")
            return "Sorry, I couldn't fetch nutrition details."
        
       # Exclude non-meal items (e.g., specific nutrients)
        excluded_items = {
            "protein", "carbs", "fiber", "fats", "iron", "omega-3", "sodium", "sugar"
        }

        seen_meals = set()  
        meal_suggestions = []
        
        # Step 3: Extract meal names and nutrition details
        for food in nutrition_data.get("foods", []):
            meal_name = food["food_name"].title()
            if meal_name.lower() in excluded_items:
                continue  

            # Extract and format nutrition values
            calories = food.get('nf_calories', 'Unknown')
            protein = food.get('nf_protein', 'Unknown')
            carbs = food.get('nf_total_carbohydrate', 'Unknown')
            fat = food.get('nf_total_fat', 'Unknown')

            meal_entry = f"{meal_name} - {calories} kcal | Protein: {protein}g | Carbs: {carbs}g | Fat: {fat}g"
            
            if meal_name not in seen_meals:  
                seen_meals.add(meal_name)
                meal_suggestions.append(meal_entry)
        
        # Format final response
        meal_text = "\n".join(meal_suggestions)  
        follow_up_message = random.choice(FOLLOW_UP_RESPONSES) if not user_preference else None

        full_response = f"Here are some meal options:\n{meal_text}"
        if follow_up_message:
            full_response += f"\n{follow_up_message}"  # Append follow-up message correctly

        print(f"🔹 Final Response Sent to Frontend by trigger function:\n{full_response}")  # Debugging step
        return full_response  # Return response instead of dispatching it


class ActionRecommendMeal(Action):
    """Fetches and recommends meals based on user preferences and nutrition data."""

    def name(self):
        """Returns the action name."""
        return "action_recommend_meal"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        """Processes user input, extracts food keywords, fetches meal recommendations, and sends responses."""
        user_query = tracker.latest_message.get("text", "").lower()
        detected_intent = tracker.latest_message.get("intent", {}).get("name", "")
        user_preference = tracker.get_slot("user_preference")  

        print(f"🔹 User Query: {user_query}")
        print(f"🔹 Detected Intent: {detected_intent}")
        print(f"🔹 Stored Diet Preference: {user_preference}")
        
        # If no input is provided, prompt the user for preferences
        if not user_query and not user_preference:
            dispatcher.utter_message("Please tell me your food preferences, or I can suggest general healthy meals!")
            return []

        # Extract food keywords
        refined_food_keywords = extract_food_keywords(user_query) if user_query else ""
        print(f"🔹 Extracted Food Keywords: {refined_food_keywords}")

        # correctly setting refined_query**
        if user_preference and refined_food_keywords:
            refined_query = f"{user_preference} {refined_food_keywords}"
        elif user_preference:
            refined_query = user_preference
        elif refined_food_keywords:
            refined_query = refined_food_keywords
        else:
            refined_query = "healthy meal"

        print(f"🔹 Final API Query: {refined_query}")

        # Step 1: Fetch meal suggestions from Nutritionix API
        try:
            search_response = requests.get(f"{NUTRITIONIX_SEARCH_API}?query={refined_query}", headers=HEADERS)
            search_response.raise_for_status()
            search_data = search_response.json()
        except Exception as e:
            print(f"⚠️ API Search Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't fetch meal suggestions at the moment.")
            return []
        
        # Extract up to 5 unique meal options
        meals = list(set([item["food_name"].title() for item in search_data.get("common", [])]))[:5]

        if not meals:
            dispatcher.utter_message("I’m not sure about that food item. Can you specify more details?")
            return []

        # Step 2: Fetch detailed nutrition information
        try:
            nutrition_response = requests.post(NUTRITIONIX_NUTRIENTS_API, headers=HEADERS, json={"query": ", ".join(meals)})
            nutrition_response.raise_for_status()
            nutrition_data = nutrition_response.json()
        except Exception as e:
            print(f"⚠️ API Nutrition Error: {e}")
            dispatcher.utter_message("Sorry, I couldn't fetch nutrition details.")
            return []

        excluded_items = {"protein", "carbs", "fiber", "fats", "iron", "omega-3", "sodium", "sugar"}

        seen_meals = set()  
        meal_suggestions = []
        
        # Step 3: Extract meal names and nutrition details
        for food in nutrition_data.get("foods", []):
            meal_name = food["food_name"].title()
            if meal_name.lower() in excluded_items:
                continue  

            # Extract and format nutrition values
            calories = food.get('nf_calories', 'Unknown')
            protein = food.get('nf_protein', 0)  # Default to 0 if missing
            carbs = food.get('nf_total_carbohydrate', 'Unknown')
            fat = food.get('nf_total_fat', 'Unknown')

            meal_entry = {
                "name": meal_name,
                "calories": calories,
                "nf_protein": protein,  # Sorting Key
                "carbs": carbs,
                "fat": fat
            }
            
            if meal_name not in seen_meals:  
                seen_meals.add(meal_name)
                meal_suggestions.append(meal_entry)

        # Sort meals by protein content (highest first)
        nutrient_priority = "nf_protein"
        meal_suggestions.sort(key=lambda x: float(x.get(nutrient_priority, 0)), reverse=True)

        # Format final response
        meal_text = "\n".join(
            f"{meal['name']} - {meal['calories']} kcal | Protein: {meal['nf_protein']}g | Carbs: {meal['carbs']}g | Fat: {meal['fat']}g"
            for meal in meal_suggestions
        )
        
        follow_up_message = random.choice(FOLLOW_UP_RESPONSES) if not user_preference else None

        full_response = f"Here are some meal options :\n{meal_text}"
        if follow_up_message:
            full_response += f"\n{follow_up_message}"  # Append follow-up message correctly

        print(f"🔹 Final Response Sent to Frontend:\n{full_response}")  # Debugging step
        dispatcher.utter_message(text=full_response)  # Ensure text is explicitly passed

        return []  # Fixed: Do NOT return the response string



class ActionHandleFeedback(Action):
    """Handles user feedback on meal recommendations."""

    def name(self):
        """Returns the action name."""
        return "action_handle_feedback"

    def run(self, dispatcher, tracker, domain):
        """Responds based on user feedback type."""
        feedback = tracker.get_slot("feedback_type")

        if feedback == "positive":
            dispatcher.utter_message("Glad you liked it! Need more suggestions?")
        elif feedback == "negative":
            dispatcher.utter_message("Sorry about that. Want another recommendation?")
        else:
            dispatcher.utter_message("Thanks for your feedback!")

        return []  # No additional actions required
