"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role="analyst",  # Default role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token = create_access_token(data={"sub": db_user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(db_user),
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Demo mode: Authenticate user and return JWT token. Creates user if doesn't exist."""
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    # If user doesn't exist, create them (demo mode)
    if not user:
        print(f"Demo mode: Creating new user for {credentials.email}")
        try:
            user = User(
                email=credentials.email,
                full_name=credentials.email.split("@")[0],  # Use email prefix as name
                hashed_password=get_password_hash(credentials.password),
                role="analyst",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ User created: {user.email}")
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user",
            )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create access token (no password verification in demo mode)
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }
