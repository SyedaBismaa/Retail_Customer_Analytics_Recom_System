"""
Customer Endpoints Router for RetailIQ.

Provides:
- Paginated customer browsing with search, segment, and loyalty tier filters.
- Detailed customer analytics profiles.
- Historical customer order records and line-item details.
"""

from typing import Optional
import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database import get_db
from src.segmentation import get_customer_segment
from src.schemas import (
    CustomerItem,
    PaginatedCustomersResponse,
    CustomerOrderDetail,
    OrderItemDetail,
)

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get(
    "",
    response_model=PaginatedCustomersResponse,
    summary="Get paginated customers with search and filters",
)
def list_customers(
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, ID, or city"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    loyalty_tier: Optional[str] = Query(None, description="Filter by loyalty tier"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of customers from the customer_analytics table.
    Integrates ML customer segment assignments with sorting and search capabilities.
    """
    try:
        # Base query from customer_analytics table
        where_clauses = ["1=1"]
        params = {}

        if search:
            where_clauses.append("""(
                LOWER(customer_id) LIKE LOWER(:search) OR
                LOWER(first_name) LIKE LOWER(:search) OR
                LOWER(last_name) LIKE LOWER(:search) OR
                LOWER(city) LIKE LOWER(:search)
            )""")
            params["search"] = f"%{search.strip()}%"

        if loyalty_tier and loyalty_tier != "All":
            where_clauses.append("LOWER(loyalty_tier) = LOWER(:loyalty_tier)")
            params["loyalty_tier"] = loyalty_tier.strip()

        where_sql = " AND ".join(where_clauses)

        # Count matching records
        count_query = text(f"SELECT COUNT(*) FROM customer_analytics WHERE {where_sql}")
        total = db.execute(count_query, params).scalar() or 0

        # Offset and pagination limits
        offset = (page - 1) * page_size
        params["limit"] = page_size
        params["offset"] = offset

        # Select customer records
        select_query = text(f"""
            SELECT 
                customer_id, first_name, last_name, age, gender, city, state,
                occupation, income, loyalty_tier,
                COALESCE(total_orders, 0) as total_orders,
                COALESCE(total_spending, 0) as total_spending,
                COALESCE(avg_order_value, 0) as avg_order_value
            FROM customer_analytics
            WHERE {where_sql}
            ORDER BY total_spending DESC, total_orders DESC
            LIMIT :limit OFFSET :offset
        """)

        rows = db.execute(select_query, params).fetchall()

        customer_items = []
        for r in rows:
            cid = r[0]
            # Attach segment from ML model assignment
            seg_name = get_customer_segment(cid) or "Recent / Low-Value"

            # Optional filter by ML segment if specified in query
            if segment and segment != "All" and seg_name.lower() != segment.lower():
                continue

            customer_items.append(
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
                    segment=seg_name,
                )
            )

        total_pages = math.ceil(total / page_size) if page_size > 0 else 1

        return PaginatedCustomersResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            customers=customer_items,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying customers: {str(exc)}",
        )


@router.get(
    "/{customer_id}",
    response_model=CustomerItem,
    summary="Get single customer details and analytics",
)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Fetches comprehensive demographic and spending analytics for a single customer ID.
    """
    query = text("""
        SELECT 
            customer_id, first_name, last_name, age, gender, city, state,
            occupation, income, loyalty_tier,
            COALESCE(total_orders, 0) as total_orders,
            COALESCE(total_spending, 0) as total_spending,
            COALESCE(avg_order_value, 0) as avg_order_value
        FROM customer_analytics
        WHERE customer_id = :customer_id
    """)
    row = db.execute(query, {"customer_id": customer_id.strip()}).fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' was not found in the database.",
        )

    cid = row[0]
    seg_name = get_customer_segment(cid) or "Recent / Low-Value"

    return CustomerItem(
        customer_id=cid,
        first_name=row[1],
        last_name=row[2],
        age=float(row[3]) if row[3] is not None else None,
        gender=row[4],
        city=row[5],
        state=row[6],
        occupation=row[7],
        income=float(row[8]) if row[8] is not None else None,
        loyalty_tier=row[9],
        total_orders=int(row[10]),
        total_spending=round(float(row[11]), 2),
        avg_order_value=round(float(row[12]), 2),
        segment=seg_name,
    )


@router.get(
    "/{customer_id}/orders",
    summary="Get customer order history and purchased items",
)
def get_customer_orders(customer_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full chronological order history with line items for a specific customer.
    """
    # Verify customer exists first
    check_cust = db.execute(
        text("SELECT customer_id FROM customers WHERE customer_id = :cid"),
        {"cid": customer_id.strip()}
    ).fetchone()

    if not check_cust:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found.",
        )

    # Fetch orders
    orders_query = text("""
        SELECT order_id, TO_CHAR(order_date, 'YYYY-MM-DD') as order_date, 
               order_status, sales_channel, payment_method, total_order_value
        FROM orders
        WHERE customer_id = :cid
        ORDER BY order_date DESC
    """)
    order_rows = db.execute(orders_query, {"cid": customer_id.strip()}).fetchall()

    if not order_rows:
        return {"customer_id": customer_id, "order_count": 0, "orders": []}

    order_ids = [r[0] for r in order_rows]

    # Fetch items for these orders
    items_query = text("""
        SELECT oi.order_id, oi.order_item_id, oi.product_id, p.product_name, p.category,
               oi.quantity, oi.unit_price, oi.discount, oi.item_total
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id IN :order_ids
    """)
    item_rows = db.execute(items_query, {"order_ids": tuple(order_ids)}).fetchall()

    # Map items to orders
    items_by_order = {}
    for ir in item_rows:
        oid = ir[0]
        if oid not in items_by_order:
            items_by_order[oid] = []
        items_by_order[oid].append({
            "order_item_id": ir[1],
            "product_id": ir[2],
            "product_name": ir[3],
            "category": ir[4],
            "quantity": int(ir[5]),
            "unit_price": float(ir[6]),
            "discount": float(ir[7]),
            "item_total": float(ir[8]),
        })

    result_orders = []
    for o in order_rows:
        oid = o[0]
        result_orders.append({
            "order_id": oid,
            "order_date": o[1],
            "order_status": o[2],
            "sales_channel": o[3],
            "payment_method": o[4],
            "total_order_value": float(o[5]),
            "items": items_by_order.get(oid, []),
        })

    return {
        "customer_id": customer_id,
        "order_count": len(result_orders),
        "orders": result_orders,
    }
