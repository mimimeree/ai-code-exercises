"""
Pydantic models for authentication.

These models define the shape of data flowing through the auth system:
- What a user looks like (public vs internal)
- What a login token looks like
- What registration data looks like
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# ─── Token Models ────────────────────────────────────────────

class Token(BaseModel):
    """
    What the server sends back after a successful login.

    The client stores this token and includes it in the
    Authorization header of future requests:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Data extracted FROM a token when verifying it.

    When a protected endpoint receives a request, it decodes the
    JWT token and extracts the username. This model holds that data.
    """
    username: Optional[str] = None


# ─── User Models ─────────────────────────────────────────────

class UserCreate(BaseModel):
    """What a new user sends to register."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5)
    full_name: Optional[str] = Field(None, max_length=100)
    password: str = Field(..., min_length=6, description="At least 6 characters")


class UserResponse(BaseModel):
    """
    What the API sends back about a user (PUBLIC data only).

    Notice: NO password field. This model ensures we never
    accidentally leak the password hash in API responses.
    This is why we have separate models for different operations.
    """
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False


class UserInDB(UserResponse):
    """
    Internal user model that includes the hashed password.

    This extends UserResponse (inherits all its fields) and adds
    hashed_password. It's only used server-side, never sent to clients.

    Inheritance chain: UserInDB → UserResponse → BaseModel
    UserInDB has everything UserResponse has, PLUS hashed_password.
    """
    hashed_password: str
