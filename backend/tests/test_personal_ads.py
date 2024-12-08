import pytest
from fastapi import status
from datetime import datetime

@pytest.fixture
def test_personal_ad(test_user):
    return {
        "content": "Test personal ad",
        "latitude": 40.7128,
        "longitude": -74.0060
    }

def test_create_personal_ad(authorized_client, test_user, test_personal_ad):
    # First update user location
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )

    response = authorized_client.post(
        "/personal-ads/",
        json=test_personal_ad
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == test_personal_ad["content"]
    assert data["latitude"] == test_personal_ad["latitude"]
    assert data["longitude"] == test_personal_ad["longitude"]
    assert data["user_id"] == test_user.id
    assert data["is_active"] == True

def test_create_personal_ad_no_location(authorized_client, test_personal_ad):
    response = authorized_client.post(
        "/personal-ads/",
        json=test_personal_ad
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "User location not set" in response.json()["detail"]

def test_get_personal_ads(authorized_client, test_user, test_personal_ad):
    # Create a personal ad first
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )
    authorized_client.post("/personal-ads/", json=test_personal_ad)

    response = authorized_client.get("/personal-ads/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["content"] == test_personal_ad["content"]

def test_get_personal_ads_by_distance(authorized_client, test_user, test_personal_ad):
    # Create a personal ad first
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )
    authorized_client.post("/personal-ads/", json=test_personal_ad)

    # Update user location to be 50 miles away
    new_location = {
        "latitude": test_personal_ad["latitude"] + 0.7,  # Roughly 50 miles
        "longitude": test_personal_ad["longitude"]
    }
    authorized_client.post(
        "/users/me/location",
        params=new_location
    )

    # Test within range (60 miles)
    response = authorized_client.get("/personal-ads/", params={"distance": 60})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0

    # Test out of range (40 miles)
    response = authorized_client.get("/personal-ads/", params={"distance": 40})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0

def test_get_specific_personal_ad(authorized_client, test_user, test_personal_ad):
    # Create a personal ad first
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )
    create_response = authorized_client.post("/personal-ads/", json=test_personal_ad)
    ad_id = create_response.json()["id"]

    response = authorized_client.get(f"/personal-ads/{ad_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == ad_id
    assert data["content"] == test_personal_ad["content"]

def test_update_personal_ad(authorized_client, test_user, test_personal_ad):
    # Create a personal ad first
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )
    create_response = authorized_client.post("/personal-ads/", json=test_personal_ad)
    ad_id = create_response.json()["id"]

    updated_content = "Updated test personal ad"
    response = authorized_client.put(
        f"/personal-ads/{ad_id}",
        json={"content": updated_content}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == updated_content

def test_delete_personal_ad(authorized_client, test_user, test_personal_ad):
    # Create a personal ad first
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )
    create_response = authorized_client.post("/personal-ads/", json=test_personal_ad)
    ad_id = create_response.json()["id"]

    response = authorized_client.delete(f"/personal-ads/{ad_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Personal ad deleted successfully"

    # Verify it's not returned in active ads
    get_response = authorized_client.get("/personal-ads/")
    assert ad_id not in [ad["id"] for ad in get_response.json()]

def test_get_user_personal_ads(authorized_client, test_user, test_personal_ad):
    # Create a personal ad first
    authorized_client.post(
        "/users/me/location",
        params={
            "latitude": test_personal_ad["latitude"],
            "longitude": test_personal_ad["longitude"]
        }
    )
    authorized_client.post("/personal-ads/", json=test_personal_ad)

    response = authorized_client.get(f"/personal-ads/user/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(ad["user_id"] == test_user.id for ad in data)
