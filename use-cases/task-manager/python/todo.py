"""
Pydantic models for to-do items.

Pydantic models define the SHAPE of data — what fields exist, what types they
are, and what validation rules apply. FastAPI uses them to:
  1. Validate incoming request data automatically
  2. Generate API documentation
  3. Serialize response data to JSON

Think of them like Python dataclasses with built-in validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class TodoStatus(str, Enum):
    """
    Status options for a to-do item.

    Inheriting from both `str` and `Enum` means each value IS a string,
    so FastAPI can serialize it to JSON directly.
    Python equivalent: like TaskStatus from our Task Manager, but as strings.
    """
    PENDING = "pending"
    COMPLETED = "completed"


class TodoCreate(BaseModel):
    """
    Model for CREATING a new to-do item (what the client sends).

    This is the REQUEST body — it defines what data the client must provide.
    The `id`, `status`, and `created_at` are NOT here because the server
    generates those automatically.

    Field() adds validation rules:
      - `...` means "required" (no default value)
      - min_length, max_length constrain string length
      - description appears in the auto-generated API docs
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Title of the to-do item"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional detailed description"
    )
    due_date: Optional[date] = Field(
        None,
        description="Optional due date (format: YYYY-MM-DD)"
    )


class TodoUpdate(BaseModel):
    """
    Model for UPDATING an existing to-do item.

    All fields are Optional because the client might only want to update
    one field (e.g., just mark it completed without changing the title).
    """
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New title"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="New description"
    )
    due_date: Optional[date] = Field(
        None,
        description="New due date"
    )
    status: Optional[TodoStatus] = Field(
        None,
        description="New status (pending or completed)"
    )


class TodoResponse(BaseModel):
    """
    Model for RESPONDING with a to-do item (what the server sends back).

    This includes all fields the client sent PLUS server-generated fields
    like `id` and `status`. It defines the shape of the JSON response.

    Config.json_schema_extra provides an example that appears in the
    auto-generated documentation.
    """
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: TodoStatus = TodoStatus.PENDING

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Complete FastAPI exercise",
                "description": "Build a to-do API with CRUD operations",
                "due_date": "2026-02-15",
                "status": "pending"
            }
        }
