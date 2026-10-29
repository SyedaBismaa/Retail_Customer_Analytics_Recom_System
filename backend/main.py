"""
RetailIQ FastAPI Application Main Entrypoint.

This module initializes the FastAPI web application, configures CORS for the Next.js frontend,
registers database and model health check endpoints, and serves interactive OpenAPI docs at /docs.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import our database connection and model management modules
from src.database import get_db, check_db_connection
from src.segmentation import is_segmentation_loaded, load_segmentation_model
from src.recommendation import is_recommendation_loaded, load_recommendation_models
from src.schemas import (
    ApiStatusResponse,
    DatabaseHealthResponse,
    ModelsHealthResponse,
)

# Import our modular routers for Dashboard, Customers, Segments, and Recommendations
from backend.routers import dashboard, customers, segments, recommendations


# Step 1: Lifespan Event Handler.
# Runs code when the FastAPI server starts up and shuts down.
# Here we ensure that ML models are loaded into memory once at startup
# rather than repeatedly reloading files on every incoming HTTP request.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting RetailIQ API Server...")
    print("Loading Customer Segmentation artifact...")
    seg_ok = load_segmentation_model()
    print(f"Segmentation Model Ready: {seg_ok}")

    print("Loading Product Recommendation rules and popularity ranking...")
    rec_ok = load_recommendation_models()
    print(f"Recommendation Models Ready: {rec_ok}")

    yield  # Application runs and handles requests here

    print("Shutting down RetailIQ API Server...")


# Step 2: Create the FastAPI Application Instance.
# We configure title, description, version, and lifespan.
app = FastAPI(
    title="RetailIQ API",
    description="Backend API for Retail Customer Analytics & Personalized Recommendation System.",
    version="2.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Step 3: Configure Cross-Origin Resource Sharing (CORS).
# This allows our local Next.js frontend running on port 3000 to securely make API requests.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Health Endpoints (Phase 2)
# -----------------------------------------------------------------------------

@app.get(
    "/",
    response_model=ApiStatusResponse,
    tags=["System Health"],
    summary="Root API status and information",
)
def read_root():
    """
    Returns basic application status and points users to interactive /docs.
    """
    return ApiStatusResponse(
        name="RetailIQ API",
        status="online",
        version="2.4.0",
        documentation_url="/docs",
    )


@app.get(
    "/health/db",
    response_model=DatabaseHealthResponse,
    tags=["System Health"],
    summary="Check PostgreSQL database connectivity",
)
def health_database():
    """
    Checks whether the PostgreSQL database ('retail_analytics') is reachable,
    executing a test query and confirming table existence.
    """
    db_status = check_db_connection()
    if db_status.get("status") != "connected":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {db_status.get('error_message')}",
        )
    return DatabaseHealthResponse(
        status=db_status["status"],
        database=db_status["database"],
        host=db_status["host"],
        port=db_status["port"],
        ping=db_status["ping"],
        tables_found=db_status.get("tables_found", []),
    )


@app.get(
    "/health/models",
    response_model=ModelsHealthResponse,
    tags=["System Health"],
    summary="Check availability of serialized ML model artifacts",
)
def health_models():
    """
    Checks whether both the Customer Segmentation and Product Recommendation
    artifacts were successfully loaded into memory using Joblib.
    """
    seg_ready = is_segmentation_loaded()
    rec_ready = is_recommendation_loaded()
    overall_status = "healthy" if (seg_ready and rec_ready) else "degraded"

    return ModelsHealthResponse(
        status=overall_status,
        customer_segmentation_loaded=seg_ready,
        recommendation_rules_loaded=rec_ready,
        popularity_ranking_loaded=rec_ready,
        artifacts={
            "customer_segmentation": "models/customer_segmentation.pkl",
            "recommendation_rules": "models/recommendation_rules.pkl",
            "popularity_ranking": "models/popularity_ranking.pkl",
        },
    )


# -----------------------------------------------------------------------------
# Business API Routers (Phase 3)
# -----------------------------------------------------------------------------
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(segments.router)
app.include_router(recommendations.router)
