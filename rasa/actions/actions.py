from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

FLASK_API_URL = "http://localhost:5000/webhook"

class ActionRecommendMeal(Action):
    def name(self):
        return "action_recommend_meal"

    def run(self, dispatcher, tracker, domain):
        user_query = tracker.latest_message.get("text")  # Get user's message

        # Send request to Flask API
        response = requests.post(FLASK_API_URL, json={"queryResult": {"queryText": user_query}})
        flask_response = response.json()

        dispatcher.utter_message(text=flask_response["fulfillmentText"])
        return []
    
class StoreUserPreferences(Action):
    def name(self):
        return "action_store_preferences"

    def run(self, dispatcher, tracker, domain):
        preference = tracker.latest_message.get("text")  # Get user message
        dispatcher.utter_message(f"Got it! You prefer {preference}.")
        return [SlotSet("user_preference", preference)]




