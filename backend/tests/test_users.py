import pytest
from fastapi import status

def test_create_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "password_hash" not in data

def test_create_user_duplicate_username(client, test_user):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",  # Same as test_user fixture
            "email": "another@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already registered" in response.json()["detail"]

def test_create_user_duplicate_email(client, test_user):
    response = client.post(
        "/users/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",  # Same as test_user fixture
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

def test_login_user(client, test_user):
    response = client.post(
        "/users/token",
        data={
            "username": "testuser",
            "password": "testpass"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password(client, test_user):
    response = client.post(
        "/users/token",
        data={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(authorized_client, test_user):
    response = authorized_client.get("/users/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email

def test_get_current_user_unauthorized(client):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_user(authorized_client, test_user):
    response = authorized_client.put(
        "/users/me",
        json={
            "username": "updateduser",
            "email": "updated@example.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["email"] == "updated@example.com"

def test_update_user_duplicate_username(authorized_client, test_user):
    # Create another user first
    client = authorized_client.app
    client.post(
        "/users/register",
        json={
            "username": "anotheruser",
            "email": "another@example.com",
            "password": "testpass123"
        }
    )
    
    # Try to update test_user's username to the existing one
    response = authorized_client.put(
        "/users/me",
        json={
            "username": "anotheruser"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already taken" in response.json()["detail"]

def test_update_location(authorized_client):
    response = authorized_client.post(
        "/users/me/location",
        params={
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Location updated successfully"

    # Verify location was updated
    user_response = authorized_client.get("/users/me")
    assert user_response.status_code == status.HTTP_200_OK
    user_data = user_response.json()
    assert user_data["latitude"] == 40.7128
    assert user_data["longitude"] == -74.0060
