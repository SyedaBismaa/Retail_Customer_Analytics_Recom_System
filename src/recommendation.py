"""
Product Recommendation Engine Service Module for RetailIQ.

This module loads the serialized FP-Growth association rules and product popularity
rankings from 'models/' once when the application starts.
It provides:
- Co-purchase recommendations based on market basket association rules.
- Confidence, lift, and support metric reporting.
- Exclusion of previously purchased items.
- Popularity-based fallback to guarantee recommendations even when
  no co-purchase rule is triggered (preventing cold-start issues).
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import joblib
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULES_PATH = PROJECT_ROOT / "models" / "recommendation_rules.pkl"
POPULARITY_PATH = PROJECT_ROOT / "models" / "popularity_ranking.pkl"

# Global in-memory artifact references (loaded once at startup)
_rules_df: Optional[pd.DataFrame] = None
_popularity_list: Optional[List[str]] = None


def load_recommendation_models() -> bool:
    """
    Loads the association rules DataFrame and popularity ranking list into memory once at startup.
    Returns True if successfully loaded, False otherwise.
    """
    global _rules_df, _popularity_list
    rules_ok = False
    pop_ok = False

    if RULES_PATH.exists():
        try:
            _rules_df = joblib.load(RULES_PATH)
            rules_ok = True
        except Exception as exc:
            print(f"Error loading recommendation rules: {exc}")
            _rules_df = None

    if POPULARITY_PATH.exists():
        try:
            _popularity_list = joblib.load(POPULARITY_PATH)
            pop_ok = True
        except Exception as exc:
            print(f"Error loading popularity ranking: {exc}")
            _popularity_list = None

    return rules_ok and pop_ok


def is_recommendation_loaded() -> bool:
    """Checks whether both association rules and popularity artifacts are loaded."""
    return _rules_df is not None and _popularity_list is not None


def get_product_details_from_db(product_names: List[str], db: Optional[Session] = None) -> Dict[str, Dict[str, Any]]:
    """
    Queries PostgreSQL for product metadata (price, category, subcategory, brand, rating).
    Falls back gracefully if the database is not provided.
    """
    details_map = {}
    if db is not None and len(product_names) > 0:
        try:
            query = text("""
                SELECT product_name, category, subcategory, brand, price, discount, product_rating
                FROM products
                WHERE product_name IN :names
            """)
            # Execute parameterized query
            rows = db.execute(query, {"names": tuple(product_names)}).fetchall()
            for r in rows:
                details_map[r[0]] = {
                    "category": r[1],
                    "subcategory": r[2],
                    "brand": r[3],
                    "price": float(r[4]) if r[4] is not None else 0.0,
                    "discount": float(r[5]) if r[5] is not None else 0.0,
                    "rating": float(r[6]) if r[6] is not None else 4.0
                }
        except Exception as exc:
            print(f"Database product detail query warning: {exc}")

    return details_map


def recommend_products(
    purchased_products: List[str],
    top_n: int = 5,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """
    Generates personalized product recommendations matching 'product_recommendation.ipynb':
    1. Matches antecedent products from the customer's purchase history.
    2. Excludes products already purchased.
    3. Ranks candidates by Lift (co-occurrence multiplier) descending, then Confidence, then Support.
    4. Falls back to Popularity ranking if fewer than top_n recommendations are matched.
    5. Returns items labeled with their source ('Association Rule' vs 'Popularity Fallback').
    """
    if not is_recommendation_loaded():
        load_recommendation_models()

    if not is_recommendation_loaded():
        return []

    purchased_set: Set[str] = set(purchased_products)
    recommendations: Dict[str, Dict[str, Any]] = {}

    # Step 1: Check Association Rules
    # Filter rules where the antecedent was purchased
    matching_rules = _rules_df[_rules_df["antecedent"].isin(purchased_set)]

    for _, row in matching_rules.iterrows():
        consequent = row["consequent"]
        # Rule of integrity: exclude items the customer has already purchased
        if consequent not in purchased_set:
            lift = float(row["lift"])
            confidence = float(row["confidence"])
            support = float(row["support"])

            # If the product was recommended multiple times, keep the rule with the highest lift
            if consequent not in recommendations or lift > recommendations[consequent]["lift"]:
                recommendations[consequent] = {
                    "product_name": consequent,
                    "confidence": confidence,
                    "lift": lift,
                    "support": support,
                    "source": "Association Rule",
                }

    # Step 2: Rank by lift descending, then confidence, then support
    ranked_candidates = sorted(
        recommendations.values(),
        key=lambda x: (x["lift"], x["confidence"], x["support"]),
        reverse=True
    )

    results = ranked_candidates[:top_n]
    recommended_set = {item["product_name"] for item in results}

    # Step 3: Popularity Fallback (ensures top_n recommendations are always returned)
    if len(results) < top_n and _popularity_list is not None:
        for popular_item in _popularity_list:
            if len(results) >= top_n:
                break
            if popular_item not in purchased_set and popular_item not in recommended_set:
                results.append({
                    "product_name": popular_item,
                    "confidence": None,
                    "lift": None,
                    "support": None,
                    "source": "Popularity Fallback",
                })
                recommended_set.add(popular_item)

    # Step 4: Enrich products with real database metadata
    product_names = [item["product_name"] for item in results]
    db_details = get_product_details_from_db(product_names, db=db)

    for item in results:
        p_name = item["product_name"]
        details = db_details.get(p_name, {
            "category": "Retail",
            "subcategory": "General",
            "brand": "Standard",
            "price": 999.0,
            "discount": 0.0,
            "rating": 4.0
        })
        item["product_info"] = details

    return results


# Load artifacts at module import time
load_recommendation_models()
