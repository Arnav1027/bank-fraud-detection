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
        print("Database connected successfully")
        
        existing_user = db.query(User).filter(User.email == "demo@test.com").first()
        if not existing_user:
            print("Creating default test user: demo@test.com")
            try:
                hashed_pwd = get_password_hash("SecureTest2026!")
                print(f"Password hashed successfully")
                
                test_user = User(
                    email="demo@test.com",
                    full_name="Demo User",
                    hashed_password=hashed_pwd,
                    role="analyst",
                    is_active=True,
                )
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
                print(f"✅ Test user created successfully! User ID: {test_user.id}")
            except Exception as hash_error:
                print(f"❌ Error creating test user: {hash_error}")
                db.rollback()
                raise
        else:
            print(f"✅ Test user already exists (ID: {existing_user.id})")
    except Exception as e:
        print(f"⚠️  Could not create test user: {e}")
        import traceback
        traceback.print_exc()
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


@app.get("/debug/check-user")
def check_test_user():
    """Debug endpoint to check if test user exists."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@test.com").first()
        if user:
            return {
                "exists": True,
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "message": "Test user found!"
            }
        else:
            return {
                "exists": False,
                "message": "Test user NOT found - login will fail"
            }
    finally:
        db.close()


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
