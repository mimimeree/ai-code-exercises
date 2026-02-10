"""
Main FastAPI application — the entry point.

This file creates the FastAPI app instance, includes route modules,
and configures exception handlers. It's the equivalent of Flask's
`app = Flask(__name__)` that we saw in Exercise 5.

Run with: uvicorn app.main:app --reload
Then visit: http://127.0.0.1:8000/docs for interactive documentation
"""

from fastapi import FastAPI
from .routes import todos
from .utils.exceptions import add_exception_handlers


# ─── Create the FastAPI Application ──────────────────────────
# These metadata fields appear in the auto-generated /docs page
app = FastAPI(
    title="To-Do List API",
    description=(
        "A simple to-do list API built with FastAPI.\n\n"
        "Features:\n"
        "- Create, read, update, and delete to-do items\n"
        "- Filter by status (pending/completed)\n"
        "- Pagination support\n"
        "- Automatic input validation\n"
        "- Interactive documentation at /docs"
    ),
    version="1.0.0",
)


# ─── Include Route Modules ───────────────────────────────────
# app.include_router() is how you add a group of related endpoints.
# The router from todos.py brings all /todos/* endpoints into the app.
app.include_router(todos.router)


# ─── Register Exception Handlers ─────────────────────────────
add_exception_handlers(app)


# ─── Root Endpoint ───────────────────────────────────────────
@app.get("/", tags=["root"])
async def root():
    """
    API root — returns basic info and links to documentation.
    """
    return {
        "message": "Welcome to the To-Do List API",
        "docs": "/docs",
        "endpoints": {
            "list_todos": "GET /todos/",
            "create_todo": "POST /todos/",
            "get_todo": "GET /todos/{id}",
            "update_todo": "PUT /todos/{id}",
            "complete_todo": "PUT /todos/{id}/complete",
            "delete_todo": "DELETE /todos/{id}",
        }
    }
