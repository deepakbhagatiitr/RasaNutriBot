from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import requests
import os

NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"

HEADERS = {
    "x-app-id": "4993cdc2",
    "x-app-key": "ab8f3d73f2fa6ee7f1554c1812caba45",
    "Content-Type": "application/json",
}

class ActionRecommendMeal(Action):
    def name(self):
        return "action_recommend_meal"

    def run(self, dispatcher, tracker, domain):
        user_query = tracker.latest_message.get("text", "")

        # ✅ Step 1: Search for relevant meals in Nutritionix API
        search_response = requests.get(f"{NUTRITIONIX_SEARCH_API}?query={user_query}", headers=HEADERS)
        search_data = search_response.json()

        # ✅ Step 2: Extract top 5 meal names
        meals = [item["food_name"].title() for item in search_data.get("common", [])][:5]

        if not meals:
            dispatcher.utter_message("Sorry, I couldn't find a good meal option. Try a different request!")
            return []

        # ✅ Step 3: Get calories from Nutritionix API
        nutrition_response = requests.post(NUTRITIONIX_NUTRIENTS_API, headers=HEADERS, json={"query": ", ".join(meals)})
        nutrition_data = nutrition_response.json()

        meal_suggestions = [
            f"{food['food_name'].title()} - {food.get('nf_calories', 'Unknown')} calories"
            for food in nutrition_data.get("foods", [])
        ]

        # ✅ Step 4: Format response
        meal_text = "\n".join(meal_suggestions)
        dispatcher.utter_message(f"Here are some meal options:\n{meal_text}")

        return []
