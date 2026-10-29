"""
Database Connection and Session Management Module for RetailIQ.

This module connects our FastAPI backend to the PostgreSQL database ('retail_analytics').
It uses SQLAlchemy to manage database connections and provide sessions to API routes.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

# Step 1: Locate and load the root .env file.
# Path(__file__).resolve().parent.parent finds the project root folder.
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Step 2: Read database credentials from environment variables.
# We read these safely without hardcoding passwords in our code.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "retail_analytics")

# Step 3: Construct the database connection URL safely using URL.create().
# URL.create automatically escapes special characters (like @, :, %) in the password.
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

# Step 4: Create one reusable database engine for the application.
# The engine manages the pool of connections to PostgreSQL efficiently.
# pool_pre_ping=True checks that connections are still alive before handing them out.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Step 5: Create a sessionmaker factory.
# Each time a request comes into an API endpoint, a new Session is created from this factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for SQLAlchemy ORM models if needed.
Base = declarative_base()


# Step 6: FastAPI Database Dependency (Dependency Injection).
# This generator function provides a database session to an endpoint.
# The 'finally' block guarantees that the database connection is always closed
# and returned to the connection pool, preventing connection leaks.
def get_db():
    """
    Dependency that yields a database session for a single request,
    then automatically closes the session when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Step 7: Database Health Check Helper.
# Runs a quick query (SELECT 1) to verify PostgreSQL is reachable and functioning.
def check_db_connection() -> dict:
    """
    Checks if PostgreSQL can be reached and returns connectivity status.
    Returns:
        dict: Status information and table verification details.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            # Verify existing tables exist
            tables = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )).fetchall()
            table_list = [row[0] for row in tables]
            
            return {
                "status": "connected",
                "database": DB_NAME,
                "host": DB_HOST,
                "port": DB_PORT,
                "ping": result == 1,
                "tables_found": table_list,
            }
    except Exception as exc:
        return {
            "status": "error",
            "database": DB_NAME,
            "host": DB_HOST,
            "port": DB_PORT,
            "error_message": str(exc),
        }
