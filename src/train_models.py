"""
Model Training and Artifact Serialization Script for RetailIQ.

This script executes the machine learning training pipelines developed in the project notebooks:
1. Customer Segmentation: RFM calculation -> Yeo-Johnson PowerTransformer -> StandardScaler -> PCA (2D) -> KMeans (k=4)
2. Product Recommendation: Market Basket Transaction Encoding -> FP-Growth -> Association Rules -> Popularity Ranking

All supported fitted objects and rule sets are saved using Joblib into the 'models/' directory.
Run this script whenever underlying retail data changes:
    python -m src.train_models
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import PowerTransformer, StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# Setup project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR = PROJECT_ROOT / "sql_ready_datasets"


def train_and_save_segmentation():
    """
    Trains the RFM Customer Segmentation model matching 'customer_analytics.ipynb':
    - Calculates Recency, Frequency, and Monetary metrics for customers.
    - Applies Yeo-Johnson PowerTransformer to normalize right-skewed RFM distributions.
    - Applies StandardScaler to bring features to comparable variance.
    - Uses PCA(n_components=2) retaining ~96.6% total variance.
    - Fits KMeans(n_clusters=4, random_state=42) and maps clusters to business segments:
        0 -> Recent / Low-Value
        1 -> At-Risk / Dormant
        2 -> Regular / Mid-Value
        3 -> High-Value Loyal
        No purchase history -> No Purchase
    """
    print("\n[1/2] Training Customer Segmentation Pipeline...")

    # Load datasets
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")
    order_items = pd.read_csv(DATA_DIR / "order_items.csv")

    # Normalize column names to lowercase for consistency
    customers.columns = customers.columns.str.lower()
    orders.columns = orders.columns.str.lower()
    order_items.columns = order_items.columns.str.lower()

    # Filter orders to only completed 'Delivered' orders
    delivered_orders = orders[orders["order_status"] == "Delivered"].copy()
    delivered_orders["order_date"] = pd.to_datetime(delivered_orders["order_date"])

    # Reference date is the latest order date in the dataset
    reference_date = delivered_orders["order_date"].max()

    # Join orders and order items to compute monetary value per order
    order_spending = delivered_orders.merge(order_items, on="order_id", how="inner")

    # Aggregate RFM metrics per customer
    rfm_grouped = order_spending.groupby("customer_id").agg(
        recency=("order_date", lambda dates: (reference_date - dates.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("item_total", "sum")
    ).reset_index()

    # Customers with purchases (4,400 customers)
    rfm = rfm_grouped.copy()

    # Preprocessing Step 1: Yeo-Johnson Power Transformation to handle skewness
    pt = PowerTransformer(method="yeo-johnson")
    rfm_transformed = pt.fit_transform(rfm[["recency", "frequency", "monetary"]])

    # Preprocessing Step 2: StandardScaler for zero mean and unit variance
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_transformed)

    # Preprocessing Step 3: PCA to 2 components (explaining ~96.6% variance)
    pca = PCA(n_components=2, random_state=42)
    rfm_pca = pca.fit_transform(rfm_scaled)

    # Clustering Step: KMeans with 4 clusters as determined in notebook
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm["cluster"] = kmeans.fit_predict(rfm_pca)

    # Business segment mapping verified from notebook
    segment_map = {
        0: "Recent / Low-Value",
        1: "At-Risk / Dormant",
        2: "Regular / Mid-Value",
        3: "High-Value Loyal"
    }
    rfm["customer_segment"] = rfm["cluster"].map(segment_map)

    # Build customer segment lookup for all 5,000 customers (including non-purchasers)
    all_customer_ids = customers["customer_id"].unique()
    customer_segment_dict = dict(zip(rfm["customer_id"], rfm["customer_segment"]))

    for cid in all_customer_ids:
        if cid not in customer_segment_dict:
            customer_segment_dict[cid] = "No Purchase"

    # Compute segment summary statistics
    cluster_summary = rfm.groupby("customer_segment")[["recency", "frequency", "monetary"]].agg(
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        customer_count=("monetary", "count")
    ).reset_index()

    # Package the fitted pipeline artifacts cleanly without custom unpicklable class dependencies
    segmentation_artifact = {
        "transformer": pt,
        "scaler": scaler,
        "pca": pca,
        "kmeans": kmeans,
        "segment_map": segment_map,
        "feature_names": ["recency", "frequency", "monetary"],
        "reference_date": str(reference_date),
        "customer_segments": customer_segment_dict,
        "cluster_summary": cluster_summary.to_dict(orient="records"),
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "total_customers": len(all_customer_ids),
        "purchasing_customers": len(rfm),
    }

    # Save artifact using Joblib
    segmentation_path = MODELS_DIR / "customer_segmentation.pkl"
    joblib.dump(segmentation_artifact, segmentation_path)
    print(f"Saved Customer Segmentation Pipeline -> {segmentation_path}")
    print(f"Segment Counts:")
    counts = pd.Series(list(customer_segment_dict.values())).value_counts()
    for seg, cnt in counts.items():
        print(f"  - {seg}: {cnt} customers ({cnt/len(customer_segment_dict):.1%})")


def train_and_save_recommendations():
    """
    Trains the Product Recommendation Engine matching 'product_recommendation.ipynb':
    - Extracts delivered order transactions.
    - Uses TransactionEncoder and FP-Growth algorithm (min_support=0.002).
    - Generates Association Rules with confidence >= 0.20, lift > 2.0, support >= 0.002.
    - Calculates product popularity rankings for fallback recommendations.
    - Saves rules DataFrame and popularity Series using Joblib.
    """
    print("\n[2/2] Training Product Recommendation Engine...")

    # Load orders, items, and products
    orders = pd.read_csv(DATA_DIR / "orders.csv")
    order_items = pd.read_csv(DATA_DIR / "order_items.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")

    orders.columns = orders.columns.str.lower()
    order_items.columns = order_items.columns.str.lower()
    products.columns = products.columns.str.lower()

    # Join transaction data for delivered orders
    transactions = (
        order_items.merge(orders[["order_id", "order_status"]], on="order_id", how="inner")
        .merge(products[["product_id", "product_name"]], on="product_id", how="inner")
    )
    delivered_transactions = transactions[transactions["order_status"] == "Delivered"]

    # Group items into market baskets (one list per order)
    baskets = delivered_transactions.groupby("order_id")["product_name"].apply(list).tolist()
    print(f"Total delivered order baskets: {len(baskets)}")

    # Step 1: One-hot encode transactions
    te = TransactionEncoder()
    te_ary = te.fit_transform(baskets)
    basket_df = pd.DataFrame(te_ary, columns=te.columns_)

    # Step 2: Frequent itemset generation using FP-Growth
    print("Mining frequent itemsets using FP-Growth (min_support=0.002)...")
    freq_itemsets = fpgrowth(basket_df, min_support=0.002, use_colnames=True)
    print(f"Found {len(freq_itemsets)} frequent itemsets.")

    # Step 3: Association rule generation
    all_rules = association_rules(freq_itemsets, metric="confidence", min_threshold=0.1)
    
    # Filter rules based on established notebook criteria:
    # confidence >= 0.20, lift > 2.0, support >= 0.002
    useful_rules = all_rules[
        (all_rules["confidence"] >= 0.20) &
        (all_rules["lift"] > 2.0) &
        (all_rules["support"] >= 0.002)
    ].copy()

    useful_rules = useful_rules.sort_values(by=["lift", "confidence"], ascending=[False, False])
    print(f"Filtered useful association rules: {len(useful_rules)}")

    # Convert frozensets to simple strings for fast JSON/API querying
    rules_export = []
    for _, row in useful_rules.iterrows():
        # Get first antecedent and first consequent
        antecedents = list(row["antecedents"])
        consequents = list(row["consequents"])
        
        for ant in antecedents:
            for cons in consequents:
                rules_export.append({
                    "antecedent": ant,
                    "consequent": cons,
                    "support": float(row["support"]),
                    "confidence": float(row["confidence"]),
                    "lift": float(row["lift"])
                })

    rules_df = pd.DataFrame(rules_export)

    # Step 4: Popularity ranking for fallback recommendations
    popularity_counts = delivered_transactions["product_name"].value_counts()
    popularity_list = popularity_counts.index.tolist()

    # Step 5: Save Joblib artifacts
    rules_path = MODELS_DIR / "recommendation_rules.pkl"
    popularity_path = MODELS_DIR / "popularity_ranking.pkl"

    joblib.dump(rules_df, rules_path)
    joblib.dump(popularity_list, popularity_path)

    print(f"Saved Association Rules -> {rules_path} ({len(rules_df)} rules)")
    print(f"Saved Popularity Ranking -> {popularity_path} ({len(popularity_list)} products)")


if __name__ == "__main__":
    train_and_save_segmentation()
    train_and_save_recommendations()
    print("\nAll model artifacts successfully trained and saved with Joblib!")
