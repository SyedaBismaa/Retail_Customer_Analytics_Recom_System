"""
Customer Segmentation Service Module for RetailIQ.

This module loads the trained RFM segmentation artifact once at startup.
It provides:
- Business interpretations and marketing recommendations for each cluster.
- Aggregate summary metrics (counts, percentages, average RFM values).
- Customer segment lookup and new customer RFM inference using the full
  Yeo-Johnson -> StandardScaler -> PCA -> KMeans pipeline.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import joblib
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "customer_segmentation.pkl"

# Segment metadata with business interpretations and actionable strategies
SEGMENT_METADATA = {
    "High-Value Loyal": {
        "badge": "High Value",
        "color": "#10B981",  # Emerald
        "description": "Top-tier customers with high spending, frequent repeat purchases, and recent activity.",
        "strategy": "VIP rewards, exclusive preview of new arrivals, early access sales, and dedicated loyalty perks."
    },
    "Regular / Mid-Value": {
        "badge": "Loyalists",
        "color": "#3B82F6",  # Blue
        "description": "Consistent shoppers who purchase on a predictable cadence with solid order values.",
        "strategy": "Cross-category product bundles, loyalty tier milestones, and category expansion promotions."
    },
    "At-Risk / Dormant": {
        "badge": "At Risk",
        "color": "#EF4444",  # Rose
        "description": "Formerly active buyers who have not placed an order in several months and risk churning.",
        "strategy": "Re-activation win-back emails, personalized discount vouchers, and 'we miss you' surveys."
    },
    "Recent / Low-Value": {
        "badge": "Recent",
        "color": "#F59E0B",  # Amber
        "description": "Recent shoppers with lower order totals or first-time trial orders who need nurturing.",
        "strategy": "Welcome series follow-ups, free shipping thresholds, and entry-level cross-sell recommendations."
    },
    "No Purchase": {
        "badge": "Lead",
        "color": "#64748B",  # Slate
        "description": "Registered accounts that have never completed a transaction in the system.",
        "strategy": "First-purchase welcome discount, onboarding product guide, and category highlight campaigns."
    }
}

# Global in-memory artifact reference (loaded once at startup)
_segmentation_artifact: Optional[Dict[str, Any]] = None


def load_segmentation_model() -> bool:
    """
    Loads the customer segmentation Joblib artifact into memory once at application startup.
    Returns True if successfully loaded, False otherwise.
    """
    global _segmentation_artifact
    if MODEL_PATH.exists():
        try:
            # Joblib loads the dictionary containing transformer, scaler, pca, kmeans, and mappings
            _segmentation_artifact = joblib.load(MODEL_PATH)
            return True
        except Exception as exc:
            print(f"Error loading segmentation model: {exc}")
            _segmentation_artifact = None
            return False
    return False


def is_segmentation_loaded() -> bool:
    """Checks whether the segmentation artifact is loaded and ready for queries."""
    return _segmentation_artifact is not None


def get_segment_summary() -> List[Dict[str, Any]]:
    """
    Returns aggregated customer segment statistics (counts, percentages, and average RFM metrics).
    """
    if not is_segmentation_loaded():
        load_segmentation_model()

    if not is_segmentation_loaded():
        return []

    customer_segments = _segmentation_artifact.get("customer_segments", {})
    total_customers = len(customer_segments)

    # Count customers per segment
    segment_counts = pd.Series(list(customer_segments.values())).value_counts().to_dict()

    # Get RFM averages from cluster summary
    cluster_records = _segmentation_artifact.get("cluster_summary", [])
    cluster_metrics_map = {row["customer_segment"]: row for row in cluster_records}

    summary_list = []
    # Guarantee consistent display order
    ordered_segments = [
        "High-Value Loyal",
        "Regular / Mid-Value",
        "At-Risk / Dormant",
        "Recent / Low-Value",
        "No Purchase"
    ]

    for seg_name in ordered_segments:
        count = segment_counts.get(seg_name, 0)
        percentage = round((count / total_customers) * 100, 1) if total_customers > 0 else 0.0
        meta = SEGMENT_METADATA.get(seg_name, {
            "badge": "General",
            "color": "#6B7280",
            "description": "",
            "strategy": ""
        })

        rfm_data = cluster_metrics_map.get(seg_name, {})
        avg_rec = round(rfm_data.get("avg_recency", 0.0), 1)
        avg_freq = round(rfm_data.get("avg_frequency", 0.0), 1)
        avg_mon = round(rfm_data.get("avg_monetary", 0.0), 2)

        summary_list.append({
            "segment_name": seg_name,
            "badge": meta["badge"],
            "color": meta["color"],
            "count": count,
            "percentage": percentage,
            "avg_recency_days": avg_rec,
            "avg_frequency_orders": avg_freq,
            "avg_monetary_spend": avg_mon,
            "description": meta["description"],
            "strategy": meta["strategy"]
        })

    return summary_list


def get_customer_segment(customer_id: str) -> Optional[str]:
    """
    Looks up the segment assignment for an existing customer ID.
    """
    if not is_segmentation_loaded():
        load_segmentation_model()

    if not is_segmentation_loaded():
        return None

    customer_segments = _segmentation_artifact.get("customer_segments", {})
    return customer_segments.get(customer_id)


def predict_new_customer_segment(recency: float, frequency: float, monetary: float) -> Optional[str]:
    """
    Predicts the customer segment for new customer RFM metrics.
    Applies the full fitted pipeline:
    1. Yeo-Johnson PowerTransformer
    2. StandardScaler
    3. PCA (2 components)
    4. KMeans (k=4)
    5. Segment name mapping
    """
    if not is_segmentation_loaded():
        load_segmentation_model()

    if not is_segmentation_loaded():
        return None

    if frequency <= 0 or monetary <= 0:
        return "No Purchase"

    try:
        pt = _segmentation_artifact["transformer"]
        scaler = _segmentation_artifact["scaler"]
        pca = _segmentation_artifact["pca"]
        kmeans = _segmentation_artifact["kmeans"]
        segment_map = _segmentation_artifact["segment_map"]

        # Prepare 1x3 array of [recency, frequency, monetary]
        raw_input = np.array([[recency, frequency, monetary]])
        transformed = pt.transform(raw_input)
        scaled = scaler.transform(transformed)
        pca_features = pca.transform(scaled)

        cluster_id = int(kmeans.predict(pca_features)[0])
        return segment_map.get(cluster_id, "Regular / Mid-Value")
    except Exception as exc:
        print(f"Error predicting customer segment: {exc}")
        return None


# Load artifact at module import time
load_segmentation_model()
