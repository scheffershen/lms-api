import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture
def mock_db_cursor():
    cursor = AsyncMock()
    cursor.fetchone = MagicMock()
    return cursor

@pytest.fixture
def mock_db_connection(mock_db_cursor):
    conn = AsyncMock()
    conn.cursor.return_value.__aenter__.return_value = mock_db_cursor
    return conn

@pytest.mark.asyncio
async def test_login_success(mock_db_connection):
    # Mock user data
    test_user = {
        "id": 1,
        "email": "test@example.com",
        "password": get_password_hash("testpassword")
    }
    
    # Setup mock DB response
    with patch("app.api.v1.endpoints.auth.get_db_connection", return_value=mock_db_connection):
        mock_db_connection.cursor().__aenter__().fetchone.return_value = [
            test_user["id"],
            test_user["email"],
            test_user["password"]
        ]
        
        # Test login
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": test_user["email"],
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user["email"]

@pytest.mark.asyncio
async def test_login_invalid_credentials(mock_db_connection):
    # Setup mock DB response - user not found
    with patch("app.api.v1.endpoints.auth.get_db_connection", return_value=mock_db_connection):
        mock_db_connection.cursor().__aenter__().fetchone.return_value = None
        
        # Test login with invalid credentials
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password" 