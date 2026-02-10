"""
FastAPI JWT Authentication Demo — Main application.
Run with: uvicorn app.main:app --reload
Docs at:  http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from .routes import auth

app = FastAPI(
    title="FastAPI Auth Demo",
    description=(
        "JWT authentication example built for Exercise 18.\n\n"
        "**Flow:** Register → Login (get token) → Use token for protected endpoints\n\n"
        "Click the **Authorize** button above to log in with your token."
    ),
    version="1.0.0",
)

app.include_router(auth.router)


@app.get("/", tags=["root"])
async def root():
    """API root with usage instructions."""
    return {
        "message": "FastAPI Auth Demo",
        "usage": {
            "1_register": "POST /register with {username, email, password}",
            "2_login": "POST /token with username & password form data",
            "3_profile": "GET /users/me with Authorization: Bearer <token>",
        },
        "docs": "/docs",
    }
