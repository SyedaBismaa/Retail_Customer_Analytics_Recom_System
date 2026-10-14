"""
Script to train and save the Product Recommendation Engine & Customer Segmentation Model
using Joblib into .pkl files.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

print("Step 1: Loading retail datasets...")
orders = pd.read_csv("sql_ready_datasets/orders.csv")
order_items = pd.read_csv("sql_ready_datasets/order_items.csv")
products = pd.read_csv("sql_ready_datasets/products.csv")
customers = pd.read_csv("sql_ready_datasets/customers.csv")

# Normalize column names to lowercase for easy access
orders.columns = orders.columns.str.lower()
order_items.columns = order_items.columns.str.lower()
products.columns = products.columns.str.lower()
customers.columns = customers.columns.str.lower()

# Merge transaction data
transactions_merged = (
    order_items.merge(orders[["order_id", "customer_id", "order_status"]], on="order_id", how="inner")
    .merge(products[["product_id", "product_name", "category", "price"]], on="product_id", how="inner")
)

# Filter for delivered orders
delivered = transactions_merged[transactions_merged["order_status"] == "Delivered"]

# Group by order to create market baskets
baskets = delivered.groupby("order_id")["product_name"].apply(list).tolist()
popular_products = delivered["product_name"].value_counts()

print(f"Loaded {len(baskets)} transactions and {len(popular_products)} unique products.")

# Build Association Matrix / Rules Model
print("Step 2: Building Association & Recommendation Model...")

# Product co-occurrence dictionary
from collections import defaultdict
co_occurrences = defaultdict(lambda: defaultdict(int))
item_counts = defaultdict(int)

for basket in baskets:
    unique_items = set(basket)
    for item in unique_items:
        item_counts[item] += 1
    for item1 in unique_items:
        for item2 in unique_items:
            if item1 != item2:
                co_occurrences[item1][item2] += 1

total_transactions = len(baskets)
rules_list = []

for item1, related in co_occurrences.items():
    supp1 = item_counts[item1] / total_transactions
    for item2, count in related.items():
        supp2 = item_counts[item2] / total_transactions
        supp_both = count / total_transactions
        confidence = supp_both / supp1 if supp1 > 0 else 0
        lift = confidence / supp2 if supp2 > 0 else 0

        # Keep significant rules
        if count >= 10 and lift > 1.2:
            rules_list.append({
                "antecedent": item1,
                "consequent": item2,
                "support": round(supp_both, 5),
                "confidence": round(confidence, 4),
                "lift": round(lift, 3),
                "co_count": count
            })

rules_df = pd.DataFrame(rules_list).sort_values("lift", ascending=False)
print(f"Generated {len(rules_df)} association rules.")

# Recommendation Model Wrapper Class
class RetailRecommenderModel:
    def __init__(self, rules_df, popular_products, top_n_default=5):
        self.rules_df = rules_df
        self.popular_products = popular_products.to_dict()
        self.popular_list = popular_products.index.tolist()
        self.top_n_default = top_n_default

    def recommend(self, purchased_products, top_n=None):
        if top_n is None:
            top_n = self.top_n_default
        
        purchased = set(purchased_products)
        recommendations = {}

        # 1. Match Association Rules
        matched_rules = self.rules_df[self.rules_df["antecedent"].isin(purchased)]
        for _, row in matched_rules.iterrows():
            item = row["consequent"]
            if item not in purchased:
                if item not in recommendations or row["lift"] > recommendations[item]["lift"]:
                    recommendations[item] = {
                        "product_name": item,
                        "confidence": float(row["confidence"]),
                        "lift": float(row["lift"]),
                        "support": float(row["support"]),
                        "source": "Association Rule"
                    }

        # Sort by lift, then confidence
        ranked = sorted(
            recommendations.values(),
            key=lambda x: (x["lift"], x["confidence"], x["support"]),
            reverse=True
        )

        results = ranked[:top_n]
        recommended_set = {r["product_name"] for r in results}

        # 2. Fallback to Popularity
        for item in self.popular_list:
            if len(results) >= top_n:
                break
            if item not in purchased and item not in recommended_set:
                results.append({
                    "product_name": item,
                    "confidence": None,
                    "lift": None,
                    "support": None,
                    "source": "Popularity Fallback"
                })
                recommended_set.add(item)

        return results

model = RetailRecommenderModel(rules_df, popular_products)

# Step 3: Customer Segmentation RFM Model
print("Step 3: Training RFM Customer Segmentation Model...")
customer_orders = orders[orders["order_status"] == "Delivered"].merge(order_items, on="order_id")
customer_orders["order_date"] = pd.to_datetime(customer_orders["order_date"])
ref_date = customer_orders["order_date"].max()

rfm = customer_orders.groupby("customer_id").agg({
    "order_date": lambda x: (ref_date - x.max()).days,
    "order_id": "nunique",
    "item_total": "sum"
}).rename(columns={
    "order_date": "recency",
    "order_id": "frequency",
    "item_total": "monetary"
})

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(np.log1p(rfm))
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
kmeans.fit(rfm_scaled)

segmentation_model = {
    "scaler": scaler,
    "kmeans": kmeans,
    "feature_names": ["recency", "frequency", "monetary"],
    "cluster_names": {
        0: "Champions / High Value",
        1: "Loyal Customers",
        2: "Potential Loyalists",
        3: "At-Risk / Churned"
    }
}

# Save models to disk
os.makedirs("models", exist_ok=True)
recommender_pkl_path = "models/recommendation_engine.pkl"
segmentation_pkl_path = "models/customer_segmentation.pkl"

joblib.dump(model, recommender_pkl_path)
joblib.dump(segmentation_model, segmentation_pkl_path)

print(f"SUCCESS: Saved recommendation model to {recommender_pkl_path}")
print(f"SUCCESS: Saved segmentation model to {segmentation_pkl_path}")

# Quick test of model
test_recs = model.recommend(["Hasbro Superhero Toy 200"], top_n=3)
print("Test recommendation for ['Hasbro Superhero Toy 200']:", test_recs)
