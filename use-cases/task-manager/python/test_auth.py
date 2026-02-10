"""
Test suite for the JWT Auth API.

Tests the complete authentication flow:
  Register → Login → Access protected endpoint → Handle errors

Run with: python test_auth.py
"""

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


# ─── REGISTRATION TESTS ─────────────────────────────────────

def test_register_new_user():
    """POST /register should create a new user account."""
    response = client.post("/register", json={
        "username": "whitney",
        "email": "whitney@example.com",
        "full_name": "Whitney Test",
        "password": "secure123",
    })
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "whitney"
    assert data["email"] == "whitney@example.com"
    assert "hashed_password" not in data  # Password hash must NOT leak
    assert "password" not in data          # Plain password must NOT leak
    print("✅ Registered new user (password not in response)")


def test_register_duplicate_username():
    """POST /register with existing username should return 409."""
    response = client.post("/register", json={
        "username": "whitney",
        "email": "other@example.com",
        "password": "password123",
    })
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]
    print("✅ Duplicate username rejected (409)")


def test_register_validation_errors():
    """POST /register with invalid data should return 422."""
    # Missing required fields
    response = client.post("/register", json={})
    assert response.status_code == 422
    print("✅ Missing fields rejected (422)")

    # Password too short
    response = client.post("/register", json={
        "username": "testuser2",
        "email": "test@example.com",
        "password": "short",
    })
    assert response.status_code == 422
    print("✅ Short password rejected (422)")


# ─── LOGIN TESTS ─────────────────────────────────────────────

def test_login_success():
    """POST /token should return a JWT access token."""
    response = client.post("/token", data={
        "username": "whitney",
        "password": "secure123",
    })
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20  # JWT tokens are long strings
    print(f"✅ Login successful (token: {data['access_token'][:30]}...)")
    return data["access_token"]


def test_login_wrong_password():
    """POST /token with wrong password should return 401."""
    response = client.post("/token", data={
        "username": "whitney",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    print("✅ Wrong password rejected (401)")


def test_login_nonexistent_user():
    """POST /token with unknown username should return 401."""
    response = client.post("/token", data={
        "username": "nobody",
        "password": "anything",
    })
    assert response.status_code == 401
    print("✅ Unknown user rejected (401)")


# ─── PROTECTED ENDPOINT TESTS ────────────────────────────────

def test_get_profile_with_token(token: str):
    """GET /users/me with valid token should return user profile."""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "whitney"
    assert data["email"] == "whitney@example.com"
    assert "hashed_password" not in data  # NEVER leak password hash
    print("✅ Profile retrieved with valid token")


def test_get_profile_no_token():
    """GET /users/me without a token should return 401."""
    response = client.get("/users/me")
    assert response.status_code == 401
    print("✅ No token → 401 Unauthorized")


def test_get_profile_invalid_token():
    """GET /users/me with a bad token should return 401."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer this-is-not-a-valid-token"},
    )
    assert response.status_code == 401
    print("✅ Invalid token → 401 Unauthorized")


def test_get_items_with_token(token: str):
    """GET /users/me/items with valid token should return items."""
    response = client.get(
        "/users/me/items",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["owner"] == "whitney"
    assert len(data["items"]) == 2
    print("✅ Protected items endpoint works with token")


# ─── ROOT TEST ───────────────────────────────────────────────

def test_root():
    """GET / should return welcome message (no auth required)."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    print("✅ Root endpoint works (no auth required)")


# ─── RUN ALL TESTS ───────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("Auth API — Test Suite")
    print("=" * 55)
    print()

    print("--- REGISTRATION ---")
    test_register_new_user()
    test_register_duplicate_username()
    test_register_validation_errors()
    print()

    print("--- LOGIN ---")
    token = test_login_success()
    test_login_wrong_password()
    test_login_nonexistent_user()
    print()

    print("--- PROTECTED ENDPOINTS ---")
    test_get_profile_with_token(token)
    test_get_profile_no_token()
    test_get_profile_invalid_token()
    test_get_items_with_token(token)
    print()

    print("--- PUBLIC ENDPOINTS ---")
    test_root()
    print()

    print("=" * 55)
    print("All tests passed! ✅")
    print("=" * 55)
