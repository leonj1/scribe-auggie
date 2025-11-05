"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.api.dependencies import get_user_repository
from app.repositories.mysql_user_repository import MySQLUserRepository

router = APIRouter()


class GoogleTokenRequest(BaseModel):
    """Request model for Google token authentication."""
    id_token: str


class AuthResponse(BaseModel):
    """Response model for successful authentication."""
    access_token: str
    token_type: str
    user: dict


@router.post("/google/token", response_model=AuthResponse)
async def authenticate_with_google_token(
    token_request: GoogleTokenRequest,
    user_repository: MySQLUserRepository = Depends(get_user_repository)
):
    """
    Authenticate user with Google ID token.
    
    Args:
        token_request: Google ID token request
        user_repository: User repository dependency
        
    Returns:
        Authentication response with JWT token and user info
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(user_repository)
    
    # Verify Google token and get user info
    google_user_info = await auth_service.verify_google_token(token_request.id_token)
    
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    
    # Authenticate or create user
    user = await auth_service.authenticate_or_create_user(google_user_info)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user"
        )
    
    # Create JWT token
    access_token = auth_service.create_user_token(user)
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=user.to_dict()
    )


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth2 login flow.
    
    Returns:
        Redirect to Google OAuth2 authorization URL
    """
    # This endpoint is primarily for documentation
    # In practice, the frontend will handle the Google OAuth2 flow
    return {
        "message": "Use Google OAuth2 client library in frontend to obtain ID token",
        "endpoint": "/auth/google/token",
        "method": "POST",
        "body": {
            "id_token": "google_id_token_here"
        }
    }


@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_user_repository)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user dependency
        
    Returns:
        Current user information
    """
    from app.api.dependencies import get_current_user
    # This will be properly implemented when we have the dependency working
    return {"message": "User info endpoint - requires authentication"}


@router.post("/logout")
async def logout():
    """
    Logout endpoint (stateless - client should discard token).
    
    Returns:
        Logout confirmation
    """
    return {"message": "Logged out successfully. Please discard your access token."}
