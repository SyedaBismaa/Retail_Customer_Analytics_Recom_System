import joblib
import json
from export_model import RetailRecommenderModel

print("Exporting rules database for frontend...")
model = joblib.load("models/recommendation_engine.pkl")

# Extract top rules for frontend instant matching
rules_export = []
for _, row in model.rules_df.iterrows():
    rules_export.append({
        "antecedent": str(row["antecedent"]),
        "consequent": str(row["consequent"]),
        "confidence": float(row["confidence"]),
        "lift": float(row["lift"]),
        "support": float(row["support"])
    })

data = {
    "rules": rules_export[:500], # top 500 rules
    "popular": model.popular_list[:30]
}

with open("frontend/src/data/rules_database.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Exported {len(rules_export[:500])} rules and {len(data['popular'])} popular items to rules_database.json")
