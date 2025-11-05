"""
Authentication service for Google OAuth2 and JWT management.
"""
from typing import Optional, Dict, Any
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.httpx_client import AsyncOAuth2Client
import httpx
import logging

from app.core.config import settings
from app.core.security import create_access_token
from app.repositories.mysql_user_repository import MySQLUserRepository
from app.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, user_repository: MySQLUserRepository):
        self.user_repository = user_repository
        self.oauth = OAuth()
        
        # Configure Google OAuth2
        self.oauth.register(
            name='google',
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
    
    async def get_google_auth_url(self, redirect_uri: str) -> str:
        """
        Generate Google OAuth2 authorization URL.
        
        Args:
            redirect_uri: The redirect URI for the OAuth2 flow
            
        Returns:
            Authorization URL string
        """
        google = self.oauth.create_client('google')
        authorization_url, state = google.create_authorization_url(
            'https://accounts.google.com/o/oauth2/auth',
            redirect_uri=redirect_uri
        )
        return authorization_url
    
    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google ID token and extract user information.
        
        Args:
            token: Google ID token
            
        Returns:
            User information dictionary or None if invalid
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
                )
                
                if response.status_code == 200:
                    user_info = response.json()
                    
                    # Verify the token is for our application
                    if user_info.get('aud') != settings.google_client_id:
                        logger.warning("Invalid audience in Google token")
                        return None
                    
                    return {
                        'google_id': user_info.get('sub'),
                        'email': user_info.get('email'),
                        'display_name': user_info.get('name'),
                        'avatar_url': user_info.get('picture')
                    }
                else:
                    logger.warning(f"Google token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            return None
    
    async def authenticate_or_create_user(self, google_user_info: Dict[str, Any]) -> Optional[User]:
        """
        Authenticate existing user or create new user from Google info.
        
        Args:
            google_user_info: User information from Google
            
        Returns:
            User object or None if authentication failed
        """
        try:
            google_id = google_user_info.get('google_id')
            email = google_user_info.get('email')
            
            if not google_id or not email:
                logger.error("Missing required Google user information")
                return None
            
            # Try to find existing user by Google ID
            user = self.user_repository.get_user_by_google_id(google_id)
            
            if user:
                # Update user information if needed
                updated_user = self.user_repository.update_user(
                    user.id,
                    display_name=google_user_info.get('display_name', user.display_name),
                    avatar_url=google_user_info.get('avatar_url', user.avatar_url)
                )
                logger.info(f"Authenticated existing user: {email}")
                return updated_user
            else:
                # Create new user
                user = self.user_repository.create_user(
                    google_id=google_id,
                    email=email,
                    display_name=google_user_info.get('display_name', ''),
                    avatar_url=google_user_info.get('avatar_url')
                )
                logger.info(f"Created new user: {email}")
                return user
                
        except Exception as e:
            logger.error(f"Error authenticating/creating user: {e}")
            return None
    
    def create_user_token(self, user: User) -> str:
        """
        Create JWT token for authenticated user.
        
        Args:
            user: Authenticated user
            
        Returns:
            JWT token string
        """
        token_data = {
            "sub": user.id,
            "email": user.email,
            "display_name": user.display_name
        }
        return create_access_token(token_data)
