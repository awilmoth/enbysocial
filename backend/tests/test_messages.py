import pytest
from fastapi import status
import json
from fastapi.testclient import TestClient

@pytest.fixture
def test_message():
    return {
        "content": "Test message content"
    }

@pytest.fixture
def another_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "anotheruser",
            "email": "another@example.com",
            "password": "testpass123"
        }
    )
    return response.json()

def test_send_message(authorized_client, test_user, another_user, test_message):
    message_data = {
        **test_message,
        "receiver_id": another_user["id"]
    }
    response = authorized_client.post("/messages/", json=message_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == test_message["content"]
    assert data["sender_id"] == test_user.id
    assert data["receiver_id"] == another_user["id"]
    assert data["is_read"] == False
    assert data["read_at"] is None

def test_send_message_invalid_receiver(authorized_client, test_message):
    message_data = {
        **test_message,
        "receiver_id": 99999  # Non-existent user
    }
    response = authorized_client.post("/messages/", json=message_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Receiver not found" in response.json()["detail"]

def test_get_messages(authorized_client, test_user, another_user, test_message):
    # Send a message first
    message_data = {
        **test_message,
        "receiver_id": another_user["id"]
    }
    authorized_client.post("/messages/", json=message_data)

    # Get messages
    response = authorized_client.get(f"/messages/", params={"other_user_id": another_user["id"]})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["content"] == test_message["content"]
    assert data[0]["sender_id"] == test_user.id
    assert data[0]["receiver_id"] == another_user["id"]

def test_mark_message_as_read(authorized_client, test_user, another_user, test_message):
    # Create a message from another user to test user
    another_client = TestClient(authorized_client.app)
    another_token = another_client.post(
        "/users/token",
        data={
            "username": "anotheruser",
            "password": "testpass123"
        }
    ).json()["access_token"]
    another_client.headers = {"Authorization": f"Bearer {another_token}"}

    message_data = {
        **test_message,
        "receiver_id": test_user.id
    }
    message_response = another_client.post("/messages/", json=message_data)
    message_id = message_response.json()["id"]

    # Mark message as read
    response = authorized_client.put(f"/messages/{message_id}/read")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Message marked as read"

    # Verify message is marked as read
    messages_response = authorized_client.get(f"/messages/", params={"other_user_id": another_user["id"]})
    message = next(m for m in messages_response.json() if m["id"] == message_id)
    assert message["is_read"] == True
    assert message["read_at"] is not None

def test_get_unread_messages(authorized_client, test_user, another_user, test_message):
    # Create messages from another user to test user
    another_client = TestClient(authorized_client.app)
    another_token = another_client.post(
        "/users/token",
        data={
            "username": "anotheruser",
            "password": "testpass123"
        }
    ).json()["access_token"]
    another_client.headers = {"Authorization": f"Bearer {another_token}"}

    # Send multiple messages
    message_data = {
        **test_message,
        "receiver_id": test_user.id
    }
    another_client.post("/messages/", json=message_data)
    another_client.post("/messages/", json=message_data)

    # Get unread messages
    response = authorized_client.get("/messages/unread")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(not message["is_read"] for message in data)
    assert all(message["receiver_id"] == test_user.id for message in data)

def test_websocket_connection(client, test_user_token):
    with client.websocket_connect(f"/messages/ws/{test_user_token}") as websocket:
        # Test sending a message through WebSocket
        websocket.send_text("Hello WebSocket!")
        data = websocket.receive_text()
        assert "You wrote: Hello WebSocket!" in data

def test_websocket_invalid_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/messages/ws/invalid-token") as websocket:
            pass
