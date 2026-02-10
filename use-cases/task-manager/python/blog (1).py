"""
Pydantic models for the blog API.

Models for posts, comments, and search — each with Create/Update/Response
variants following the pattern we established in Exercises 17-18.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Post Models ─────────────────────────────────────────────

class PostCreate(BaseModel):
    """What the client sends to create a new post."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    tags: List[str] = Field(default=[])


class PostUpdate(BaseModel):
    """Partial update — all fields optional."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None


class PostResponse(BaseModel):
    """What the server sends back about a post."""
    id: int
    title: str
    content: str
    author: str
    tags: List[str] = []
    created_at: str
    comment_count: int = 0


# ─── Comment Models ──────────────────────────────────────────

class CommentCreate(BaseModel):
    """What the client sends to add a comment."""
    author: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """What the server sends back about a comment."""
    id: int
    post_id: int
    author: str
    text: str
    created_at: str


# ─── Notification Model ─────────────────────────────────────

class NotificationLog(BaseModel):
    """Record of a background notification (for demonstrating background tasks)."""
    event: str
    message: str
    timestamp: str
