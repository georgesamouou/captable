import pytest
from fastapi import status


class TestShareholderEndpoints:
    def test_get_all_shareholders_admin(self, client, admin_token):
        """Test admin can get all shareholders"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/shareholders/", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_shareholders_unauthorized(self, client):
        """Test unauthorized access to shareholders list"""
        response = client.get("/api/shareholders/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_shareholder_admin(self, client, admin_token):
        """Test admin can create shareholder"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        shareholder_data = {
            "email": "newshareholder@example.com",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+1234567890",
            "address": "456 Oak St, City, Country",
            "tax_id": "TAX789012"
        }
        
        response = client.post("/api/shareholders/", json=shareholder_data, headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert "id" in data
    
    def test_create_shareholder_duplicate_email(self, client, admin_token, shareholder_user):
        """Test creating shareholder with duplicate email"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        shareholder_data = {
            "email": shareholder_user.email,
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "+1234567890",
            "address": "456 Oak St, City, Country",
            "tax_id": "TAX789012"
        }
        
        response = client.post("/api/shareholders/", json=shareholder_data, headers=headers)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_my_profile_shareholder(self, client, shareholder_token):
        """Test shareholder can get their own profile"""
        headers = {"Authorization": f"Bearer {shareholder_token}"}
        response = client.get("/api/shareholders/me", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "first_name" in data
        assert "last_name" in data
    
    def test_get_my_profile_not_found(self, client, admin_token):
        """Test getting profile when shareholder profile doesn't exist"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/shareholders/me", headers=headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestShareholderValidation:
    def test_create_shareholder_invalid_email(self, client, admin_token):
        """Test creating shareholder with invalid email"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        shareholder_data = {
            "email": "invalid-email",
            "password": "password123",
            "first_name": "Jane",
            "last_name": "Smith"
        }
        
        response = client.post("/api/shareholders/", json=shareholder_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_shareholder_missing_required_fields(self, client, admin_token):
        """Test creating shareholder with missing required fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        shareholder_data = {
            "email": "test@example.com",
            "password": "password123"
            # Missing first_name and last_name
        }
        
        response = client.post("/api/shareholders/", json=shareholder_data, headers=headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 