"""
API routes for to-do item CRUD operations.

CRUD = Create, Read, Update, Delete — the four basic operations for any data.
Each operation maps to an HTTP method:
  - Create → POST   (send data to create something new)
  - Read   → GET    (retrieve data)
  - Update → PUT    (replace/update existing data)
  - Delete → DELETE (remove data)

APIRouter groups related endpoints together. It's like a mini-app that
gets included in the main FastAPI app. This keeps the code organized —
if we had users too, they'd get their own router in routes/users.py.
"""

from fastapi import APIRouter, Query, status
from typing import List, Optional

from ..models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStatus
from ..utils.exceptions import TodoNotFoundError


# Create a router with a URL prefix and a tag for documentation grouping
# All routes in this file will start with /todos
router = APIRouter(prefix="/todos", tags=["todos"])

# ─── In-Memory Storage ───────────────────────────────────────
# In a real app, this would be a database. We're using a dictionary
# as a simple stand-in, just like we did with the Task Manager.
todo_database: dict[int, dict] = {}
next_id: int = 1


# ─── CREATE ──────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new to-do item"
)
async def create_todo(todo: TodoCreate):
    """
    Create a new to-do item.

    The client sends a JSON body matching TodoCreate (title required,
    description and due_date optional). The server assigns an ID and
    sets the initial status to "pending".

    **How FastAPI handles the request:**
    1. Client sends JSON → FastAPI parses it
    2. Pydantic validates it against TodoCreate model
    3. If invalid → automatic 422 error (we never see the bad data)
    4. If valid → this function receives a TodoCreate object

    The `todo: TodoCreate` parameter tells FastAPI: "parse the request
    body as a TodoCreate model." This is called dependency injection.
    """
    global next_id

    new_todo = {
        "id": next_id,
        "title": todo.title,
        "description": todo.description,
        "due_date": todo.due_date,
        "status": TodoStatus.PENDING,
    }

    todo_database[next_id] = new_todo
    next_id += 1

    return new_todo


# ─── READ (List) ─────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[TodoResponse],
    summary="List all to-do items"
)
async def list_todos(
    status_filter: Optional[TodoStatus] = Query(
        None,
        alias="status",
        description="Filter by status: 'pending' or 'completed'"
    ),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
):
    """
    List all to-do items with optional filtering and pagination.

    **Query parameters** (everything after ? in the URL):
    - `status` — filter by pending or completed
    - `skip` — for pagination (skip the first N items)
    - `limit` — max items to return (between 1 and 100)

    Example URLs:
    - `/todos/` — all items
    - `/todos/?status=pending` — only pending items
    - `/todos/?status=completed&limit=5` — first 5 completed items

    **Query() vs Path():**
    - Query parameters are optional filters: `/todos/?status=pending`
    - Path parameters are required identifiers: `/todos/42`

    **alias="status":** The parameter is named `status_filter` in Python
    (to avoid shadowing the `status` module) but appears as `status` in
    the URL. The `alias` parameter handles this mapping.
    """
    items = list(todo_database.values())

    # Filter by status if provided
    if status_filter is not None:
        items = [item for item in items if item["status"] == status_filter]

    # Apply pagination (same slice syntax as Python lists)
    return items[skip : skip + limit]


# ─── READ (Single Item) ─────────────────────────────────────

@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get a specific to-do item"
)
async def get_todo(todo_id: int):
    """
    Get a single to-do item by its ID.

    The `{todo_id}` in the path is a **path parameter**. FastAPI
    automatically extracts it from the URL and converts it to an int.

    If `/todos/42` is requested, `todo_id` will be the integer 42.
    If `/todos/abc` is requested, FastAPI returns a 422 error
    automatically because "abc" can't be converted to int.
    """
    if todo_id not in todo_database:
        raise TodoNotFoundError(todo_id)

    return todo_database[todo_id]


# ─── UPDATE ──────────────────────────────────────────────────

@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Update a to-do item"
)
async def update_todo(todo_id: int, updates: TodoUpdate):
    """
    Update an existing to-do item (partial updates supported).

    The client sends a JSON body with only the fields they want to change.
    Fields not included in the request body stay unchanged.

    **How partial updates work:**
    `updates.model_dump(exclude_unset=True)` returns a dict containing
    ONLY the fields the client actually sent. If they send
    `{"status": "completed"}`, the dict is just `{"status": "completed"}` —
    title, description, and due_date are untouched.

    This is the difference between TodoUpdate (all fields Optional) and
    TodoCreate (title is required). Different models for different operations.
    """
    if todo_id not in todo_database:
        raise TodoNotFoundError(todo_id)

    # Get only the fields the client actually sent
    update_data = updates.model_dump(exclude_unset=True)

    # Apply each update to the existing item
    existing_todo = todo_database[todo_id]
    for field, value in update_data.items():
        existing_todo[field] = value

    return existing_todo


# ─── UPDATE (Quick Complete) ─────────────────────────────────

@router.put(
    "/{todo_id}/complete",
    response_model=TodoResponse,
    summary="Mark a to-do item as completed"
)
async def complete_todo(todo_id: int):
    """
    Convenience endpoint to mark a to-do item as completed.

    Instead of sending `{"status": "completed"}` to the update endpoint,
    the client can just PUT to `/todos/42/complete`. This is a common
    API design pattern: provide shortcuts for frequent operations.
    """
    if todo_id not in todo_database:
        raise TodoNotFoundError(todo_id)

    todo_database[todo_id]["status"] = TodoStatus.COMPLETED
    return todo_database[todo_id]


# ─── DELETE ──────────────────────────────────────────────────

@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a to-do item"
)
async def delete_todo(todo_id: int):
    """
    Delete a to-do item permanently.

    Returns HTTP 204 (No Content) — meaning "success, but there's nothing
    to send back." This is the standard response for successful deletions.

    The function returns None (implicitly), and FastAPI sends an empty
    response body with status 204.
    """
    if todo_id not in todo_database:
        raise TodoNotFoundError(todo_id)

    del todo_database[todo_id]
