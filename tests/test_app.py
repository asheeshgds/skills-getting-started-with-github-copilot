import copy
import pytest

from src import app
from fastapi.testclient import TestClient

# keep original state for resetting between tests
INITIAL_ACTIVITIES = copy.deepcopy(app.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory database before each test."""
    app.activities = copy.deepcopy(INITIAL_ACTIVITIES)

@pytest.fixture
def client():
    return TestClient(app.app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should at least contain some known activity keys
    assert "Chess Club" in data
    assert isinstance(data, dict)


def test_signup_success(client):
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Signed up")
    # ensure participant appears
    assert email in app.activities[activity]["participants"]


def test_signup_already_registered(client):
    activity = "Chess Club"
    email = "michael@mergington.edu"  # already in initial data
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is already signed up for this activity"


def test_signup_activity_not_found(client):
    resp = client.post("/activities/Invalid/signup?email=test@mergington.edu")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"


def test_remove_participant_success(client):
    activity = "Chess Club"
    email = "michael@mergington.edu"
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Removed {email} from {activity}"
    assert email not in app.activities[activity]["participants"]


def test_remove_participant_not_registered(client):
    activity = "Chess Club"
    email = "nosuch@mergington.edu"
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student is not registered for this activity"


def test_remove_participant_activity_not_found(client):
    resp = client.delete("/activities/Invalid/participants?email=foo@bar.com")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Activity not found"
