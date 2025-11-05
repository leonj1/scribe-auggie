"""
MySQL implementation of UserRepository.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.models.user import User
from app.repositories.interfaces import UserRepository

logger = logging.getLogger(__name__)


class MySQLUserRepository:
    """MySQL implementation of UserRepository interface."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, google_id: str, email: str, display_name: str, avatar_url: Optional[str] = None) -> User:
        """Create a new user."""
        try:
            user = User(
                google_id=google_id,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Created user: {user.email}")
            return user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create user {email}: {e}")
            raise ValueError(f"User with email {email} or Google ID {google_id} already exists")
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        return self.db.query(User).filter(User.google_id == google_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Updated user: {user.email}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
