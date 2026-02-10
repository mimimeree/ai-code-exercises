"""
Security utilities: password hashing and JWT token management.

Two security concepts at work here:

1. PASSWORD HASHING
   We never store actual passwords. We store a "hash" — a one-way
   scrambled version. When someone logs in, we hash what they typed
   and compare it to the stored hash. If they match, the password
   was correct. But even if someone steals the database, they can't
   reverse the hash to get the original password.

   This is the same concept from Exercise 11 where we identified
   storing plain text passwords as a critical security flaw in the
   Java UserManager code.

2. JWT TOKENS (JSON Web Tokens)
   After login, the server creates a signed "token" containing the
   username and an expiration time. The client sends this token with
   every future request instead of sending username/password each time.

   The token is SIGNED (not encrypted) — anyone can read it, but
   only the server can create valid ones. It's like a stamped ticket:
   you can see what's on it, but you can't forge the stamp.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..models.user import TokenData


# ─── Configuration ───────────────────────────────────────────
# In production, SECRET_KEY would come from an environment variable,
# NEVER hardcoded in source code. This is for learning only.
SECRET_KEY = "exercise-18-demo-secret-key-not-for-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ─── Password Hashing ───────────────────────────────────────
# bcrypt is the industry standard for password hashing.
# CryptContext handles the details: salting, hashing, and verification.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password for storage.

    Called during registration. The result looks like:
    $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW

    That jumble IS the hash. It includes a random "salt" that makes
    every hash different even for the same password, preventing
    attackers from using precomputed hash tables.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if a plain text password matches a stored hash.

    Called during login. Returns True if they match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ─── JWT Token Management ───────────────────────────────────

def create_access_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token containing the username and expiration time.

    The token contains (called "claims"):
    - "sub" (subject): the username
    - "exp" (expiration): when the token becomes invalid

    jwt.encode() signs this data with our SECRET_KEY. The resulting
    token is a long string like: eyJhbGciOi...

    Anyone can DECODE the token and read the claims (it's base64, not
    encrypted). But only someone with the SECRET_KEY can CREATE a valid
    token. If someone tampers with the claims, the signature won't match
    and jwt.decode() will reject it.
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))

    token_data = {
        "sub": username,   # "sub" is the standard JWT claim for "subject"
        "exp": expire,
    }

    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode a JWT token and extract the username.

    Returns TokenData if the token is valid, None if it's invalid
    (expired, tampered with, or malformed).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None
