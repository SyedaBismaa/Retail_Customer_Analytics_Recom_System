"""
Dashboard Endpoints Router for RetailIQ.

This module queries PostgreSQL for:
- Executive KPIs: Total customers, total orders, completed sales revenue, and average order value.
- Monthly Sales Velocity: Time-series order counts and delivered revenue trends.
- Category Breakdown: Performance metrics grouped by product categories.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import (
    DashboardSummaryResponse,
    SalesTrendResponse,
    SalesTrendItem,
    CategoryPerformanceResponse,
    CategoryPerformanceItem,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Get executive dashboard summary KPIs",
)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Computes true executive KPI metrics from PostgreSQL:
    - total_customers: Count of unique customers.
    - total_orders: Count of all orders placed across all fulfillment statuses.
    - total_delivered_orders: Only orders successfully fulfilled ('Delivered').
    - total_revenue: Sum of total_order_value for delivered orders.
    - avg_order_value: Mean order value of completed sales.
    - delivered_ratio: Fulfillment rate percentage.
    """
    try:
        # 1. Count total customer base
        total_customers = db.execute(text("SELECT COUNT(*) FROM customers")).scalar() or 0

        # 2. Query order aggregates (overall orders and delivered orders)
        order_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) as delivered_orders,
                COALESCE(SUM(CASE WHEN order_status = 'Delivered' THEN total_order_value ELSE 0 END), 0) as total_revenue,
                COALESCE(AVG(CASE WHEN order_status = 'Delivered' THEN total_order_value ELSE NULL END), 0) as avg_order_value
            FROM orders
        """)).mappings().first()

        total_orders = order_stats["total_orders"]
        delivered_orders = order_stats["delivered_orders"]
        total_revenue = float(order_stats["total_revenue"])
        avg_order_value = float(order_stats["avg_order_value"])

        delivered_ratio = round((delivered_orders / total_orders * 100), 2) if total_orders > 0 else 0.0

        return DashboardSummaryResponse(
            total_customers=total_customers,
            total_orders=total_orders,
            total_delivered_orders=delivered_orders,
            total_revenue=round(total_revenue, 2),
            avg_order_value=round(avg_order_value, 2),
            delivered_ratio=delivered_ratio,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard summary metrics: {str(exc)}"
        )


@router.get(
    "/sales-trend",
    response_model=SalesTrendResponse,
    summary="Get monthly revenue and order velocity trends",
)
def get_sales_trend(db: Session = Depends(get_db)):
    """
    Aggregates completed sales by year and month from the PostgreSQL orders table.
    Provides chronological sales data for charts.
    """
    try:
        # Group delivered orders by YYYY-MM
        trend_query = text("""
            SELECT 
                TO_CHAR(order_date, 'YYYY-MM') AS period,
                COUNT(*) AS order_count,
                COALESCE(SUM(total_order_value), 0) AS revenue
            FROM orders
            WHERE order_status = 'Delivered'
            GROUP BY TO_CHAR(order_date, 'YYYY-MM')
            ORDER BY period ASC
        """)
        rows = db.execute(trend_query).fetchall()

        trend_items = [
            SalesTrendItem(
                period=row[0],
                order_count=int(row[1]),
                revenue=round(float(row[2]), 2),
            )
            for row in rows
        ]

        return SalesTrendResponse(trends=trend_items)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sales trends: {str(exc)}"
        )


@router.get(
    "/category-performance",
    response_model=CategoryPerformanceResponse,
    summary="Get category revenue, volume, and market share",
)
def get_category_performance(db: Session = Depends(get_db)):
    """
    Joins order_items, products, and orders to compute sales volume and revenue by category.
    """
    try:
        cat_query = text("""
            SELECT 
                p.category,
                COALESCE(SUM(oi.item_total), 0) AS revenue,
                COUNT(DISTINCT oi.order_id) AS orders,
                COALESCE(SUM(oi.quantity), 0) AS items_sold
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_status = 'Delivered'
            GROUP BY p.category
            ORDER BY revenue DESC
        """)
        rows = db.execute(cat_query).fetchall()

        total_cat_revenue = sum(float(r[1]) for r in rows)

        cat_items = []
        for r in rows:
            rev = float(r[1])
            share = round((rev / total_cat_revenue * 100), 2) if total_cat_revenue > 0 else 0.0
            cat_items.append(
                CategoryPerformanceItem(
                    category=r[0],
                    revenue=round(rev, 2),
                    orders=int(r[2]),
                    items_sold=int(r[3]),
                    percentage_share=share,
                )
            )

        return CategoryPerformanceResponse(categories=cat_items)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category performance: {str(exc)}"
        )
