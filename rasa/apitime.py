import time
import requests
NUTRITIONIX_SEARCH_API = "https://trackapi.nutritionix.com/v2/search/instant"
NUTRITIONIX_NUTRIENTS_API = "https://trackapi.nutritionix.com/v2/natural/nutrients"
refined_query = "high protein"
HEADERS = {
    "x-app-id": "4993cdc2",
    "x-app-key": "ab8f3d73f2fa6ee7f1554c1812caba45",
    "Content-Type": "application/json",
}
# Measure API response time
start_time = time.time()
search_response = requests.get(f"{NUTRITIONIX_SEARCH_API}?query={refined_query}", headers=HEADERS)
end_time = time.time()

search_latency = end_time - start_time
print(f"🔹 Nutritionix API Search Response Time: {search_latency:.2f} seconds")
