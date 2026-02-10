"""
Blog API — Documentation Navigation Exercise.
Run with: uvicorn app.main:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from .routes import blog

app = FastAPI(
    title="Blog API",
    description=(
        "A blog API built by navigating FastAPI's documentation.\n\n"
        "**Features:** Posts (CRUD), Comments, Search, Background Tasks\n\n"
        "**Background tasks:** Creating posts and comments triggers "
        "notifications visible at GET /notifications"
    ),
    version="1.0.0",
)

app.include_router(blog.router)


@app.get("/", tags=["root"])
async def root():
    """API overview with documentation section references."""
    return {
        "message": "Blog API — Documentation Navigation Exercise",
        "docs": "/docs",
        "documentation_sections_used": {
            "First Steps": "Basic app setup",
            "Path Parameters": "GET /posts/{id}",
            "Query Parameters": "GET /posts?tag=... and GET /posts/search?q=...",
            "Request Body": "POST /posts with JSON body",
            "Body - Updates": "PUT /posts/{id} with partial updates",
            "Background Tasks": "Notifications after create/comment",
            "Handling Errors": "404 for missing posts",
            "Extra Models": "Separate Create/Update/Response models",
            "Bigger Applications": "Router-based project structure",
        },
    }
