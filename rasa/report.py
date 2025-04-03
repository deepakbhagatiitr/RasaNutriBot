import json
import pandas as pd

# Load JSON file
with open("results/intent_report.json", "r") as f:
    data = json.load(f)

# Convert JSON to DataFrame
df = pd.DataFrame(data).T  # Transpose for proper structure

# Save as CSV
df.to_csv("intent_report.csv", index_label="Intent")

print("✅ Conversion complete! Saved as 'intent_report.csv'")
