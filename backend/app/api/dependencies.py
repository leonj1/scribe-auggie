"""
FastAPI dependencies for authentication and database access.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.repositories.mysql_user_repository import MySQLUserRepository
from app.repositories.mysql_recording_repository import MySQLRecordingRepository
from app.models.user import User

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repository = MySQLUserRepository(db)
    user = user_repository.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_user_repository(db: Session = Depends(get_db)) -> MySQLUserRepository:
    """
    Dependency to get user repository.
    
    Args:
        db: Database session
        
    Returns:
        User repository instance
    """
    return MySQLUserRepository(db)


def get_recording_repository(db: Session = Depends(get_db)) -> MySQLRecordingRepository:
    """
    Dependency to get recording repository.
    
    Args:
        db: Database session
        
    Returns:
        Recording repository instance
    """
    return MySQLRecordingRepository(db)
