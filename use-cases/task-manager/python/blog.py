"""
Blog API routes — CRUD for posts, comments, search, and background tasks.

This exercise demonstrates documentation navigation by implementing
features found across multiple FastAPI doc sections:

  - Tutorial > First Steps        → basic route structure
  - Tutorial > Path Parameters    → /posts/{post_id}
  - Tutorial > Query Parameters   → /posts/search?q=...
  - Tutorial > Request Body       → POST with Pydantic models
  - Tutorial > Body - Updates     → PUT with partial updates
  - Tutorial > Background Tasks   → notifications after create/comment
  - Tutorial > Handling Errors    → custom exceptions
  - Tutorial > Extra Models       → separate Create/Update/Response models
"""

from fastapi import APIRouter, Query, BackgroundTasks, HTTPException, status
from typing import List, Optional
from datetime import datetime

from ..models.blog import (
    PostCreate, PostUpdate, PostResponse,
    CommentCreate, CommentResponse,
)
from ..utils.background import (
    send_new_post_notification,
    send_new_comment_notification,
    log_search_query,
    get_notification_log,
)


router = APIRouter(tags=["blog"])

# ─── In-Memory Storage ───────────────────────────────────────
posts_db: dict[int, dict] = {}
comments_db: dict[int, dict] = {}
next_post_id: int = 1
next_comment_id: int = 1


# ═══════════════════════════════════════════════════════════════
# POSTS — CRUD Operations
# Docs section: Tutorial > Path Parameters, Request Body, Body - Updates
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog post",
)
async def create_post(post: PostCreate, background_tasks: BackgroundTasks):
    """
    Create a new blog post and notify subscribers in the background.

    **Background task in action:** After the response is sent, FastAPI
    runs send_new_post_notification() to simulate emailing subscribers.
    The client gets their response immediately — they never wait for
    the notification to be sent.

    Docs section: Tutorial > Background Tasks
    """
    global next_post_id

    new_post = {
        "id": next_post_id,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "tags": post.tags,
        "created_at": datetime.utcnow().isoformat(),
        "comment_count": 0,
    }
    posts_db[next_post_id] = new_post
    next_post_id += 1

    # Schedule notification to run AFTER response is sent
    background_tasks.add_task(send_new_post_notification, post.title, post.author)

    return new_post


@router.get(
    "/posts",
    response_model=List[PostResponse],
    summary="List all blog posts",
)
async def list_posts(
    tag: Optional[str] = Query(None, description="Filter posts by tag"),
    author: Optional[str] = Query(None, description="Filter posts by author"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    List posts with optional filtering by tag or author, plus pagination.

    Docs section: Tutorial > Query Parameters
    """
    items = list(posts_db.values())

    if tag:
        items = [p for p in items if tag.lower() in [t.lower() for t in p["tags"]]]
    if author:
        items = [p for p in items if p["author"].lower() == author.lower()]

    return items[skip : skip + limit]


@router.get(
    "/posts/search",
    response_model=List[PostResponse],
    summary="Search posts by keyword",
)
async def search_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    background_tasks: BackgroundTasks = None,
):
    """
    Search posts by keyword in title or content.

    **Background task in action:** The search results return immediately.
    The search query is logged for analytics in the background — the
    user never waits for the log write.

    Note: `q: str = Query(...)` — the `...` (Ellipsis) means this
    query parameter is REQUIRED. Without it, you get a 422 error.

    Docs section: Tutorial > Query Parameters, Background Tasks
    """
    query_lower = q.lower()
    results = [
        p for p in posts_db.values()
        if query_lower in p["title"].lower() or query_lower in p["content"].lower()
    ]

    # Log the search in the background
    if background_tasks:
        background_tasks.add_task(log_search_query, q, len(results))

    return results


@router.get(
    "/posts/{post_id}",
    response_model=PostResponse,
    summary="Get a specific blog post",
)
async def get_post(post_id: int):
    """
    Get a single post by ID.

    Docs section: Tutorial > Path Parameters
    """
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {post_id} not found"
        )
    return posts_db[post_id]


@router.put(
    "/posts/{post_id}",
    response_model=PostResponse,
    summary="Update a blog post",
)
async def update_post(post_id: int, updates: PostUpdate):
    """
    Update a post (partial updates supported).

    Uses model_dump(exclude_unset=True) to only apply fields the
    client actually sent — same pattern as Exercise 17's to-do API.

    Docs section: Tutorial > Body - Updates
    """
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        posts_db[post_id][field] = value

    return posts_db[post_id]


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a blog post",
)
async def delete_post(post_id: int):
    """Delete a post and its comments."""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    del posts_db[post_id]

    # Also delete associated comments
    comment_ids_to_delete = [
        cid for cid, c in comments_db.items() if c["post_id"] == post_id
    ]
    for cid in comment_ids_to_delete:
        del comments_db[cid]


# ═══════════════════════════════════════════════════════════════
# COMMENTS — Nested Resource
# Docs section: Tutorial > Bigger Applications, Path Parameters
# ═══════════════════════════════════════════════════════════════

@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a post",
)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    background_tasks: BackgroundTasks,
):
    """
    Add a comment to a blog post.

    **Background task in action:** After the comment is created and the
    response sent, a notification is sent to the post author in the
    background.

    This endpoint combines path parameters (post_id) with a request
    body (comment) — something covered in the "Body - Multiple Parameters"
    docs section.

    Docs section: Tutorial > Body - Multiple Parameters, Background Tasks
    """
    global next_comment_id

    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    new_comment = {
        "id": next_comment_id,
        "post_id": post_id,
        "author": comment.author,
        "text": comment.text,
        "created_at": datetime.utcnow().isoformat(),
    }
    comments_db[next_comment_id] = new_comment
    next_comment_id += 1

    # Update comment count on the post
    posts_db[post_id]["comment_count"] += 1

    # Notify post author in the background
    post_title = posts_db[post_id]["title"]
    background_tasks.add_task(send_new_comment_notification, post_title, comment.author)

    return new_comment


@router.get(
    "/posts/{post_id}/comments",
    response_model=List[CommentResponse],
    summary="List comments on a post",
)
async def list_comments(post_id: int):
    """Get all comments for a specific post."""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    return [c for c in comments_db.values() if c["post_id"] == post_id]


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS — Background Task Visibility
# (Not in a typical API — here for learning purposes)
# ═══════════════════════════════════════════════════════════════

@router.get(
    "/notifications",
    summary="View background task notification log",
)
async def view_notifications():
    """
    View the notification log to see background tasks that have run.

    This endpoint exists for learning purposes — it lets you SEE the
    results of background tasks. In a real app, notifications would go
    to an email service, message queue, or logging system.
    """
    log = get_notification_log()
    return {
        "total_notifications": len(log),
        "notifications": log,
    }
