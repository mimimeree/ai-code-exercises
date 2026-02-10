"""
Test script for the To-Do List API.

Uses FastAPI's built-in TestClient, which lets us test endpoints
without actually starting a server. It simulates HTTP requests
and returns responses we can assert against.

This is similar to Flask's test_client() from Exercise 5.

Run with: python -m pytest test_todos.py -v
Or just:  python test_todos.py
"""

from fastapi.testclient import TestClient
from app.main import app


# TestClient wraps our FastAPI app so we can make fake HTTP requests
client = TestClient(app)


def test_root_endpoint():
    """GET / should return welcome message and endpoint list."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Welcome to the To-Do List API"
    assert "endpoints" in data
    print("✅ Root endpoint works")


def test_create_todo():
    """POST /todos/ should create a new to-do item."""
    new_todo = {
        "title": "Learn FastAPI",
        "description": "Complete exercise 17",
        "due_date": "2026-02-15"
    }
    response = client.post("/todos/", json=new_todo)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Learn FastAPI"
    assert data["description"] == "Complete exercise 17"
    assert data["due_date"] == "2026-02-15"
    assert data["status"] == "pending"
    assert "id" in data
    print(f"✅ Created to-do item (ID: {data['id']})")
    return data["id"]


def test_create_todo_minimal():
    """POST /todos/ with only title (description and due_date optional)."""
    response = client.post("/todos/", json={"title": "Quick task"})
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Quick task"
    assert data["description"] is None
    assert data["due_date"] is None
    print(f"✅ Created minimal to-do (ID: {data['id']})")
    return data["id"]


def test_create_todo_validation_error():
    """POST /todos/ with invalid data should return 422."""
    # Missing required 'title' field
    response = client.post("/todos/", json={})
    assert response.status_code == 422
    print("✅ Validation error caught (missing title)")

    # Title too short (empty string)
    response = client.post("/todos/", json={"title": ""})
    assert response.status_code == 422
    print("✅ Validation error caught (empty title)")


def test_list_todos():
    """GET /todos/ should return all to-do items."""
    response = client.get("/todos/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # We created at least 2 items above
    print(f"✅ Listed {len(data)} to-do items")


def test_get_single_todo(todo_id: int):
    """GET /todos/{id} should return a specific item."""
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == todo_id
    print(f"✅ Retrieved to-do item {todo_id}: '{data['title']}'")


def test_get_nonexistent_todo():
    """GET /todos/9999 should return 404."""
    response = client.get("/todos/9999")
    assert response.status_code == 404

    data = response.json()
    assert "not found" in data["detail"].lower()
    print("✅ 404 returned for nonexistent item")


def test_update_todo(todo_id: int):
    """PUT /todos/{id} should update specified fields only."""
    # Update only the description — title should stay the same
    response = client.put(
        f"/todos/{todo_id}",
        json={"description": "Updated description!"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["description"] == "Updated description!"
    assert data["title"] == "Learn FastAPI"  # Unchanged
    assert data["status"] == "pending"       # Unchanged
    print(f"✅ Updated to-do {todo_id} (partial update)")


def test_complete_todo(todo_id: int):
    """PUT /todos/{id}/complete should mark item as completed."""
    response = client.put(f"/todos/{todo_id}/complete")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    print(f"✅ Marked to-do {todo_id} as completed")


def test_filter_by_status():
    """GET /todos/?status=pending should return only pending items."""
    # Get pending items
    response = client.get("/todos/?status=pending")
    assert response.status_code == 200
    pending = response.json()
    assert all(item["status"] == "pending" for item in pending)
    print(f"✅ Filtered pending: {len(pending)} items")

    # Get completed items
    response = client.get("/todos/?status=completed")
    assert response.status_code == 200
    completed = response.json()
    assert all(item["status"] == "completed" for item in completed)
    print(f"✅ Filtered completed: {len(completed)} items")


def test_pagination():
    """GET /todos/?skip=1&limit=1 should return exactly 1 item."""
    response = client.get("/todos/?skip=0&limit=1")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    print("✅ Pagination works (limit=1 returned 1 item)")


def test_delete_todo(todo_id: int):
    """DELETE /todos/{id} should remove the item."""
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 404
    print(f"✅ Deleted to-do {todo_id} (verified with 404)")


def test_delete_nonexistent_todo():
    """DELETE /todos/9999 should return 404."""
    response = client.delete("/todos/9999")
    assert response.status_code == 404
    print("✅ 404 returned when deleting nonexistent item")


# ─── Run All Tests ───────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("To-Do API — Test Suite")
    print("=" * 50)
    print()

    # Create
    print("--- CREATE ---")
    todo_id = test_create_todo()
    quick_id = test_create_todo_minimal()
    test_create_todo_validation_error()
    print()

    # Read
    print("--- READ ---")
    test_list_todos()
    test_get_single_todo(todo_id)
    test_get_nonexistent_todo()
    print()

    # Update
    print("--- UPDATE ---")
    test_update_todo(todo_id)
    test_complete_todo(todo_id)
    test_filter_by_status()
    test_pagination()
    print()

    # Delete
    print("--- DELETE ---")
    test_delete_todo(quick_id)
    test_delete_nonexistent_todo()
    print()

    # Root
    print("--- ROOT ---")
    test_root_endpoint()
    print()

    print("=" * 50)
    print("All tests passed! ✅")
    print("=" * 50)
