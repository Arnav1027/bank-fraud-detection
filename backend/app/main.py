"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.models import Base, User
from app.core.security import get_password_hash

# Initialize database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    print("Starting up Bank Fraud Detection API...")
    
    # Create default test user if it doesn't exist
    db = None
    try:
        db = SessionLocal()
        existing_user = db.query(User).filter(User.email == "demo@test.com").first()
        if not existing_user:
            print("Creating default test user: demo@test.com")
            test_user = User(
                email="demo@test.com",
                full_name="Demo User",
                hashed_password=get_password_hash("SecureTest2026!"),
                role="analyst",
                is_active=True,
            )
            db.add(test_user)
            db.commit()
            print("✅ Test user created successfully!")
        else:
            print("✅ Test user already exists")
    except Exception as e:
        print(f"⚠️  Could not create test user: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()
    
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-time and batch fraud detection API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "bank-fraud-detection"}


# Include routers (imported after app creation to avoid circular imports)
from app.api.routes import auth, transactions, analytics
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(transactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Bank Fraud Detection API",
        "docs": "/docs",
        "version": "1.0.0",
    }
