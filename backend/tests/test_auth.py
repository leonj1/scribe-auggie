"""
Tests for authentication endpoints.
"""
import pytest
from unittest.mock import patch, AsyncMock


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_google_login_info(self, client):
        """Test Google login info endpoint."""
        response = client.get("/auth/google/login")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoint" in data
        assert data["endpoint"] == "/auth/google/token"
    
    @patch('app.services.auth_service.AuthService.verify_google_token')
    @patch('app.services.auth_service.AuthService.authenticate_or_create_user')
    def test_google_token_authentication_success(
        self, 
        mock_auth_user, 
        mock_verify_token, 
        client, 
        test_user
    ):
        """Test successful Google token authentication."""
        # Mock the service methods
        mock_verify_token.return_value = {
            'google_id': test_user.google_id,
            'email': test_user.email,
            'display_name': test_user.display_name,
            'avatar_url': test_user.avatar_url
        }
        mock_auth_user.return_value = test_user
        
        response = client.post("/auth/google/token", json={
            "id_token": "mock_google_id_token"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    @patch('app.services.auth_service.AuthService.verify_google_token')
    def test_google_token_authentication_invalid_token(
        self, 
        mock_verify_token, 
        client
    ):
        """Test Google token authentication with invalid token."""
        mock_verify_token.return_value = None
        
        response = client.post("/auth/google/token", json={
            "id_token": "invalid_token"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid Google token"
    
    def test_google_token_authentication_missing_token(self, client):
        """Test Google token authentication with missing token."""
        response = client.post("/auth/google/token", json={})
        
        assert response.status_code == 422  # Validation error
    
    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.post("/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower()


class TestAuthService:
    """Test authentication service."""
    
    @pytest.mark.asyncio
    async def test_verify_google_token_success(self):
        """Test successful Google token verification."""
        from app.services.auth_service import AuthService
        from app.repositories.mysql_user_repository import MySQLUserRepository
        
        # This would require mocking the HTTP request to Google
        # For now, we'll test the structure
        auth_service = AuthService(None)
        assert hasattr(auth_service, 'verify_google_token')
        assert hasattr(auth_service, 'authenticate_or_create_user')
        assert hasattr(auth_service, 'create_user_token')
    
    def test_create_user_token(self, test_user):
        """Test JWT token creation."""
        from app.services.auth_service import AuthService
        
        auth_service = AuthService(None)
        token = auth_service.create_user_token(test_user)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        from app.core.security import verify_token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == test_user.id
        assert payload["email"] == test_user.email
