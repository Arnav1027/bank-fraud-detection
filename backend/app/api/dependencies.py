"""FastAPI dependencies."""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.core.security import decode_token
from app.models import User


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="authorization"),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token in Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        
        if len(parts) != 2:
            raise ValueError("Invalid header format")
            
        scheme, token = parts
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        payload = decode_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Convert to int if it's a string
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None, alias="authorization"),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current authenticated user from JWT token, or None if no token provided (demo mode)."""
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        
        if len(parts) != 2:
            return None
            
        scheme, token = parts
        if scheme.lower() != "bearer":
            return None
        
        payload = decode_token(token)
        
        if payload is None:
            return None
    except Exception:
        return None

    user_id: int = payload.get("sub")
    if user_id is None:
        return None
    
    # Convert to int if it's a string
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    if not user.is_active:
        return None

    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verify current user is admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
