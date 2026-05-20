import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_activity_keys():
    # Arrange
    expected_activity = "Chess Club"
    with TestClient(app) as client:
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert expected_activity in data
        assert isinstance(data[expected_activity]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
        assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]

    with TestClient(app) as client:
        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": duplicate_email})

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = activities[activity_name]["participants"][0]

    with TestClient(app) as client:
        # Act
        response = client.post(f"/activities/{activity_name}/unregister", params={"email": email_to_remove})

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
        assert email_to_remove not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missingstudent@mergington.edu"

    with TestClient(app) as client:
        # Act
        response = client.post(f"/activities/{activity_name}/unregister", params={"email": missing_email})

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
