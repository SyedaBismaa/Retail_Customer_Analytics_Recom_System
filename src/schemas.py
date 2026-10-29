"""
Pydantic Schemas and Validation Models for RetailIQ API.

This module defines the response and request schemas to ensure:
- Strict type validation.
- Clean JSON responses.
- Accurate OpenAPI / Swagger documentation at /docs.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# Health Check Schemas
# -------------------------------------------------------------
class ApiStatusResponse(BaseModel):
    name: str = "RetailIQ API"
    status: str = "online"
    version: str = "2.4.0"
    documentation_url: str = "/docs"


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    host: str
    port: int
    ping: bool
    tables_found: List[str] = []
    error_message: Optional[str] = None


class ModelsHealthResponse(BaseModel):
    status: str
    customer_segmentation_loaded: bool
    recommendation_rules_loaded: bool
    popularity_ranking_loaded: bool
    artifacts: Dict[str, Any]


# -------------------------------------------------------------
# Dashboard Schemas
# -------------------------------------------------------------
class DashboardSummaryResponse(BaseModel):
    total_customers: int
    total_orders: int
    total_delivered_orders: int
    total_revenue: float
    avg_order_value: float
    delivered_ratio: float


class SalesTrendItem(BaseModel):
    period: str
    order_count: int
    revenue: float


class SalesTrendResponse(BaseModel):
    trends: List[SalesTrendItem]


class CategoryPerformanceItem(BaseModel):
    category: str
    revenue: float
    orders: int
    items_sold: int
    percentage_share: float


class CategoryPerformanceResponse(BaseModel):
    categories: List[CategoryPerformanceItem]


# -------------------------------------------------------------
# Customer Schemas
# -------------------------------------------------------------
class CustomerItem(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    age: Optional[float] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    income: Optional[float] = None
    loyalty_tier: Optional[str] = None
    total_orders: int
    total_spending: float
    avg_order_value: float
    segment: str


class PaginatedCustomersResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    customers: List[CustomerItem]


class OrderItemDetail(BaseModel):
    order_item_id: str
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_price: float
    discount: float
    item_total: float


class CustomerOrderDetail(BaseModel):
    order_id: str
    order_date: str
    order_status: str
    sales_channel: str
    payment_method: str
    total_order_value: float
    items: List[OrderItemDetail] = []


# -------------------------------------------------------------
# Segmentation Schemas
# -------------------------------------------------------------
class SegmentSummaryItem(BaseModel):
    segment_name: str
    badge: str
    color: str
    count: int
    percentage: float
    avg_recency_days: float
    avg_frequency_orders: float
    avg_monetary_spend: float
    description: str
    strategy: str


class SegmentsSummaryResponse(BaseModel):
    total_customers: int
    segments: List[SegmentSummaryItem]


# -------------------------------------------------------------
# Recommendation Schemas
# -------------------------------------------------------------
class ProductInfo(BaseModel):
    category: Optional[str] = "Retail"
    subcategory: Optional[str] = "General"
    brand: Optional[str] = "Standard"
    price: float = 0.0
    discount: float = 0.0
    rating: float = 4.0


class RecommendationItem(BaseModel):
    product_name: str
    confidence: Optional[float] = None
    lift: Optional[float] = None
    support: Optional[float] = None
    source: str  # 'Association Rule' or 'Popularity Fallback'
    product_info: ProductInfo


class CustomerRecommendationResponse(BaseModel):
    customer_id: str
    customer_name: str
    loyalty_tier: str
    customer_segment: str
    purchased_history_count: int
    previously_purchased_products: List[str]
    recommendations: List[RecommendationItem]


class RecommendationRequest(BaseModel):
    purchased_products: List[str]
    top_n: int = 5
