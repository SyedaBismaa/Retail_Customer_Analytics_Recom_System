"""
Customer Segmentation Router for RetailIQ.

Endpoints:
- GET /api/segments/summary: High-level cluster summary, RFM centroids, and marketing playbooks.
- GET /api/segments/customers: Customer segment assignments with pagination and filtering.
- GET /api/segments/{segment_name}: Drilldown into a specific segment's performance and customers.
"""

from typing import Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database import get_db
from src.segmentation import (
    get_segment_summary,
    get_customer_segment,
    is_segmentation_loaded,
)
from src.schemas import (
    SegmentsSummaryResponse,
    PaginatedCustomersResponse,
    CustomerItem,
)

router = APIRouter(prefix="/api/segments", tags=["Segmentation"])


@router.get(
    "/summary",
    response_model=SegmentsSummaryResponse,
    summary="Get summary of all 5 customer segments and RFM metrics",
)
def get_segments_summary():
    """
    Returns the distribution of all 5 customer segments:
    - High-Value Loyal
    - Regular / Mid-Value
    - At-Risk / Dormant
    - Recent / Low-Value
    - No Purchase
    Includes customer counts, population share, average RFM metrics, and marketing strategies.
    """
    summary_items = get_segment_summary()
    total_customers = sum(item["count"] for item in summary_items)

    return SegmentsSummaryResponse(
        total_customers=total_customers,
        segments=summary_items,
    )


@router.get(
    "/customers",
    response_model=PaginatedCustomersResponse,
    summary="Get customers by segment with pagination",
)
def get_segment_customers(
    segment_name: Optional[str] = Query(None, description="Segment filter name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns paginated customer profiles belonging to a particular RFM segment.
    """
    try:
        # Base query from customer_analytics table
        query = text("""
            SELECT 
                customer_id, first_name, last_name, age, gender, city, state,
                occupation, income, loyalty_tier,
                COALESCE(total_orders, 0) as total_orders,
                COALESCE(total_spending, 0) as total_spending,
                COALESCE(avg_order_value, 0) as avg_order_value
            FROM customer_analytics
            ORDER BY total_spending DESC
        """)
        rows = db.execute(query).fetchall()

        matched_customers = []
        for r in rows:
            cid = r[0]
            assigned_seg = get_customer_segment(cid) or "Recent / Low-Value"

            if segment_name and segment_name != "All":
                if assigned_seg.lower() != segment_name.strip().lower():
                    continue

            matched_customers.append(
                CustomerItem(
                    customer_id=cid,
                    first_name=r[1],
                    last_name=r[2],
                    age=float(r[3]) if r[3] is not None else None,
                    gender=r[4],
                    city=r[5],
                    state=r[6],
                    occupation=r[7],
                    income=float(r[8]) if r[8] is not None else None,
                    loyalty_tier=r[9],
                    total_orders=int(r[10]),
                    total_spending=round(float(r[11]), 2),
                    avg_order_value=round(float(r[12]), 2),
                    segment=assigned_seg,
                )
            )

        total = len(matched_customers)
        offset = (page - 1) * page_size
        paginated_slice = matched_customers[offset : offset + page_size]
        total_pages = math.ceil(total / page_size) if page_size > 0 else 1

        return PaginatedCustomersResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            customers=paginated_slice,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying segment customers: {str(exc)}",
        )


@router.get(
    "/{segment_name}",
    summary="Get single segment profile, RFM values, and sample members",
)
def get_single_segment_details(
    segment_name: str,
    db: Session = Depends(get_db),
):
    """
    Returns complete profile and top customer members for a single segment.
    """
    summaries = get_segment_summary()
    target_summary = next(
        (s for s in summaries if s["segment_name"].lower() == segment_name.strip().lower()),
        None
    )

    if not target_summary:
        valid_names = [s["segment_name"] for s in summaries]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segment '{segment_name}' not found. Valid segments: {valid_names}",
        )

    # Get sample customers for this segment
    cust_query = text("""
        SELECT customer_id, first_name, last_name, city, state, loyalty_tier, total_spending, total_orders
        FROM customer_analytics
        ORDER BY total_spending DESC
    """)
    rows = db.execute(cust_query).fetchall()

    sample_customers = []
    for r in rows:
        cid = r[0]
        assigned_seg = get_customer_segment(cid)
        if assigned_seg and assigned_seg.lower() == segment_name.strip().lower():
            sample_customers.append({
                "customer_id": cid,
                "name": f"{r[1]} {r[2]}",
                "location": f"{r[3]}, {r[4]}",
                "loyalty_tier": r[5],
                "total_spending": float(r[6]),
                "total_orders": int(r[7]),
            })
            if len(sample_customers) >= 10:
                break

    return {
        "segment": target_summary,
        "sample_customers": sample_customers,
    }
