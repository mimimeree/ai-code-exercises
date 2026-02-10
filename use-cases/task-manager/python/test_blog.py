"""
Test suite for the Blog API.

Tests CRUD for posts, comments, search, and background task notifications.
Run with: python test_blog.py
"""

from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)


# ─── POST CRUD ───────────────────────────────────────────────

def test_create_post():
    """POST /posts should create a new blog post."""
    response = client.post("/posts", json={
        "title": "Learning FastAPI",
        "content": "FastAPI is a modern Python web framework for building APIs.",
        "author": "Whitney",
        "tags": ["python", "fastapi", "tutorial"],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learning FastAPI"
    assert data["author"] == "Whitney"
    assert data["comment_count"] == 0
    assert "id" in data
    assert "created_at" in data
    print(f"✅ Created post (ID: {data['id']})")
    return data["id"]


def test_create_second_post():
    """Create a second post for search/filter testing."""
    response = client.post("/posts", json={
        "title": "Background Tasks Deep Dive",
        "content": "Background tasks run after the response is sent to the client.",
        "author": "Whitney",
        "tags": ["python", "fastapi", "advanced"],
    })
    assert response.status_code == 201
    print(f"✅ Created second post (ID: {response.json()['id']})")
    return response.json()["id"]


def test_create_third_post():
    """Create a third post by a different author."""
    response = client.post("/posts", json={
        "title": "JavaScript vs Python",
        "content": "Comparing two popular programming languages.",
        "author": "Alex",
        "tags": ["javascript", "python", "comparison"],
    })
    assert response.status_code == 201
    print(f"✅ Created third post by different author (ID: {response.json()['id']})")


def test_list_posts():
    """GET /posts should return all posts."""
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    print(f"✅ Listed {len(data)} posts")


def test_get_single_post(post_id: int):
    """GET /posts/{id} should return a specific post."""
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    assert response.json()["id"] == post_id
    print(f"✅ Retrieved post {post_id}")


def test_get_nonexistent_post():
    """GET /posts/9999 should return 404."""
    response = client.get("/posts/9999")
    assert response.status_code == 404
    print("✅ 404 for nonexistent post")


def test_update_post(post_id: int):
    """PUT /posts/{id} should update only specified fields."""
    response = client.put(f"/posts/{post_id}", json={
        "title": "Learning FastAPI (Updated!)",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Learning FastAPI (Updated!)"
    assert data["content"] == "FastAPI is a modern Python web framework for building APIs."
    print(f"✅ Updated post {post_id} (partial update)")


def test_filter_by_tag():
    """GET /posts?tag=advanced should filter by tag."""
    response = client.get("/posts?tag=advanced")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all("advanced" in [t.lower() for t in p["tags"]] for p in data)
    print(f"✅ Filtered by tag 'advanced': {len(data)} posts")


def test_filter_by_author():
    """GET /posts?author=Alex should filter by author."""
    response = client.get("/posts?author=Alex")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(p["author"] == "Alex" for p in data)
    print(f"✅ Filtered by author 'Alex': {len(data)} posts")


# ─── SEARCH ──────────────────────────────────────────────────

def test_search_posts():
    """GET /posts/search?q=fastapi should find matching posts."""
    response = client.get("/posts/search?q=fastapi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    print(f"✅ Search 'fastapi': {len(data)} results")


def test_search_no_results():
    """GET /posts/search?q=nonexistent should return empty list."""
    response = client.get("/posts/search?q=zzzznonexistentzzzz")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    print("✅ Search with no results: empty list")


def test_search_requires_query():
    """GET /posts/search without q parameter should return 422."""
    response = client.get("/posts/search")
    assert response.status_code == 422
    print("✅ Search without query: 422 validation error")


# ─── COMMENTS ────────────────────────────────────────────────

def test_create_comment(post_id: int):
    """POST /posts/{id}/comments should add a comment."""
    response = client.post(f"/posts/{post_id}/comments", json={
        "author": "Reader",
        "text": "Great article! Really helped me understand FastAPI.",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["author"] == "Reader"
    assert data["post_id"] == post_id
    print(f"✅ Added comment to post {post_id}")


def test_comment_updates_count(post_id: int):
    """Comment count should increment on the post."""
    response = client.get(f"/posts/{post_id}")
    data = response.json()
    assert data["comment_count"] >= 1
    print(f"✅ Post {post_id} comment count: {data['comment_count']}")


def test_list_comments(post_id: int):
    """GET /posts/{id}/comments should return comments for that post."""
    response = client.get(f"/posts/{post_id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(c["post_id"] == post_id for c in data)
    print(f"✅ Listed {len(data)} comments on post {post_id}")


def test_comment_on_nonexistent_post():
    """POST /posts/9999/comments should return 404."""
    response = client.post("/posts/9999/comments", json={
        "author": "Nobody", "text": "This should fail",
    })
    assert response.status_code == 404
    print("✅ 404 when commenting on nonexistent post")


# ─── BACKGROUND TASKS ────────────────────────────────────────

def test_notifications_logged():
    """GET /notifications should show background task activity."""
    # Give background tasks a moment to complete
    time.sleep(0.5)

    response = client.get("/notifications")
    assert response.status_code == 200
    data = response.json()
    assert data["total_notifications"] >= 1

    events = [n["event"] for n in data["notifications"]]
    assert "new_post" in events
    assert "new_comment" in events
    print(f"✅ Background tasks logged: {data['total_notifications']} notifications")

    for n in data["notifications"]:
        print(f"   → [{n['event']}] {n['message']}")


# ─── DELETE ──────────────────────────────────────────────────

def test_delete_post():
    """DELETE /posts/{id} should remove post and its comments."""
    # Create a post to delete
    create_resp = client.post("/posts", json={
        "title": "Temporary Post",
        "content": "This will be deleted.",
        "author": "Tester",
    })
    temp_id = create_resp.json()["id"]

    # Add a comment
    client.post(f"/posts/{temp_id}/comments", json={
        "author": "Commenter", "text": "Nice post!",
    })

    # Delete the post
    response = client.delete(f"/posts/{temp_id}")
    assert response.status_code == 204

    # Verify it's gone
    assert client.get(f"/posts/{temp_id}").status_code == 404
    print(f"✅ Deleted post {temp_id} and its comments")


# ─── ROOT ────────────────────────────────────────────────────

def test_root():
    """GET / should return API info with doc section references."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "documentation_sections_used" in data
    print("✅ Root endpoint shows documentation references")


# ─── RUN ALL ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("Blog API — Test Suite")
    print("=" * 55)
    print()

    print("--- POSTS (CRUD) ---")
    post_id = test_create_post()
    post2_id = test_create_second_post()
    test_create_third_post()
    test_list_posts()
    test_get_single_post(post_id)
    test_get_nonexistent_post()
    test_update_post(post_id)
    test_filter_by_tag()
    test_filter_by_author()
    print()

    print("--- SEARCH ---")
    test_search_posts()
    test_search_no_results()
    test_search_requires_query()
    print()

    print("--- COMMENTS ---")
    test_create_comment(post_id)
    test_comment_updates_count(post_id)
    test_list_comments(post_id)
    test_comment_on_nonexistent_post()
    print()

    print("--- BACKGROUND TASKS ---")
    test_notifications_logged()
    print()

    print("--- DELETE ---")
    test_delete_post()
    print()

    print("--- ROOT ---")
    test_root()
    print()

    print("=" * 55)
    print("All tests passed! ✅")
    print("=" * 55)
