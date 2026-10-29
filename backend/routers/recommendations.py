"""
Recommendation Endpoints Router for RetailIQ.

Endpoints:
- GET /api/recommendations/{customer_id}: Generates personalized product recommendations
  for a customer based on their historical delivered purchases.
- POST /api/recommendations/custom: Allows testing recommendations for any custom basket of products.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database import get_db
from src.recommendation import recommend_products, is_recommendation_loaded
from src.segmentation import get_customer_segment
from src.schemas import (
    CustomerRecommendationResponse,
    RecommendationItem,
    RecommendationRequest,
    ProductInfo,
)

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get(
    "/{customer_id}",
    response_model=CustomerRecommendationResponse,
    summary="Get personalized product recommendations for a customer",
)
def get_customer_recommendations(
    customer_id: str,
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
):
    """
    1. Validates that the customer exists in PostgreSQL.
    2. Queries customer's past delivered purchases.
    3. Runs the association rule engine to find high-affinity complementary items.
    4. Excludes items the customer already bought.
    5. Falls back to popularity ranking if needed.
    6. Returns items with confidence, lift, support, and source ('Association Rule' vs 'Popularity Fallback').
    """
    # Step 1: Validate customer existence
    cust_query = text("""
        SELECT customer_id, first_name, last_name, loyalty_tier
        FROM customers
        WHERE customer_id = :cid
    """)
    cust_row = db.execute(cust_query, {"cid": customer_id.strip()}).fetchone()

    if not cust_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found in the database.",
        )

    cid = cust_row[0]
    name = f"{cust_row[1]} {cust_row[2]}"
    tier = cust_row[3] or "Silver"
    segment = get_customer_segment(cid) or "Recent / Low-Value"

    # Step 2: Retrieve historical purchased products from PostgreSQL
    history_query = text("""
        SELECT DISTINCT p.product_name
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.customer_id = :cid AND o.order_status = 'Delivered'
    """)
    purchased_rows = db.execute(history_query, {"cid": cid}).fetchall()
    purchased_history = [r[0] for r in purchased_rows]

    # Step 3: Check that recommendation model is ready
    if not is_recommendation_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation model artifacts are not currently loaded.",
        )

    # Step 4: Run the recommendation engine
    raw_recs = recommend_products(purchased_products=purchased_history, top_n=top_n, db=db)

    # Step 5: Format response items
    formatted_recs = []
    for r in raw_recs:
        info = r.get("product_info", {})
        formatted_recs.append(
            RecommendationItem(
                product_name=r["product_name"],
                confidence=r.get("confidence"),
                lift=r.get("lift"),
                support=r.get("support"),
                source=r.get("source", "Popularity Fallback"),
                product_info=ProductInfo(
                    category=info.get("category", "Retail"),
                    subcategory=info.get("subcategory", "General"),
                    brand=info.get("brand", "Standard"),
                    price=float(info.get("price", 0.0)),
                    discount=float(info.get("discount", 0.0)),
                    rating=float(info.get("rating", 4.0)),
                )
            )
        )

    return CustomerRecommendationResponse(
        customer_id=cid,
        customer_name=name,
        loyalty_tier=tier,
        customer_segment=segment,
        purchased_history_count=len(purchased_history),
        previously_purchased_products=purchased_history,
        recommendations=formatted_recs,
    )


@router.post(
    "/custom",
    summary="Get recommendations for a custom shopping basket",
)
def get_custom_basket_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    """
    Generates recommendations for an arbitrary basket of products,
    ideal for testing chained co-purchases in the interactive playground.
    """
    if not is_recommendation_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recommendation models are not loaded.",
        )

    raw_recs = recommend_products(
        purchased_products=request.purchased_products,
        top_n=request.top_n,
        db=db,
    )

    formatted_recs = []
    for r in raw_recs:
        info = r.get("product_info", {})
        formatted_recs.append({
            "product_name": r["product_name"],
            "confidence": r.get("confidence"),
            "lift": r.get("lift"),
            "support": r.get("support"),
            "source": r.get("source", "Popularity Fallback"),
            "product_info": info,
        })

    return {
        "status": "success",
        "basket_count": len(request.purchased_products),
        "recommendations": formatted_recs,
    }
