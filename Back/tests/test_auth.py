import pytest
from fastapi import status
from app.models import UserRole


class TestAuthentication:
    def test_login_success(self, client, admin_user):
        """Test successful login"""
        response = client.post("/api/token/", data={
            "username": admin_user.email,
            "password": "testpassword"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post("/api/token/", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_token(self, client, admin_token):
        """Test accessing protected endpoint with valid token"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/shareholders/", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/shareholders/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/shareholders/", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_only_endpoint_with_shareholder(self, client, shareholder_token):
        """Test admin-only endpoint with shareholder token"""
        headers = {"Authorization": f"Bearer {shareholder_token}"}
        response = client.get("/api/shareholders/", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_shareholder_endpoint_with_admin(self, client, admin_token):
        """Test shareholder endpoint with admin token"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/shareholders/me", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserRoles:
    def test_admin_user_creation(self, db_session):
        """Test admin user creation"""
        from app.models import User
        from app.auth import get_password_hash
        
        admin_user = User(
            email="admin@test.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.ADMIN
        )
        db_session.add(admin_user)
        db_session.commit()
        
        assert admin_user.role == UserRole.ADMIN
        assert admin_user.is_active is True
    
    def test_shareholder_user_creation(self, db_session):
        """Test shareholder user creation"""
        from app.models import User
        from app.auth import get_password_hash
        
        shareholder_user = User(
            email="shareholder@test.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.SHAREHOLDER
        )
        db_session.add(shareholder_user)
        db_session.commit()
        
        assert shareholder_user.role == UserRole.SHAREHOLDER
        assert shareholder_user.is_active is True 