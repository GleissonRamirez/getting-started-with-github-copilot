from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect some known activities from the fixture data
    assert "Chess Club" in data


def test_signup_and_unregister_flow(client):
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    body = res.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]

    # Unregister
    res2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res2.status_code == 200
    body2 = res2.json()
    assert "Unregistered" in body2.get("message", "")
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent(client):
    activity = "Programming Class"
    email = "nonexistent@example.com"
    # Ensure email not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 404
    data = res.json()
    assert data.get("detail") in ("Participant not found",)
